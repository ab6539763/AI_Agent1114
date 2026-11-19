"""
Day 33 - 步骤一：BM25 稀疏检索 + Dense 向量检索 + RRF 倒数排名融合
对应生产栈：rank_bm25 / Elasticsearch BM25 + Milvus/Qdrant + EnsembleRetriever(RRF)
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple


@dataclass
class Document:
    """统一文档切片模型（与 LangChain Document 接口对齐）。"""

    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def doc_id(self) -> str:
        if "doc_id" in self.metadata:
            return str(self.metadata["doc_id"])
        return hashlib.md5(self.page_content.encode("utf-8")).hexdigest()[:12]


def tokenize_mixed_cn_en(text: str) -> List[str]:
    """
    中英混合 + 错误码友好分词器：
    1. 完整提取英文词、错误码与编号（如 ERR-5042、STARMIND-033、VPN、OA）；
    2. 对中文连续片段同时提取单字与二元字（Bigram），兼顾召回与词组精度。
    """
    lowered = text.lower()
    tokens: List[str] = []

    # 提取英文/数字/连字符组合（完整保留错误码与工单号）
    alnum_tokens = re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", lowered)
    tokens.extend(alnum_tokens)

    # 提取中文连续串并生成单字 + 二元词组
    cn_chunks = re.findall(r"[\u4e00-\u9fff]+", lowered)
    for chunk in cn_chunks:
        for ch in chunk:
            tokens.append(ch)
        for i in range(len(chunk) - 1):
            tokens.append(chunk[i : i + 2])
    return tokens


class BM25Index:
    """
    标准 Okapi BM25 稀疏检索引擎：
    score(q, d) = sum_{t in q} IDF(t) * (f(t,d) * (k1 + 1)) / (f(t,d) + k1 * (1 - b + b * |d| / avgdl))
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.documents: List[Document] = []
        self.doc_term_freqs: List[Counter[str]] = []
        self.doc_lengths: List[int] = []
        self.df: Counter[str] = Counter()
        self.avgdl: float = 0.0

    def add_documents(self, docs: Sequence[Document]) -> None:
        for doc in docs:
            tokens = tokenize_mixed_cn_en(doc.page_content)
            tf = Counter(tokens)
            self.documents.append(doc)
            self.doc_term_freqs.append(tf)
            self.doc_lengths.append(len(tokens))
            for term in tf.keys():
                self.df[term] += 1
        total_len = sum(self.doc_lengths)
        self.avgdl = total_len / max(1, len(self.documents))

    def _idf(self, term: str) -> float:
        n = len(self.documents)
        df = self.df.get(term, 0)
        return math.log(1.0 + (n - df + 0.5) / (df + 0.5))

    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        q_tokens = tokenize_mixed_cn_en(query)
        if not q_tokens or not self.documents:
            return []

        scored: List[Tuple[Document, float]] = []
        for idx, doc in enumerate(self.documents):
            tf_map = self.doc_term_freqs[idx]
            dl = self.doc_lengths[idx]
            score = 0.0
            for term in q_tokens:
                freq = tf_map.get(term, 0)
                if freq == 0:
                    continue
                idf = self._idf(term)
                denom = freq + self.k1 * (1.0 - self.b + self.b * dl / max(1e-9, self.avgdl))
                score += idf * (freq * (self.k1 + 1.0)) / denom
            if score > 0:
                scored.append((doc, round(score, 4)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]


class DenseVectorIndex:
    """
    轻量确定性语义向量索引（离线模拟 bge-m3 语义检索能力）：
    内置企业领域同义词语义桶 + 特征哈希投影，支持余弦相似度检索。
    """

    SEMANTIC_GROUPS: Dict[str, Tuple[str, ...]] = {
        "travel_hotel": ("出差", "差旅", "酒店", "住宿", "住店", "魔都", "上海", "北京", "一线城市", "报销", "上限"),
        "gateway_timeout": ("网关", "超时", "504", "熔断", "连接池", "上游", "延迟", "故障", "排查"),
        "deploy_window": ("发布", "上线", "发版", "窗口", "周五", "合并", "变更", "生产"),
        "vpn_security": ("远程", "居家", "内网", "令牌", "零信任", "vpn", "安全", "脱敏"),
        "project_approval": ("审批", "立项", "预算", "负责人", "流程", "项目"),
        "leave_policy": ("年假", "病假", "休假", "请假", "诊断证明", "工龄"),
    }

    def __init__(self, dim: int = 96) -> None:
        self.dim = dim
        self.documents: List[Document] = []
        self.vectors: List[List[float]] = []

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        lowered = text.lower()

        # 1. 前 12 维编码企业语义概念桶（模拟语义泛化能力）
        for g_idx, words in enumerate(self.SEMANTIC_GROUPS.values()):
            hits = sum(1 for w in words if w in lowered)
            if hits > 0:
                vec[g_idx] += 2.5 * math.log1p(hits)

        # 2. 其余维度采用中文二元词特征哈希（有意淡化纯错误码权重，体现语义模型特点）
        cn_chunks = re.findall(r"[\u4e00-\u9fff]+", lowered)
        for chunk in cn_chunks:
            for i in range(len(chunk) - 1):
                bg = chunk[i : i + 2]
                h = int(hashlib.md5(bg.encode("utf-8")).hexdigest(), 16)
                slot = 12 + (h % (self.dim - 12))
                vec[slot] += 1.0

        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    @staticmethod
    def cosine(a: Sequence[float], b: Sequence[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def add_documents(self, docs: Sequence[Document]) -> None:
        for doc in docs:
            self.documents.append(doc)
            self.vectors.append(self.embed(doc.page_content))

    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        if not self.documents:
            return []
        q_vec = self.embed(query)
        scored = [
            (doc, round(self.cosine(q_vec, d_vec), 4))
            for doc, d_vec in zip(self.documents, self.vectors)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]


class HybridRRFRetriever:
    """
    BM25 + Dense 向量混合检索器（基于 RRF 倒数排名融合）。
    公式：RRF(d) = w_bm25 / (rrf_k + rank_bm25(d)) + w_dense / (rrf_k + rank_dense(d))
    """

    def __init__(
        self,
        bm25_index: BM25Index,
        dense_index: DenseVectorIndex,
        rrf_k: int = 60,
        bm25_weight: float = 0.5,
        dense_weight: float = 0.5,
    ) -> None:
        self.bm25_index = bm25_index
        self.dense_index = dense_index
        self.rrf_k = rrf_k
        self.bm25_weight = bm25_weight
        self.dense_weight = dense_weight

    def retrieve(self, query: str, top_k: int = 5, recall_k: int = 10) -> List[Tuple[Document, float]]:
        bm25_hits = self.bm25_index.search(query, k=recall_k)
        dense_hits = self.dense_index.search(query, k=recall_k)

        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        for rank, (doc, _score) in enumerate(bm25_hits, start=1):
            did = doc.doc_id
            doc_map[did] = doc
            rrf_scores[did] = rrf_scores.get(did, 0.0) + self.bm25_weight / (self.rrf_k + rank)

        for rank, (doc, _score) in enumerate(dense_hits, start=1):
            did = doc.doc_id
            doc_map[did] = doc
            rrf_scores[did] = rrf_scores.get(did, 0.0) + self.dense_weight / (self.rrf_k + rank)

        fused = [(doc_map[did], round(score, 6)) for did, score in rrf_scores.items()]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused[:top_k]


def build_enterprise_sample_docs() -> List[Document]:
    """构建星辰数科故障排查 + 制度 + 内部代号混合测试语料。"""
    return [
        Document(
            "【运维故障手册】错误码 ERR-5042 表示星辰统一网关调用上游推理服务超时（默认阈值 15s）。"
            "排查步骤：1. 检查上游 Pod CPU/显存水位；2. 核对 Nginx proxy_read_timeout 配置；3. 开启降级熔断。",
            {"doc_id": "ops-5042", "source": "运维故障排查手册.md", "section": "ERR-5042网关超时"},
        ),
        Document(
            "【运维故障手册】错误码 ERR-4019 表示零信任 VPN 动态令牌校验失败，常见原因是客户端系统时钟偏差超过 30 秒，请同步 NTP 时间。",
            {"doc_id": "ops-4019", "source": "运维故障排查手册.md", "section": "ERR-4019令牌失效"},
        ),
        Document(
            "【项目规范】内部代号「天枢项目」为星辰智脑 2026 核心知识库中台，项目负责人为架构师老陈，预算审批需经 CTO 终审。",
            {"doc_id": "proj-tianshu", "source": "内部项目立项白皮书.md", "section": "天枢项目立项"},
        ),
        Document(
            "【财务报销制度】一线城市（北京、上海、深圳、广州）出差酒店住宿报销上限为每晚 600 元，需提前在 OA 提交差旅申请。",
            {"doc_id": "fin-hotel", "source": "财务报销制度_v3.md", "section": "差旅住宿标准"},
        ),
        Document(
            "【研发规范】生产环境日常发布窗口为周一至周四 10:00-18:00，严禁周五 17:00 之后提交非紧急上线变更。",
            {"doc_id": "dev-window", "source": "研发工程规范.md", "section": "生产发布窗口"},
        ),
    ]


if __name__ == "__main__":
    docs = build_enterprise_sample_docs()
    bm25 = BM25Index()
    dense = DenseVectorIndex()
    bm25.add_documents(docs)
    dense.add_documents(docs)
    hybrid = HybridRRFRetriever(bm25, dense)

    for q in ("ERR-5042 报错怎么排查？", "天枢项目预算找谁审批？", "去魔都出差住店报销上限"):
        print(f"\nQuery: {q}")
        print("  BM25  Top1:", [(d.doc_id, s) for d, s in bm25.search(q, k=1)])
        print("  Dense Top1:", [(d.doc_id, s) for d, s in dense.search(q, k=1)])
        print("  RRF   Top2:", [(d.doc_id, s) for d, s in hybrid.retrieve(q, top_k=2)])

