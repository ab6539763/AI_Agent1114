"""
Day 44 课后作业 3（架构进阶）：为长期记忆增加时间衰减（Time Decay）排序因子
工单：STARMIND-044
"""

"""Day 44 作业 3 参考答案：长期记忆指数时间衰减评分。"""


def decay_score(importance: int, age_days: float, half_life_days: float = 30.0) -> float:
    return round(importance * (0.5 ** (max(age_days, 0.0) / half_life_days)), 4)


if __name__ == "__main__":
    recent = decay_score(importance=4, age_days=1.0)
    stale = decay_score(importance=4, age_days=90.0)
    print("近期记忆分:", recent, "| 90天前记忆分:", stale)
    assert recent > stale and stale == 0.5

