"""
Day 29 课后作业 2（企业实战）：作业二：实现最大边际相关性检索（MMR，Maximal Marginal Relevance）
工单：STARMIND-029
"""

"""Day 29 作业二参考答案：MMR 最大边际相关性多样化检索"""
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_embeddings_hnsw import cosine_similarity
from src.day29_vector_store import StarMindVectorStore


def mmr_search(
    store: StarMindVectorStore,
    query: str,
    k: int = 3,
    fetch_k: int = 8,
    lambda_mult: float = 0.5,
) -> List[Document]:
    q_vec = store.embedding_function.embed_query(query)
    raw_hits = store.similarity_search_with_score(query, k=fetch_k)
    if not raw_hits:
        return []

    cand_docs = [doc for doc, _ in raw_hits]
    cand_vecs = [store.embedding_function.embed_query(d.page_content) for d in cand_docs]

    selected_indices: List[int] = []
    remaining = list(range(len(cand_docs)))

    while remaining and len(selected_indices) < k:
        best_idx = -1
        best_score = -1e9
        for idx in remaining:
            rel = cosine_similarity(q_vec, cand_vecs[idx])
            redundancy = (
                max(cosine_similarity(cand_vecs[idx], cand_vecs[s]) for s in selected_indices)
                if selected_indices
                else 0.0
            )
            mmr_score = lambda_mult * rel - (1.0 - lambda_mult) * redundancy
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx
        selected_indices.append(best_idx)
        remaining.remove(best_idx)

    return [cand_docs[i] for i in selected_indices]


if __name__ == "__main__":
    vs = StarMindVectorStore()
    vs.add_documents([
        Document("一线城市出差住宿上限600元。", {"id": 1}),
        Document("一线城市出差住宿上限为600元每晚。", {"id": 2}),  # 与id=1高度重复
        Document("出差餐饮补助每天100元无需发票。", {"id": 3}),
    ])
    diversified = mmr_search(vs, "出差报销标准", k=2, lambda_mult=0.5)
    print("MMR 多样化召回:", [(d.metadata["id"], d.page_content) for d in diversified])
    assert {d.metadata["id"] for d in diversified} != {1, 2}

