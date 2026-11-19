"""
Day 60 - 模块一：星辰智脑混合检索引擎（BM25 + 语义向量 + RRF 融合）
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Tuple

SYNONYM_GROUPS = [
    ("酒店", "住宿", "差旅", "宾馆"),
    ("报销", "发票", "费用", "核销"),
    ("报错", "异常", "故障", "失败", "错误码"),
    ("熔断", "限流", "超额", "429"),
    ("密码", "登录", "账号", "sso"),
]


def tokenize(text: str) -> List[str]:
    """中英文混合分词：英文/数字完整保留，中文采用 2-gram + 单字"""
    text_low = text.lower()
    alnum = re.findall(r"[a-z0-9_\-]+", text_low)
    cjk_runs = re.findall(r"[\u4e00-\u9fff]+", text_low)
    tokens: List[str] = list(alnum)
    for run in cjk_runs:
        tokens.extend(list(run))
        tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
    return tokens


def semantic_expand(tokens: List[str]) -> Counter[str]:
    """轻量领域同义概念向量投影（生产可无缝替换为 bge-m3 Embedding）"""
    vec = Counter(tokens)
    joined = "".join(tokens)
    for idx, group in enumerate(SYNONYM_GROUPS):
        if any(word in joined for word in group):
            vec[f"__concept_{idx}__"] += 3.0
    return vec


def cosine_sim(v1: Counter[str], v2: Counter[str]) -> float:
    common = set(v1.keys()) & set(v2.keys())
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    n1 = math.sqrt(sum(v * v for v in v1.values()))
    n2 = math.sqrt(sum(v * v for v in v2.values()))
    return dot / max(1e-9, n1 * n2)


@dataclass
class KnowledgeChunk:
    doc_id: str
    title: str
    content: str


class HybridRetriever:
    """BM25 + 语义向量 + RRF 融合检索器"""

    def __init__(self, chunks: List[KnowledgeChunk]) -> None:
        self.chunks = chunks
        self._doc_tokens = [tokenize(f"{c.title} {c.content}") for c in chunks]
        self._doc_vecs = [semantic_expand(toks) for toks in self._doc_tokens]
        self._avg_dl = sum(len(t) for t in self._doc_tokens) / max(1, len(chunks))
        self._df: Counter[str] = Counter()
        for toks in self._doc_tokens:
            for term in set(toks):
                self._df[term] += 1

    def _bm25_scores(self, q_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> List[Tuple[int, float]]:
        n_docs = len(self.chunks)
        scores = []
        for idx, d_toks in enumerate(self._doc_tokens):
            tf = Counter(d_toks)
            dl = len(d_toks)
            s = 0.0
            for qt in q_tokens:
                if qt not in tf:
                    continue
                df = self._df[qt]
                idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)
                num = tf[qt] * (k1 + 1.0)
                den = tf[qt] + k1 * (1.0 - b + b * dl / max(1.0, self._avg_dl))
                s += idf * (num / den)
            scores.append((idx, s))
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def _vector_scores(self, q_tokens: List[str]) -> List[Tuple[int, float]]:
        q_vec = semantic_expand(q_tokens)
        scores = [(idx, cosine_sim(q_vec, d_vec)) for idx, d_vec in enumerate(self._doc_vecs)]
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def search_rrf(self, query: str, top_k: int = 3, rrf_k: int = 60) -> List[Tuple[KnowledgeChunk, float]]:
        q_tokens = tokenize(query)
        bm25_rank = self._bm25_scores(q_tokens)
        vec_rank = self._vector_scores(q_tokens)

        rrf_scores: Dict[int, float] = {}
        for rank, (idx, score) in enumerate(bm25_rank, start=1):
            if score > 0:
                rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (rrf_k + rank)
        for rank, (idx, score) in enumerate(vec_rank, start=1):
            if score > 0:
                rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (rrf_k + rank)

        ordered = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self.chunks[idx], round(sc, 5)) for idx, sc in ordered]


if __name__ == "__main__":
    kb = [
        KnowledgeChunk("DOC-01", "差旅住宿报销标准", "一线城市出差住宿上限650元/晚，需在费用中心上传电子专票核销。"),
        KnowledgeChunk("DOC-02", "网关错误码ERR_4291手册", "错误码ERR_4291表示部门日Token配额已触发100%硬熔断，请联系管理员提额。"),
    ]
    ret = HybridRetriever(kb)
    print("专有码检索:", [(c.doc_id, s) for c, s in ret.search_rrf("接口报 ERR_4291 怎么办")])
    print("同义词检索:", [(c.doc_id, s) for c, s in ret.search_rrf("出差住宾馆最多能花多少钱")])

