"""
Day 20 课后作业 2（企业实战）：向量检索评估指标 MRR（Mean Reciprocal Rank）计算器
工单：STARMIND-020
"""

from typing import List, Tuple
from src.day20_semantic_matcher import FAQEntry, SemanticFAQMatcher


def evaluate_mrr(matcher: SemanticFAQMatcher, test_cases: List[Tuple[str, str]], top_k: int = 3) -> float:
    """计算语义检索系统的 MRR (Mean Reciprocal Rank) 指标。"""
    if not test_cases:
        return 0.0
    total_rr = 0.0
    for query, expected_id in test_cases:
        hits = matcher.search(query, top_k=top_k, min_score=0.0)
        for rank, hit in enumerate(hits, 1):
            if hit.faq_id == expected_id:
                total_rr += 1.0 / rank
                break
    return round(total_rr / len(test_cases), 4)


if __name__ == "__main__":
    m = SemanticFAQMatcher()
    m.add_faqs([
        FAQEntry("F1", "差旅住宿报销标准", "600元/晚", "fin"),
        FAQEntry("F2", "内网VPN申请流程", "OA提交", "it"),
    ])
    print("MRR:", evaluate_mrr(m, [("出差住酒店报多少", "F1"), ("连不上公司内网", "F2")]))

