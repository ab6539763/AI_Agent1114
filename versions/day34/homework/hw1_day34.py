"""
Day 34 课后作业 1（基础巩固）：作业一：实现 Answer Correctness（综合答案正确性 F1）指标
工单：STARMIND-034
"""

"""Day 34 作业一参考答案：Answer Correctness 综合正确性 F1 指标"""
import re
from typing import Set


def _tokens(text: str) -> Set[str]:
    res = set(re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", text.lower()))
    for chunk in re.findall(r"[\u4e00-\u9fff]+", text):
        for i in range(len(chunk) - 1):
            res.add(chunk[i : i + 2])
    return res


def compute_answer_correctness(answer: str, ground_truth: str) -> float:
    a_set, g_set = _tokens(answer), _tokens(ground_truth)
    if not a_set or not g_set:
        return 0.0
    inter = len(a_set & g_set)
    p = inter / len(a_set)
    r = inter / len(g_set)
    return round(2 * p * r / (p + r), 4) if (p + r) > 0 else 0.0


if __name__ == "__main__":
    gt = "北京出差住宿上限每晚600元，需提前3天OA申请。"
    s1 = compute_answer_correctness("北京出差住宿上限每晚600元，需提前3天OA申请。", gt)
    s2 = compute_answer_correctness("北京出差住宿上限每晚600元。", gt)
    s3 = compute_answer_correctness("今天杭州西湖天气不错。", gt)
    print(f"完全匹配={s1}, 部分匹配={s2}, 无关回答={s3}")
    assert s1 == 1.0 and s1 > s2 > s3

