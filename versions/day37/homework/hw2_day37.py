"""
Day 37 课后作业 2（企业实战）：作业二：实现基于滑动 Token 预算的对话历史裁剪器
工单：STARMIND-037
"""

"""Day 37 作业二参考答案：基于字符/Token 预算的滑动历史裁剪器"""
from typing import Dict, List, Sequence


def trim_history_by_budget(turns: Sequence[Dict[str, str]], max_chars: int = 80) -> List[Dict[str, str]]:
    kept: List[Dict[str, str]] = []
    used = 0
    for item in reversed(turns):
        size = len(item["content"])
        if used + size > max_chars and kept:
            break
        kept.append(item)
        used += size
    kept.reverse()
    return kept


if __name__ == "__main__":
    hist = [
        {"role": "user", "content": "第一轮很长的历史提问内容" * 3},
        {"role": "assistant", "content": "第一轮很长的历史回答内容" * 3},
        {"role": "user", "content": "北京住宿上限多少？"},
        {"role": "assistant", "content": "每晚600元。"},
    ]
    trimmed = trim_history_by_budget(hist, max_chars=30)
    print("裁剪后保留:", trimmed)
    assert len(trimmed) == 2 and trimmed[0]["content"] == "北京住宿上限多少？"

