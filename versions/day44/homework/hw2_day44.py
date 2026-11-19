"""
Day 44 课后作业 2（企业实战）：实现基于规则的用户偏好自动提取器
工单：STARMIND-044
"""

"""Day 44 作业 2 参考答案：自然语言长期记忆候选提取器。"""

from typing import List, Tuple


def extract_preferences(utterance: str) -> List[Tuple[str, str, int]]:
    items: List[Tuple[str, str, int]] = []
    if any(k in utterance for k in ("以后", "请始终", "喜欢用")):
        items.append(("preference", utterance.strip(), 5))
    elif any(k in utterance for k in ("我在", "我负责")):
        items.append(("fact", utterance.strip(), 4))
    return items


if __name__ == "__main__":
    p1 = extract_preferences("以后回复我的周报都用表格列出")
    p2 = extract_preferences("今天天气不错")
    print("提取结果:", p1, "| 闲聊过滤:", p2)
    assert len(p1) == 1 and p1[0][0] == "preference"
    assert p2 == []

