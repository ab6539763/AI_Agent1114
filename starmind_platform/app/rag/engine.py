"""
企业级混合检索 RAG（Retrieval-Augmented Generation）引擎模块。

全链路核心组件：
1. `DocumentLoader`：支持 txt / md / csv / json 多格式文档与原始文本加载。
2. `RecursiveCharacterTextSplitter`：中文标点优先递归切片器（`\n\n` -> `\n` -> `。` -> `！` -> `？` -> `；`），
   支持 `chunk_size` 与 `chunk_overlap`，避免语义在句中断裂。
3. `LightweightSemanticEmbedder`：零重型依赖的轻量本地语义向量器（中文字符 1/2/3-gram + 英文词袋特征哈希 + L2 归一化），
   在纯 CPU 环境下毫秒级完成高维向量化与真实余弦相似度计算。
4. `LocalVectorStore`：支持 JSON 磁盘持久化与元数据精确过滤的向量存储引擎。
5. `BM25Retriever`：经典 Okapi BM25 词频逆文档频率检索器，擅长专有名词、制度编号与精确术语匹配。
6. `HybridRetriever`：融合 BM25 与向量检索两路召回，采用 RRF（Reciprocal Rank Fusion）倒数排名融合算法。
7. `Reranker`：基于查询词覆盖率、连续短语命中与词序紧密度的交叉重排序器。
8. `QueryRewriter`：中文口语查询改写与多路同义扩展，提升召回率。
9. `RAGPipeline`：端到端企业知识库入库与问答管线，强制标注 `[文档名#片段ID]` 引用来源，
   低置信度时严格触发“知识库暂无相关依据，我不知道”防幻觉兜底。
10. `RagasEvaluator`：无外网依赖的自动化 RAG 评估器，计算忠实度（Faithfulness）、
    答案相关性（Answer Relevancy）与上下文召回率（Context Recall）。
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from starmind_platform.app.core.exceptions import RAGRetrievalError
from starmind_platform.app.core.logging_utils import get_logger
from starmind_platform.app.core.observability import get_observability
from starmind_platform.app.llm.client import BaseLLM, create_llm_client

logger = get_logger("starmind.rag")

# 中英文基础分词正则：匹配连续英文数字词或单个中文汉字
_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]")
_CN_STOPWORDS = frozenset(
    {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
        "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
        "自己", "这", "那", "吗", "呢", "啊", "吧", "请问", "什么", "怎么", "如何",
    }
)


def tokenize_zh_en(text: str) -> List[str]:
    """
    中英文混合轻量分词：
    - 英文/数字统一转小写按词切分；
    - 中文保留单字并补充相邻二字词（Bigram），兼顾字面召回与中文语义词组匹配。
    """
    if not text:
        return []
    raw_tokens = [t.lower() for t in _TOKEN_RE.findall(text)]
    tokens: List[str] = [t for t in raw_tokens if t not in _CN_STOPWORDS]

    # 补充中文双字词特征（如“差旅”“报销”“年假”“审批”）
    cjk_runs = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    for run in cjk_runs:
        for i in range(len(run) - 1):
            bg = run[i : i + 2]
            if bg not in _CN_STOPWORDS:
                tokens.append(bg)
    return tokens


@dataclass
class DocumentChunk:
    """切分后的知识库文档片段。"""

    chunk_id: str
    doc_name: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)

    @property
    def citation_tag(self) -> str:
        """标准企业溯源引用标签：`[文档名#片段ID]`。"""
        return f"[{self.doc_name}#{self.chunk_id}]"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentChunk":
        return cls(
            chunk_id=str(data["chunk_id"]),
            doc_name=str(data["doc_name"]),
            content=str(data["content"]),
            metadata=dict(data.get("metadata") or {}),
            embedding=[float(x) for x in data.get("embedding") or []],
        )


@dataclass
class RetrievedChunk:
    """检索与重排序后的候选片段（附带多路得分）。"""

    chunk: DocumentChunk
    vector_score: float = 0.0
    bm25_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.chunk_id,
            "doc_name": self.chunk.doc_name,
            "citation": self.chunk.citation_tag,
            "content": self.chunk.content,
            "metadata": self.chunk.metadata,
            "vector_score": round(self.vector_score, 4),
            "bm25_score": round(self.bm25_score, 4),
            "rrf_score": round(self.rrf_score, 4),
            "rerank_score": round(self.rerank_score, 4),
        }


class DocumentLoader:
    """多格式企业文档加载器（支持 txt / md / csv / json）。"""

    SUPPORTED_FORMATS = {"txt", "md", "markdown", "csv", "json"}

    @classmethod
    def load_text(cls, content: str, doc_format: str = "txt") -> str:
        """将原始文本按指定格式规范化为可切分的纯文本字符串。"""
        fmt = doc_format.lower().lstrip(".")
        if fmt not in cls.SUPPORTED_FORMATS:
            raise RAGRetrievalError(
                f"不支持的文档格式: {doc_format}，当前支持 {sorted(cls.SUPPORTED_FORMATS)}"
            )

        if fmt in {"txt", "md", "markdown"}:
            return content.strip()

        if fmt == "csv":
            reader = csv.DictReader(io.StringIO(content.strip()))
            lines: List[str] = []
            for idx, row in enumerate(reader, start=1):
                pairs = [f"{k}: {v}" for k, v in row.items() if k is not None and v is not None]
                lines.append(f"记录{idx} | " + "；".join(pairs))
            return "\n".join(lines)

        if fmt == "json":
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError as exc:
                raise RAGRetrievalError(f"JSON 文档解析失败: {exc}") from exc

            if isinstance(parsed, list):
                return "\n".join(
                    json.dumps(item, ensure_ascii=False) if isinstance(item, (dict, list)) else str(item)
                    for item in parsed
                )
            if isinstance(parsed, dict):
                return "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in parsed.items())
            return str(parsed)

        return content.strip()

    @classmethod
    def load_file(cls, file_path: str | Path) -> Tuple[str, str]:
        """从本地文件读取内容并自动识别格式，返回 `(文件名, 规范化文本)`。"""
        path = Path(file_path)
        if not path.exists():
            raise RAGRetrievalError(f"文档路径不存在: {path}")
        raw = path.read_text(encoding="utf-8")
        ext = path.suffix.lstrip(".") or "txt"
        return path.name, cls.load_text(raw, ext)


class RecursiveCharacterTextSplitter:
    """
    中文标点优先递归文本切片器。
    按段落 -> 换行 -> 中文句号/感叹号/问号 -> 分号 -> 逗号 -> 空格顺序切分，
    并在相邻片段间保留 `chunk_overlap` 个字符的重叠上下文。
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]

    def __init__(
        self,
        chunk_size: int = 320,
        chunk_overlap: int = 60,
        separators: Optional[Sequence[str]] = None,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须小于 chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = list(separators or self.DEFAULT_SEPARATORS)

    def _split_recursive(self, text: str, sep_idx: int) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        if sep_idx >= len(self.separators) - 1:
            # 兜底硬切分
            step = max(1, self.chunk_size - self.chunk_overlap)
            return [text[i : i + self.chunk_size] for i in range(0, len(text), step)]

        sep = self.separators[sep_idx]
        if sep and sep in text:
            parts = text.split(sep)
            merged: List[str] = []
            buffer = ""
            for i, part in enumerate(parts):
                piece = part + (sep if i < len(parts) - 1 and sep not in {"\n\n", "\n", " "} else "")
                if not piece.strip():
                    continue
                if len(buffer) + len(piece) + (1 if buffer else 0) <= self.chunk_size:
                    joiner = sep if sep in {"\n\n", "\n", " "} and buffer else ""
                    buffer = f"{buffer}{joiner}{piece}" if buffer else piece
                else:
                    if buffer:
                        merged.append(buffer)
                    if len(piece) > self.chunk_size:
                        merged.extend(self._split_recursive(piece, sep_idx + 1))
                        buffer = ""
                    else:
                        buffer = piece
            if buffer:
                merged.append(buffer)
            return merged

        return self._split_recursive(text, sep_idx + 1)

    def split_text(self, text: str) -> List[str]:
        """将长文档切分为带有重叠窗口的语义片段列表。"""
        cleaned = text.strip()
        if not cleaned:
            return []

        raw_chunks = self._split_recursive(cleaned, 0)
        if self.chunk_overlap <= 0 or len(raw_chunks) <= 1:
            return [c.strip() for c in raw_chunks if c.strip()]

        overlapped: List[str] = [raw_chunks[0].strip()]
        for prev, curr in zip(raw_chunks, raw_chunks[1:]):
            prefix = prev[-self.chunk_overlap :].strip()
            combined = f"{prefix}{curr}".strip() if prefix and not curr.startswith(prefix) else curr.strip()
            overlapped.append(combined)
        return [c for c in overlapped if c]


class LightweightSemanticEmbedder:
    """
    轻量本地语义向量器（零重型深度学习依赖，毫秒级运行）。
    原理：提取中英文字符 N-gram（1/2/3-gram）与分词词袋特征，通过确定性 BLAKE2b 特征哈希
    映射到固定高维稀疏空间（默认 256 维），采用带符号哈希降低碰撞误差并做 L2 单位化。
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _extract_features(self, text: str) -> Counter[str]:
        feats: Counter[str] = Counter()
        tokens = tokenize_zh_en(text)
        for tok in tokens:
            # 词级特征给予更高权重
            feats[f"w:{tok}"] += 2
        compact = re.sub(r"\s+", "", text.lower())
        for n in (2, 3):
            for i in range(max(0, len(compact) - n + 1)):
                feats[f"g{n}:{compact[i:i+n]}"] += 1
        return feats

    def embed(self, text: str) -> List[float]:
        """将文本编码为长度为 `self.dim` 的 L2 归一化浮点向量。"""
        vec = [0.0] * self.dim
        feats = self._extract_features(text)
        if not feats:
            return vec

        for feat, count in feats.items():
            digest = hashlib.blake2b(feat.encode("utf-8"), digest_size=8).digest()
            val = int.from_bytes(digest[:4], "little")
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            idx = val % self.dim
            vec[idx] += sign * (1.0 + math.log(count))

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 1e-12:
            vec = [round(x / norm, 6) for x in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
        """计算两个已归一化向量的余弦相似度（范围 [-1, 1]，非负特征下常见 [0, 1]）。"""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, float(dot)))


class LocalVectorStore:
    """支持 JSON 持久化与元数据过滤的轻量级本地向量存储。"""

    def __init__(self, persist_path: Optional[str | Path] = None) -> None:
        self.persist_path = Path(persist_path) if persist_path else None
        self.chunks: List[DocumentChunk] = []
        if self.persist_path and self.persist_path.exists():
            self.load()

    def add_chunks(self, new_chunks: Sequence[DocumentChunk], *, save_to_disk: bool = True) -> int:
        existing_ids = {c.chunk_id for c in self.chunks}
        added = 0
        for chunk in new_chunks:
            if chunk.chunk_id in existing_ids:
                # 覆盖更新同 ID 片段
                self.chunks = [c for c in self.chunks if c.chunk_id != chunk.chunk_id]
            self.chunks.append(chunk)
            existing_ids.add(chunk.chunk_id)
            added += 1
        if save_to_disk and self.persist_path:
            self.save()
        return added

    def filter_chunks(self, metadata_filter: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        if not metadata_filter:
            return list(self.chunks)
        matched: List[DocumentChunk] = []
        for chunk in self.chunks:
            if all(chunk.metadata.get(k) == v for k, v in metadata_filter.items()):
                matched.append(chunk)
        return matched

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = 8,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        candidates = self.filter_chunks(metadata_filter)
        scored = [
            (chunk, LightweightSemanticEmbedder.cosine_similarity(query_vector, chunk.embedding))
            for chunk in candidates
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def save(self) -> None:
        if not self.persist_path:
            return
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [c.to_dict() for c in self.chunks]
        self.persist_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load(self) -> None:
        if not self.persist_path or not self.persist_path.exists():
            return
        try:
            raw = json.loads(self.persist_path.read_text(encoding="utf-8"))
            self.chunks = [DocumentChunk.from_dict(item) for item in raw]
        except Exception as exc:
            logger.warning(f"加载本地向量库失败，将使用空索引: {exc}")
            self.chunks = []

    def clear(self) -> None:
        self.chunks.clear()
        if self.persist_path and self.persist_path.exists():
            self.persist_path.unlink()


class BM25Retriever:
    """Okapi BM25 关键词检索器（擅长制度编号、产品名与精确业务术语召回）。"""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b

    def search(
        self,
        query: str,
        chunks: Sequence[DocumentChunk],
        top_k: int = 8,
    ) -> List[Tuple[DocumentChunk, float]]:
        if not chunks:
            return []

        q_tokens = tokenize_zh_en(query)
        if not q_tokens:
            return []

        doc_tokens_list = [tokenize_zh_en(c.content) for c in chunks]
        doc_lens = [len(toks) for toks in doc_tokens_list]
        avg_dl = sum(doc_lens) / len(doc_lens) if doc_lens else 1.0
        n_docs = len(chunks)

        # 计算包含每个词项的文档频率 DF
        df: Counter[str] = Counter()
        for toks in doc_tokens_list:
            for t in set(toks):
                df[t] += 1

        results: List[Tuple[DocumentChunk, float]] = []
        for chunk, toks, dl in zip(chunks, doc_tokens_list, doc_lens):
            tf = Counter(toks)
            score = 0.0
            for qt in q_tokens:
                freq = tf.get(qt, 0)
                if freq == 0:
                    continue
                idf = math.log((n_docs - df[qt] + 0.5) / (df[qt] + 0.5) + 1.0)
                denom = freq + self.k1 * (1.0 - self.b + self.b * (dl / max(avg_dl, 1.0)))
                score += idf * ((freq * (self.k1 + 1.0)) / max(denom, 1e-9))
            if score > 0:
                results.append((chunk, score))

        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]


class QueryRewriter:
    """企业查询改写器：针对中文口语提问进行同义词扩展与多路查询生成。"""

    SYNONYM_MAP: Dict[str, List[str]] = {
        "报销": ["差旅费用", "财务报销标准", "发票核销"],
        "年假": ["休假制度", "带薪年休假", "请假流程"],
        "加班": ["调休", "加班补贴", "考勤制度"],
        "上线": ["发布规范", "灰度发布", "生产变更"],
        "安全": ["数据合规", "脱敏规范", "权限管控"],
        "微调": ["LoRA", "LLaMA-Factory", "模型训练"],
    }

    def rewrite(self, query: str) -> List[str]:
        """返回包含原始查询及最多 2 条扩展查询的列表。"""
        clean_q = query.strip()
        queries = [clean_q]
        for key, synonyms in self.SYNONYM_MAP.items():
            if key in clean_q:
                queries.append(f"{clean_q} {' '.join(synonyms[:2])}")
                break
        # 去除疑问语气词生成关键词压缩查询
        compact = re.sub(r"[？?吗呢啊吧请问一下告诉我怎么如何]", " ", clean_q).strip()
        if compact and compact != clean_q:
            queries.append(compact)
        return list(dict.fromkeys(queries))[:3]


class HybridRetriever:
    """
    混合检索器：融合向量语义检索 + BM25 关键词检索，使用 RRF（倒数排名融合）汇总排序。
    RRF 公式：`score(d) = sum(1 / (k + rank_i(d)))`，默认 `k = 60`。
    """

    def __init__(
        self,
        vector_store: LocalVectorStore,
        embedder: LightweightSemanticEmbedder,
        bm25: Optional[BM25Retriever] = None,
        rrf_k: int = 60,
    ) -> None:
        self.vector_store = vector_store
        self.embedder = embedder
        self.bm25 = bm25 or BM25Retriever()
        self.rrf_k = rrf_k

    def retrieve(
        self,
        queries: Sequence[str],
        top_k: int = 8,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievedChunk]:
        candidates = self.vector_store.filter_chunks(metadata_filter)
        if not candidates:
            return []

        merged: Dict[str, RetrievedChunk] = {}

        for q in queries:
            q_vec = self.embedder.embed(q)
            vec_hits = self.vector_store.search(q_vec, top_k=max(top_k * 2, 10), metadata_filter=metadata_filter)
            bm25_hits = self.bm25.search(q, candidates, top_k=max(top_k * 2, 10))

            for rank, (chunk, score) in enumerate(vec_hits, start=1):
                item = merged.setdefault(chunk.chunk_id, RetrievedChunk(chunk=chunk))
                item.vector_score = max(item.vector_score, score)
                if score > 0.05:
                    item.rrf_score += 1.0 / (self.rrf_k + rank)

            for rank, (chunk, score) in enumerate(bm25_hits, start=1):
                item = merged.setdefault(chunk.chunk_id, RetrievedChunk(chunk=chunk))
                item.bm25_score = max(item.bm25_score, score)
                if score > 0:
                    item.rrf_score += 1.2 / (self.rrf_k + rank)

        ranked = sorted(merged.values(), key=lambda x: x.rrf_score, reverse=True)
        return ranked[:top_k]


class Reranker:
    """
    轻量交叉重排序器（Cross-Feature Reranker）。
    综合查询词覆盖率（Coverage）、短语连续匹配度（Proximity）与原始向量相似度计算最终置信度 [0, 1]。
    """

    def rerank(self, query: str, candidates: Sequence[RetrievedChunk], top_k: int = 4) -> List[RetrievedChunk]:
        if not candidates:
            return []

        q_tokens = list(dict.fromkeys(tokenize_zh_en(query)))
        q_clean = re.sub(r"\s+", "", query.lower())

        for item in candidates:
            doc_text = item.chunk.content
            doc_lower = re.sub(r"\s+", "", doc_text.lower())
            doc_tokens = set(tokenize_zh_en(doc_text))

            # 1. 查询词覆盖率
            coverage = (
                sum(1 for t in q_tokens if t in doc_tokens) / max(len(q_tokens), 1)
                if q_tokens
                else 0.0
            )

            # 2. 连续 2~4 字核心短语命中加分
            phrase_hits = 0
            phrase_total = 0
            for n in (2, 3, 4):
                if len(q_clean) >= n:
                    for i in range(0, min(len(q_clean) - n + 1, 12)):
                        sub = q_clean[i : i + n]
                        phrase_total += 1
                        if sub in doc_lower:
                            phrase_hits += 1
            proximity = phrase_hits / max(phrase_total, 1)

            # 3. 归一化 BM25 贡献
            bm25_norm = 1.0 - math.exp(-item.bm25_score / 4.0) if item.bm25_score > 0 else 0.0

            # 加权综合置信度分数 [0, 1]
            score = 0.42 * coverage + 0.25 * proximity + 0.20 * bm25_norm + 0.13 * item.vector_score
            item.rerank_score = round(min(1.0, max(0.0, score)), 4)

        reranked = sorted(candidates, key=lambda x: x.rerank_score, reverse=True)
        return reranked[:top_k]


class RagasEvaluator:
    """
    自动化 RAG 质量评估器（对标 Ragas 核心三维指标）：
    1. `faithfulness`（忠实度）：回答中的核心信息有多少能在检索上下文中找到直接支撑，防止大模型幻觉。
    2. `answer_relevancy`（答案相关性）：回答是否紧扣用户原始提问。
    3. `context_recall`（上下文召回率）：若提供参考标准答案 `ground_truth`，计算上下文对其关键点的覆盖比例。
    """

    @staticmethod
    def _overlap_ratio(source_tokens: Sequence[str], target_tokens: Sequence[str]) -> float:
        src = set(source_tokens)
        tgt = set(target_tokens)
        if not src:
            return 0.0
        return round(len(src & tgt) / len(src), 4)

    def evaluate(
        self,
        *,
        question: str,
        answer: str,
        contexts: Sequence[str],
        ground_truth: Optional[str] = None,
    ) -> Dict[str, Any]:
        joined_ctx = "\n".join(contexts)
        q_toks = tokenize_zh_en(question)
        a_toks = tokenize_zh_en(answer)
        ctx_toks = tokenize_zh_en(joined_ctx)

        # 忠实度：回答词项在上下文中的支撑比例（若触发诚实拒答，忠实度为 1.0）
        if "知识库暂无相关依据" in answer:
            faithfulness = 1.0
        else:
            faithfulness = self._overlap_ratio(a_toks, ctx_toks)

        # 答案相关性：问题关键词在回答中的覆盖率与长度合理性加权
        q_cov = self._overlap_ratio(q_toks, a_toks)
        answer_relevancy = round(min(1.0, q_cov * 0.75 + (0.25 if len(answer) >= 20 else 0.1)), 4)

        # 上下文召回率：以 ground_truth（若无则以 question）作为参照计算上下文覆盖度
        ref_toks = tokenize_zh_en(ground_truth) if ground_truth else q_toks
        context_recall = self._overlap_ratio(ref_toks, ctx_toks)

        overall = round((faithfulness + answer_relevancy + context_recall) / 3.0, 4)
        return {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_recall": context_recall,
            "overall_score": overall,
            "verdict": "优秀" if overall >= 0.75 else ("良好" if overall >= 0.5 else "待优化"),
        }


class RAGPipeline:
    """星辰智脑企业级端到端 RAG 知识库管线。"""

    FALLBACK_ANSWER = "知识库暂无相关依据，我不知道。建议补充相关制度或技术文档后重新检索。"

    def __init__(
        self,
        *,
        llm: Optional[BaseLLM] = None,
        persist_path: Optional[str | Path] = None,
        chunk_size: int = 320,
        chunk_overlap: int = 60,
        min_confidence: float = 0.12,
    ) -> None:
        self.llm = llm or create_llm_client()
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.embedder = LightweightSemanticEmbedder(dim=256)
        self.vector_store = LocalVectorStore(persist_path=persist_path)
        self.retriever = HybridRetriever(self.vector_store, self.embedder)
        self.reranker = Reranker()
        self.rewriter = QueryRewriter()
        self.evaluator = RagasEvaluator()
        self.min_confidence = min_confidence

    def ingest_document(
        self,
        *,
        doc_name: str,
        content: str,
        doc_format: str = "txt",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """将单个文档解析、切分、向量化并写入本地向量库。"""
        start = time.perf_counter()
        normalized_text = DocumentLoader.load_text(content, doc_format)
        pieces = self.splitter.split_text(normalized_text)
        if not pieces:
            raise RAGRetrievalError(f"文档 {doc_name} 解析后内容为空，无法入库。")

        base_meta = dict(metadata or {})
        base_meta["doc_format"] = doc_format
        doc_hash = hashlib.md5(doc_name.encode("utf-8")).hexdigest()[:6]

        chunks: List[DocumentChunk] = []
        for idx, piece in enumerate(pieces, start=1):
            chunk_id = f"{doc_hash}-c{idx}"
            meta = dict(base_meta)
            meta["chunk_index"] = idx
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    doc_name=doc_name,
                    content=piece,
                    metadata=meta,
                    embedding=self.embedder.embed(piece),
                )
            )

        added = self.vector_store.add_chunks(chunks)
        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
        get_observability().record_span(
            name="rag.ingest",
            category="rag",
            latency_ms=elapsed_ms,
            metadata={"doc_name": doc_name, "chunks": added},
        )
        return {
            "doc_name": doc_name,
            "chunks_added": added,
            "total_chunks_in_kb": len(self.vector_store.chunks),
            "latency_ms": elapsed_ms,
        }

    def query(
        self,
        question: str,
        *,
        top_k: int = 4,
        metadata_filter: Optional[Dict[str, Any]] = None,
        use_query_rewrite: bool = True,
    ) -> Dict[str, Any]:
        """执行“查询改写 -> 混合检索(BM25+向量+RRF) -> 重排序 -> 置信度门控 -> 溯源生成”全流程。"""
        start = time.perf_counter()
        rewritten_queries = self.rewriter.rewrite(question) if use_query_rewrite else [question]
        candidates = self.retriever.retrieve(rewritten_queries, top_k=max(top_k * 2, 8), metadata_filter=metadata_filter)
        reranked = self.reranker.rerank(question, candidates, top_k=top_k)

        # 低置信度防幻觉兜底门控
        top_score = reranked[0].rerank_score if reranked else 0.0
        if not reranked or top_score < self.min_confidence:
            elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
            get_observability().record_span(
                name="rag.query.fallback",
                category="rag",
                latency_ms=elapsed_ms,
                metadata={"top_score": top_score},
            )
            return {
                "question": question,
                "answer": self.FALLBACK_ANSWER,
                "confidence": top_score,
                "fallback_triggered": True,
                "rewritten_queries": rewritten_queries,
                "citations": [],
                "sources": [r.to_dict() for r in reranked],
                "latency_ms": elapsed_ms,
            }

        context_lines = [
            f"{item.chunk.citation_tag} {item.chunk.content}" for item in reranked
        ]
        prompt = (
            "请严格基于以下企业知识库参考资料回答用户问题，并在关键结论后附上对应的引用标签（如 [文档名#片段ID]）。\n"
            "如果参考资料不足以回答，请直接说明“知识库暂无相关依据，我不知道”。\n\n"
            "--- 参考资料 ---\n"
            + "\n".join(context_lines)
            + f"\n\n--- 用户问题 ---\n{question}"
        )

        llm_resp = self.llm.chat(
            [
                {"role": "system", "content": "RAG_ANSWER_MODE: 你是杭州星辰数科企业知识库严谨问答助手。"},
                {"role": "user", "content": prompt},
            ]
        )

        citations = [item.chunk.citation_tag for item in reranked]
        answer = llm_resp.content
        # 保障回答末尾必然携带标准引用标注
        if not any(tag in answer for tag in citations):
            answer = f"{answer}\n\n引用来源：{'、'.join(citations[:2])}"

        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
        get_observability().record_span(
            name="rag.query",
            category="rag",
            latency_ms=elapsed_ms,
            metadata={"top_score": top_score, "hits": len(reranked)},
        )

        return {
            "question": question,
            "answer": answer,
            "confidence": top_score,
            "fallback_triggered": False,
            "rewritten_queries": rewritten_queries,
            "citations": citations,
            "sources": [r.to_dict() for r in reranked],
            "latency_ms": elapsed_ms,
        }

    def evaluate_query(self, question: str, ground_truth: Optional[str] = None, top_k: int = 4) -> Dict[str, Any]:
        """执行一次 RAG 问答并立即输出 Ragas 三维自动化评估报告。"""
        result = self.query(question, top_k=top_k)
        contexts = [src["content"] for src in result["sources"]]
        scores = self.evaluator.evaluate(
            question=question,
            answer=result["answer"],
            contexts=contexts,
            ground_truth=ground_truth,
        )
        return {
            "question": question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "citations": result["citations"],
            "metrics": scores,
        }
