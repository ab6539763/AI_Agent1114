"""
Day 41 课后作业 2（企业实战）：实现自定义字典合并 Reducer（支持统计各节点耗时）
工单：STARMIND-041
"""

"""Day 41 作业 2 参考答案：指标字典合并 Reducer。"""

from typing import Dict


def merge_metrics_reducer(old: Dict[str, float], new: Dict[str, float]) -> Dict[str, float]:
    merged = dict(old)
    merged.update(new)
    return merged


if __name__ == "__main__":
    s1 = merge_metrics_reducer({"parse": 1.2}, {"approve": 5.4})
    s2 = merge_metrics_reducer(s1, {"order": 2.1})
    print("合并指标:", s2)
    assert s2 == {"parse": 1.2, "approve": 5.4, "order": 2.1}

