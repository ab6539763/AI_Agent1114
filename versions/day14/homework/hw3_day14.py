"""
Day 14 课后作业 3（架构进阶）：架构进阶：基于 Token 预算的智能上下文裁剪器
工单：STARMIND-014
"""

"""Day 14 课后题 3：按字符/Token 预算倒序裁剪多轮上下文。"""

from typing import Dict, List


def trim_messages_by_budget(
    system_prompt: str,
    messages: List[Dict[str, str]],
    max_chars: int,
) -> List[Dict[str, str]]:
    """在严格不超过 max_chars 预算的前提下，保留 system 人设与尽可能多的新近消息。"""
    budget = max_chars - len(system_prompt)
    selected_rev: List[Dict[str, str]] = []

    for msg in reversed(messages):
        cost = len(msg.get("content", ""))
        if cost <= budget:
            selected_rev.append(msg)
            budget -= cost
        else:
            break

    selected_rev.reverse()
    return [{"role": "system", "content": system_prompt}, *selected_rev]


if __name__ == "__main__":
    history = [
        {"role": "user", "content": "这是一条很老很长的历史问题" * 3},
        {"role": "assistant", "content": "旧回复"},
        {"role": "user", "content": "最新问题"},
        {"role": "assistant", "content": "最新回复"},
    ]
    trimmed = trim_messages_by_budget("系统人设", history, max_chars=25)
    print(trimmed)

