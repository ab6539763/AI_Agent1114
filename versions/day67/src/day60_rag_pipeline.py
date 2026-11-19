"""
Day 60 - 模块二：Rerank 精排 + 置信度拒答 + 强制 [doc_id] 引用溯源问答流水线
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from src.day60_hybrid_retriever import HybridRetriever, KnowledgeChunk, cosine_sim, semantic_expand, tokenize


@dataclass
class Citation:
    doc_id: str
    title: str
    rerank_score: float
    snippet: str


@dataclass
class RAGAnswer:
    query: str
    answered: bool
    answer: str
    citations: List[Citation] = field(default_factory=list)


def rerank_score(query: str, chunk: KnowledgeChunk) -> float:
    """精排重打分 [0.0, 1.0]：融合语义余弦 + 标题命中加权 + 关键词覆盖率"""
    q_toks = tokenize(query)
    if not q_toks:
        return 0.0
    title_toks = set(tokenize(chunk.title))
    body_toks = set(tokenize(f"{chunk.title} {chunk.content}"))

    sem = cosine_sim(semantic_expand(q_toks), semantic_expand(list(body_toks)))
    title_hit = sum(1 for t in set(q_toks) if t in title_toks) / max(1, len(set(q_toks)))
    body_hit = sum(1 for t in set(q_toks) if t in body_toks) / max(1, len(set(q_toks)))
    code_tokens = [t for t in set(q_toks) if t.isascii() and any(ch.isdigit() for ch in t)]
    exact_code_boost = 0.35 if (code_tokens and any(t in body_toks for t in code_tokens)) else 0.0
    score = 0.50 * sem + 0.30 * title_hit + 0.20 * body_hit + exact_code_boost
    return round(min(1.0, score), 4)


class StarMindRAGEngine:
    """星辰智脑企业级 RAG 主链路引擎"""

    def __init__(self, chunks: List[KnowledgeChunk], min_confidence: float = 0.22) -> None:
        self.retriever = HybridRetriever(chunks)
        self.min_confidence = min_confidence

    def ask(self, query: str, top_k: int = 2) -> RAGAnswer:
        candidates = self.retriever.search_rrf(query, top_k=max(top_k * 2, 4))
        reranked = sorted(
            [(chunk, rerank_score(query, chunk)) for chunk, _ in candidates],
            key=lambda x: x[1],
            reverse=True,
        )
        if not reranked or reranked[0][1] < self.min_confidence:
            return RAGAnswer(
                query=query,
                answered=False,
                answer="抱歉，星辰知识库中未检索到足够可信的依据，为避免幻觉拒绝编造答案，请联系对应部门人工核实。",
                citations=[],
            )

        selected = [item for item in reranked[:top_k] if item[1] >= self.min_confidence * 0.8]
        citations = [
            Citation(c.doc_id, c.title, sc, c.content[:80])
            for c, sc in selected
        ]
        summary_lines = [f"- {c.content} [{c.doc_id}]" for c, _ in selected]
        answer_text = "根据星辰数科企业知识库检索结果，为您整理如下依据：\n" + "\n".join(summary_lines)
        return RAGAnswer(query=query, answered=True, answer=answer_text, citations=citations)


if __name__ == "__main__":
    kb = [
        KnowledgeChunk("DOC-01", "差旅住宿报销标准", "一线城市出差住宿上限650元/晚，需在费用中心上传电子专票核销。"),
        KnowledgeChunk("DOC-02", "网关错误码ERR_4291手册", "错误码ERR_4291表示部门日Token配额已触发100%硬熔断，请联系管理员提额。"),
    ]
    rag = StarMindRAGEngine(kb)
    print("命中场景:", rag.ask("出差住宾馆报销标准是什么？"))
    print("拒答场景:", rag.ask("火星移民飞船票价多少？"))

