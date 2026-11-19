"""
Day 20 课后作业 3（架构进阶）：混合检索分数融合器（RRF 倒数排名融合）
工单：STARMIND-020
"""

from typing import Dict, List, Tuple


def rrf_fuse(list_a: List[str], list_b: List[str], k: int = 60) -> List[Tuple[str, float]]:
    """Reciprocal Rank Fusion (RRF) 混合检索多路排名融合算法。"""
    scores: Dict[str, float] = {}
    for ranked_list in (list_a, list_b):
        for rank, doc_id in enumerate(ranked_list, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(((d, round(s, 6)) for d, s in scores.items()), key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    bm25_top = ["DOC-2", "DOC-1", "DOC-5"]
    vector_top = ["DOC-1", "DOC-3", "DOC-2"]
    print("RRF 融合排名:", rrf_fuse(bm25_top, vector_top))

