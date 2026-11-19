"""
Day 05 课后作业 1（基础巩固）：基础巩固：词频统计字典构建器
工单：STARMIND-005
"""

"""Day 5 课后题 1：工单意图频次统计器。"""

from typing import List, Dict


def count_intents(labels: List[str]) -> Dict[str, int]:
    """统计每个意图标签出现次数，并按频次降序返回字典。"""
    counts: Dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    # 按值降序排列，Python 3.7+ 字典保留插入顺序
    sorted_pairs = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return dict(sorted_pairs)


if __name__ == "__main__":
    sample = ["物流", "退款", "物流", "发票", "物流", "退款"]
    print("意图统计:", count_intents(sample))

