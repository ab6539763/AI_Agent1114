"""
Day 04 课后作业 3（架构进阶）：架构进阶：列表推导式实现滑动窗口切块
工单：STARMIND-004
"""

"""Day 4 课后题 3：滑动窗口切块器（RAG 分块原型）。"""

from typing import List, Tuple, Any


def sliding_window(items: List[Any], size: int, step: int = 1) -> List[Tuple[Any, ...]]:
    """按窗口大小与步长切分序列，返回不可变窗口元组列表。"""
    if size <= 0 or step <= 0 or size > len(items):
        return []
    return [tuple(items[i : i + size]) for i in range(0, len(items) - size + 1, step)]


if __name__ == "__main__":
    sentences = ["句1", "句2", "句3", "句4", "句5"]
    print("窗口=3, 步长=2:", sliding_window(sentences, size=3, step=2))

