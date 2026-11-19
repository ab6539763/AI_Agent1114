"""
Day 06 课后作业 1（基础巩固）：基础巩固：修复可变默认参数 Bug
工单：STARMIND-006
"""

"""Day 6 课后题 1：修复可变默认参数导致的对话串台 Bug。"""

from typing import List, Optional


def append_message(msg: str, history: Optional[List[str]] = None) -> List[str]:
    """安全追加对话消息，每次未传 history 时创建全新列表。"""
    records = [] if history is None else list(history)
    records.append(msg)
    return records


if __name__ == "__main__":
    user_a = append_message("你好，我是A")
    user_b = append_message("你好，我是B")
    print("用户A:", user_a)
    print("用户B:", user_b)

