"""
Day 27 课后作业 1（基础巩固）：作业一：实现按 Token 预算精确裁剪的 TokenBudgetMemoryStrategy
工单：STARMIND-027
"""

"""Day 27 作业一参考答案：按 Token 预算精确裁剪记忆"""
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import AIMessage, BaseChatModel, BaseMessage, HumanMessage


class TokenBudgetMemoryStrategy:
    def __init__(self, max_tokens: int = 120) -> None:
        self.max_tokens = max_tokens

    def compress(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        if len(messages) <= 2:
            return list(messages)
        selected_rev: List[BaseMessage] = []
        used = 0
        # 按 (human, ai) 成对从后往前扫描
        i = len(messages) - 1
        while i >= 1:
            pair = [messages[i - 1], messages[i]]
            pair_tokens = sum(BaseChatModel._estimate_tokens(m.content) for m in pair)
            if selected_rev and used + pair_tokens > self.max_tokens:
                break
            selected_rev.extend(reversed(pair))
            used += pair_tokens
            i -= 2
        return list(reversed(selected_rev))


if __name__ == "__main__":
    msgs = []
    for idx in range(6):
        msgs.append(HumanMessage(content=f"问题{idx}：请详细介绍杭州星辰数科的差旅住宿报销标准与审批流"))
        msgs.append(AIMessage(content=f"回答{idx}：一线城市每日上限600元，需部门主管审批"))
    strategy = TokenBudgetMemoryStrategy(max_tokens=60)
    kept = strategy.compress(msgs)
    print("原消息数:", len(msgs), "-> 裁剪后消息数:", len(kept))
    assert len(kept) < len(msgs) and len(kept) % 2 == 0

