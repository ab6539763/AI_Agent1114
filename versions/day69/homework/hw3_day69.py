"""
Day 69 课后作业 3（架构进阶）：架构进阶：实现面试题库错题间隔重复调度器（Spaced Repetition）
工单：STARMIND-069
"""

def next_review_days(mastery: int) -> int:
    mapping = {1: 1, 2: 3, 3: 7}
    if mastery not in mapping:
        raise ValueError("mastery 仅支持 1/2/3")
    return mapping[mastery]


assert [next_review_days(1), next_review_days(2), next_review_days(3)] == [1, 3, 7]
print("艾宾浩斯面试复习调度通过")

