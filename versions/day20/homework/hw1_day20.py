"""
Day 20 课后作业 1（基础巩固）：批量文本去重器（Semantic Deduplicator）
工单：STARMIND-020
"""

from typing import List
from src.day20_semantic_matcher import StarMindLocalEmbedder, cosine_similarity


def deduplicate_questions(questions: List[str], threshold: float = 0.85) -> List[str]:
    """基于余弦相似度的语义去重器。"""
    embedder = StarMindLocalEmbedder()
    kept_texts: List[str] = []
    kept_vecs: List[List[float]] = []

    for q in questions:
        vec = embedder.embed(q)
        if all(cosine_similarity(vec, kv) < threshold for kv in kept_vecs):
            kept_texts.append(q)
            kept_vecs.append(vec)
    return kept_texts


if __name__ == "__main__":
    raw = [
        "差旅住宿报销标准是多少？",
        "出差住酒店报销上限多少？",
        "新员工怎么申请内网VPN？",
    ]
    print("去重结果:", deduplicate_questions(raw, threshold=0.80))

