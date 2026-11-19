"""
Day 04 课后作业 1（基础巩固）：基础巩固：保序去重工具
工单：STARMIND-004
"""

"""Day 4 课后题 1：RAG 召回文档保序去重。"""

from typing import List


def dedupe_keep_order(items: List[str]) -> List[str]:
    """去除重复元素并严格保留首次出现的顺序。"""
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


if __name__ == "__main__":
    recalled = ["doc3", "doc1", "doc3", "doc2", "doc1"]
    print("保序去重结果:", dedupe_keep_order(recalled))

