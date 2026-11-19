"""
Day 18 课后作业 3（架构进阶）：带加权专家置信度的 Self-Consistency 投票器
工单：STARMIND-018
"""

from typing import Dict, List, Tuple


def weighted_majority_vote(ballots: List[Tuple[str, float]]) -> Tuple[str, float]:
    """多模型加权自一致性投票。"""
    if not ballots:
        raise ValueError("ballots 不能为空")
    totals: Dict[str, float] = {}
    for label, weight in ballots:
        if weight <= 0:
            raise ValueError("权重必须为正数")
        totals[label] = totals.get(label, 0.0) + weight
    total_weight = sum(totals.values())
    winner, win_weight = max(totals.items(), key=lambda kv: kv[1])
    return winner, round(win_weight / total_weight, 4)


if __name__ == "__main__":
    print(weighted_majority_vote([("refund", 0.5), ("complaint", 0.3), ("refund", 0.4)]))

