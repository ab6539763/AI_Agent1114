"""
Day 36 - 步骤一：阶段项目二(上) 企业级知识库核心引擎
支持：多格式文档解析(MD/TXT/JSON/CSV)、doc_id 幂等 Upsert/删除、部门 ACL 过滤、
     BM25 + Dense 向量 RRF 混合检索 + Cross-Encoder 精排 + 阈值拒答
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
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass
class KBChunk:
    chunk_id: str
    doc_id: str
    source: str
    section: str
    department: str
    content: str
    chunk_index: int


@dataclass
class CitationItem:
    doc_id: str
    source: str
    section: str
    snippet: str
    score: float


@dataclass
class QAResult:
    question: str
    answer: str
    citations: List[CitationItem]
    refused: bool
    latency_ms: float
    used_rerank: bool


def tokenize_text(text: str) -> List[str]:
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", lowered)
    for chunk in re.findall(r"[\u4e00-\u9fff]+", lowered):
        for ch in chunk:
            tokens.append(ch)
        for i in range(len(chunk) - 1):
            tokens.append(chunk[i : i + 2])
    return tokens


class MultiFormatParser:
    """企业多格式文档统一解析与语义切分器（支持 md / txt / json / csv）。"""

    @staticmethod
    def parse(
        doc_id: str,
        source: str,
        fmt: str,
        content: str,
        department: str = "public",
        chunk_size: int = 180,
    ) -> List[KBChunk]:
        fmt_lower = fmt.lower().strip(".")
        chunks: List[KBChunk] = []

        if fmt_lower == "md":
            # 按 Markdown 二级标题分段保留章节名
            sections = re.split(r"(?m)^##\s+", content.strip())
            idx = 0
            for raw_sec in sections:
                raw_sec = raw_sec.strip()
                if not raw_sec:
                    continue
                lines = raw_sec.splitlines()
                sec_title = lines[0].strip("# ") if len(lines) > 1 else "正文"
                body = "\n".join(lines[1:]).strip() if len(lines) > 1 else raw_sec
                for start in range(0, max(1, len(body)), chunk_size):
                    piece = body[start : start + chunk_size].strip()
                    if not piece:
                        continue
                    chunks.append(
                        KBChunk(
                            chunk_id=f"{doc_id}#c{idx}",
                            doc_id=doc_id,
                            source=source,
                            section=sec_title,
                            department=department,
                            content=piece,
                            chunk_index=idx,
                        )
                    )
                    idx += 1
            return chunks

        if fmt_lower == "csv":
            reader = csv.DictReader(io.StringIO(content.strip()))
            for idx, row in enumerate(reader):
                kv_text = "；".join(f"{k.strip()}: {str(v).strip()}" for k, v in row.items() if k)
                if kv_text:
                    chunks.append(
                        KBChunk(
                            chunk_id=f"{doc_id}#c{idx}",
                            doc_id=doc_id,
                            source=source,
                            section=f"表格第{idx + 1}行",
                            department=department,
                            content=kv_text,
                            chunk_index=idx,
                        )
                    )
            return chunks

        if fmt_lower == "json":
            data = json.loads(content)
            items = data if isinstance(data, list) else [data]
            for idx, item in enumerate(items):
                if isinstance(item, dict):
                    sec = str(item.get("code") or item.get("title") or f"条目{idx + 1}")
                    text = "；".join(f"{k}: {v}" for k, v in item.items())
                else:
                    sec = f"条目{idx + 1}"
                    text = str(item)
                chunks.append(
                    KBChunk(
                        chunk_id=f"{doc_id}#c{idx}",
                        doc_id=doc_id,
                        source=source,
                        section=sec,
                        department=department,
                        content=text,
                        chunk_index=idx,
                    )
                )
            return chunks

        # 默认按 txt 段落切分
        paras = [p.strip() for p in re.split(r"\n{2,}", content.strip()) if p.strip()]
        for idx, p in enumerate(paras):
            chunks.append(
                KBChunk(
                    chunk_id=f"{doc_id}#c{idx}",
                    doc_id=doc_id,
                    source=source,
                    section=f"段落{idx + 1}",
                    department=department,
                    content=p,
                    chunk_index=idx,
                )
            )
        return chunks


class EnterpriseKBEngine:
    """StarMind-KB v2.0 核心引擎：多格式入库、ACL过滤、混合RRF检索与Cross-Encoder精排。"""

    def __init__(self, refuse_threshold: float = 0.25, dim: int = 96) -> None:
        self.refuse_threshold = refuse_threshold
        self.dim = dim
        self.doc_registry: Dict[str, Dict[str, Any]] = {}
        self.chunks: List[KBChunk] = []
        self._chunk_tfs: Dict[str, Counter[str]] = {}
        self._chunk_vecs: Dict[str, List[float]] = {}

    def _embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for tok in tokenize_text(text):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            vec[h % self.dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def ingest_document(
        self,
        doc_id: str,
        source: str,
        fmt: str,
        content: str,
        department: str = "public",
    ) -> int:
        """幂等入库：若 doc_id 已存在则先清除旧切片再写入新版本。"""
        self.delete_document(doc_id)
        new_chunks = MultiFormatParser.parse(
            doc_id=doc_id, source=source, fmt=fmt, content=content, department=department
        )
        for ch in new_chunks:
            self.chunks.append(ch)
            self._chunk_tfs[ch.chunk_id] = Counter(tokenize_text(ch.content + " " + ch.section))
            self._chunk_vecs[ch.chunk_id] = self._embed(ch.content + " " + ch.section)

        self.doc_registry[doc_id] = {
            "doc_id": doc_id,
            "source": source,
            "format": fmt,
            "department": department,
            "chunk_count": len(new_chunks),
        }
        return len(new_chunks)

    def delete_document(self, doc_id: str) -> bool:
        if doc_id not in self.doc_registry:
            return False
        kept: List[KBChunk] = []
        for ch in self.chunks:
            if ch.doc_id == doc_id:
                self._chunk_tfs.pop(ch.chunk_id, None)
                self._chunk_vecs.pop(ch.chunk_id, None)
            else:
                kept.append(ch)
        self.chunks = kept
        self.doc_registry.pop(doc_id, None)
        return True

    def list_documents(self) -> List[Dict[str, Any]]:
        return list(self.doc_registry.values())

    def _rerank_score(self, query: str, chunk: KBChunk) -> float:
        q_tokens = set(tokenize_text(query))
        if not q_tokens:
            return 0.0
        c_tokens = set(self._chunk_tfs[chunk.chunk_id].keys())
        q_bigrams = {t for t in q_tokens if len(t) >= 2}
        c_bigrams = {t for t in c_tokens if len(t) >= 2}
        overlap_bi = len(q_bigrams & c_bigrams) / max(1, len(q_bigrams)) if q_bigrams else 0.0
        overlap_all = len(q_tokens & c_tokens) / max(1, len(q_tokens))
        q_codes = set(re.findall(r"[a-z0-9]+[-_][a-z0-9]+", query.lower()))
        code_bonus = 0.35 if (q_codes and any(c in chunk.content.lower() for c in q_codes)) else 0.0
        return round(min(1.0, 0.55 * overlap_bi + 0.35 * overlap_all + code_bonus), 4)

    def search(
        self,
        question: str,
        top_k: int = 3,
        department: str = "public",
        use_rerank: bool = True,
    ) -> List[Tuple[KBChunk, float]]:
        # 1. ACL 权限预过滤（Pre-Filtering）
        allowed_depts = {"public", department}
        pool = [ch for ch in self.chunks if ch.department in allowed_depts]
        if not pool:
            return []

        q_tokens = tokenize_text(question)
        q_vec = self._embed(question)

        # 2. BM25 稀疏打分
        n_docs = len(pool)
        df: Counter[str] = Counter()
        lengths: Dict[str, int] = {}
        for ch in pool:
            tf = self._chunk_tfs[ch.chunk_id]
            lengths[ch.chunk_id] = sum(tf.values())
            for t in tf.keys():
                df[t] += 1
        avgdl = sum(lengths.values()) / max(1, n_docs)

        bm25_ranked: List[Tuple[KBChunk, float]] = []
        for ch in pool:
            tf = self._chunk_tfs[ch.chunk_id]
            dl = lengths[ch.chunk_id]
            s = 0.0
            for t in q_tokens:
                freq = tf.get(t, 0)
                if freq == 0:
                    continue
                idf = math.log(1.0 + (n_docs - df[t] + 0.5) / (df[t] + 0.5))
                s += idf * (freq * 2.5) / (freq + 1.5 * (0.25 + 0.75 * dl / max(1e-9, avgdl)))
            if s > 0:
                bm25_ranked.append((ch, s))
        bm25_ranked.sort(key=lambda x: x[1], reverse=True)

        # 3. Dense 向量余弦打分
        dense_ranked: List[Tuple[KBChunk, float]] = []
        for ch in pool:
            c_vec = self._chunk_vecs[ch.chunk_id]
            sim = sum(x * y for x, y in zip(q_vec, c_vec))
            if sim > 0:
                dense_ranked.append((ch, sim))
        dense_ranked.sort(key=lambda x: x[1], reverse=True)

        # 4. RRF 倒数排名融合
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, KBChunk] = {}
        for rank, (ch, _) in enumerate(bm25_ranked[:10], start=1):
            chunk_map[ch.chunk_id] = ch
            rrf_scores[ch.chunk_id] = rrf_scores.get(ch.chunk_id, 0.0) + 0.5 / (60 + rank)
        for rank, (ch, _) in enumerate(dense_ranked[:10], start=1):
            chunk_map[ch.chunk_id] = ch
            rrf_scores[ch.chunk_id] = rrf_scores.get(ch.chunk_id, 0.0) + 0.5 / (60 + rank)

        candidates = [
            chunk_map[cid]
            for cid, _ in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:8]
        ]
        if not candidates:
            return []

        # 5. Cross-Encoder 精排（或直接返回归一化特征分）
        scored = [(ch, self._rerank_score(question, ch)) for ch in candidates]
        if use_rerank:
            scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def query(
        self,
        question: str,
        top_k: int = 3,
        department: str = "public",
        use_rerank: bool = True,
    ) -> QAResult:
        t0 = time.perf_counter()
        hits = self.search(question, top_k=top_k, department=department, use_rerank=use_rerank)
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        if not hits or hits[0][1] < self.refuse_threshold:
            return QAResult(
                question=question,
                answer="抱歉，星辰知识库当前授权范围内未检索到足够可靠的依据，无法回答该问题。",
                citations=[],
                refused=True,
                latency_ms=latency_ms,
                used_rerank=use_rerank,
            )

        citations = [
            CitationItem(
                doc_id=ch.doc_id,
                source=ch.source,
                section=ch.section,
                snippet=ch.content[:140],
                score=sc,
            )
            for ch, sc in hits
            if sc >= self.refuse_threshold
        ]
        evidence_lines = [
            f"[{i}] {c.snippet}（来源：{c.source} · {c.section}）"
            for i, c in enumerate(citations, start=1)
        ]
        answer = f"根据星辰数科知识库检索结果，针对「{question}」解答如下：\n" + "\n".join(evidence_lines)
        return QAResult(
            question=question,
            answer=answer,
            citations=citations,
            refused=False,
            latency_ms=latency_ms,
            used_rerank=use_rerank,
        )


def build_seeded_kb_engine() -> EnterpriseKBEngine:
    """预置星辰数科多格式演示知识库（MD + CSV + JSON）。"""
    engine = EnterpriseKBEngine()
    engine.ingest_document(
        doc_id="hr-handbook-2026",
        source="员工休假与差旅手册.md",
        fmt="md",
        department="public",
        content=(
            "## 年假与病假规定\n"
            "入职满1年员工享有5天带薪年假，年假需提前3个工作日提交OA审批；病假超过2天须提供公立医院诊断证明。\n\n"
            "## 生产发布窗口\n"
            "业务代码日常发布窗口为周一至周四10:00-18:00，严禁周五17:00后提交非紧急上线变更。"
        ),
    )
    engine.ingest_document(
        doc_id="fin-travel-table",
        source="差旅住宿标准表.csv",
        fmt="csv",
        department="public",
        content="城市等级,代表城市,住宿上限,餐饮补助\n一线城市,北京/上海/深圳/广州,每晚600元,每天100元\n新一线城市,杭州/成都/武汉,每晚450元,每天100元\n",
    )
    engine.ingest_document(
        doc_id="ops-err-dict",
        source="网关错误码字典.json",
        fmt="json",
        department="rd",
        content=json.dumps(
            [
                {"code": "ERR-5042", "meaning": "统一网关调用上游推理服务超时", "action": "检查上游Pod显存并调大proxy_read_timeout"},
                {"code": "ERR-4019", "meaning": "零信任VPN动态令牌校验失败", "action": "同步客户端NTP时钟"},
            ],
            ensure_ascii=False,
        ),
    )
    engine.ingest_document(
        doc_id="fin-salary-secret",
        source="2026高管薪酬方案.txt",
        fmt="txt",
        department="finance",
        content="2026年高管年终奖金池基数为税前净利润的8%，仅限财务总监与CEO查阅。",
    )
    return engine


if __name__ == "__main__":
    kb = build_seeded_kb_engine()
    print("已入库文档:", [(d["doc_id"], d["department"], d["chunk_count"]) for d in kb.list_documents()])
    r1 = kb.query("ERR-5042 怎么处理？", department="rd")
    print("\n研发查错误码:", r1.answer)
    r2 = kb.query("高管年终奖金池基数是多少？", department="rd")
    print("\n研发越权查高管薪酬 refused=", r2.refused)

