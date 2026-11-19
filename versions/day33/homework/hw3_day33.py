"""
Day 33 课后作业 3（架构进阶）：作业三：实现带延迟统计的 Top-K 精排截断阈值滤波器
工单：STARMIND-033
"""

"""Day 33 作业三参考答案：精排动态截断阈值滤波器"""
from typing import List, Tuple


def smart_rerank_cutoff(
    ranked_items: List[Tuple[str, float]],
    min_score: float = 0.45,
    gap_threshold: float = 0.35,
) -> List[Tuple[str, float]]:
    filtered = [(doc, sc) for doc, sc in ranked_items if sc >= min_score]
    if len(filtered) >= 2 and (filtered[0][1] - filtered[1][1]) > gap_threshold:
        return [filtered[0]]
    return filtered


if __name__ == "__main__":
    case_gap = [("最优文档", 0.95), ("弱相关文档", 0.50), ("噪音文档", 0.20)]
    case_close = [("文档A", 0.88), ("文档B", 0.82), ("噪音文档", 0.15)]
    out1 = smart_rerank_cutoff(case_gap)
    out2 = smart_rerank_cutoff(case_close)
    print("断层领先截断:", out1)
    print("势均力敌保留:", out2)
    assert len(out1) == 1 and len(out2) == 2

