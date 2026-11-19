"""
Day 60 课后作业 3（架构进阶）：架构进阶：计算 Recall@K 与 MRR 检索质量指标
工单：STARMIND-060
"""

def eval_retrieval(retrieved_list: list[list[str]], expected_list: list[str], k: int = 3) -> dict:
    hits, rr_sum = 0, 0.0
    for ret, exp in zip(retrieved_list, expected_list):
        top_k = ret[:k]
        if exp in top_k:
            hits += 1
            rr_sum += 1.0 / (top_k.index(exp) + 1)
    n = max(1, len(expected_list))
    return {"recall_at_k": round(hits / n, 4), "mrr": round(rr_sum / n, 4)}


print(eval_retrieval([["D1", "D2"], ["D3", "D1"], ["D2", "D3"]], ["D1", "D1", "D4"]))

