"""
Day 21 课后作业 1（基础巩固）：按 Token 预算动态裁剪对话历史
工单：STARMIND-021
"""

from typing import Dict, List


def trim_by_char_budget(messages: List[Dict[str, str]], max_chars: int) -> List[Dict[str, str]]:
    """保留 system 消息，按字符预算从最新记录倒序裁剪历史。"""
    if not messages:
        return []
    head = [messages[0]] if messages[0].get("role") == "system" else []
    body = messages[1:] if head else messages
    kept: List[Dict[str, str]] = []
    used = 0
    for msg in reversed(body):
        length = len(msg.get("content", ""))
        if used + length > max_chars:
            break
        kept.append(msg)
        used += length
    kept.reverse()
    return head + kept


if __name__ == "__main__":
    sample = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "很早之前的超长历史记录" * 5},
        {"role": "user", "content": "最新问题"},
        {"role": "assistant", "content": "最新回答"},
    ]
    print(trim_by_char_budget(sample, max_chars=20))

