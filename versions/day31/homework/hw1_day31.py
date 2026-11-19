"""
Day 31 课后作业 1（基础巩固）：作业一：实现 NDCG@K（归一化折损累计增益）检索评估指标
工单：STARMIND-031
"""

"""Day 31 作业一参考答案：多相关文档评估指标 NDCG@K"""
import math
from typing import Sequence


def compute_dcg(relevances: Sequence[float], k: int) -> float:
    return sum(rel / math.log2(idx + 2) for idx, rel in enumerate(relevances[:k]))


def compute_ndcg(relevances: Sequence[float], k: int) -> float:
    actual = compute_dcg(relevances, k)
    ideal = compute_dcg(sorted(relevances, reverse=True), k)
    return round(actual / ideal, 4) if ideal > 0 else 0.0


if __name__ == "__main__":
    print("理想排序 [1, 1, 0] -> NDCG@3 =", compute_ndcg([1, 1, 0], 3))
    print("次优排序 [0, 1, 1] -> NDCG@3 =", compute_ndcg([0, 1, 1], 3))
    assert compute_ndcg([1, 1, 0], 3) == 1.0
    assert compute_ndcg([0, 1, 1], 3) < 1.0

