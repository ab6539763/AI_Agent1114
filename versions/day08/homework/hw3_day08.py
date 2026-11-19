"""
Day 08 课后作业 3（架构进阶）：架构进阶：支持上下文 Token 预算自动裁剪的会话类
工单：STARMIND-008
"""

"""Day 8 课后题 3：按 Token 预算动态裁剪的会话容器。"""

from typing import List


class BudgetSession:
    """按最大 Token 预算自动淘汰最早历史消息的会话管理器。"""

    def __init__(self, max_tokens: int = 30) -> None:
        self.max_tokens = max_tokens
        self._messages: List[str] = []

    @staticmethod
    def _count(text: str) -> int:
        return max(1, len(text))

    def total_tokens(self) -> int:
        return sum(self._count(m) for m in self._messages)

    def add(self, text: str) -> None:
        self._messages.append(text)
        # 持续淘汰最早消息，但至少保留刚输入的最新一条
        while len(self._messages) > 1 and self.total_tokens() > self.max_tokens:
            self._messages.pop(0)

    def messages(self) -> List[str]:
        return list(self._messages)


if __name__ == "__main__":
    bs = BudgetSession(max_tokens=15)
    for m in ["消息一12345", "消息二12345", "消息三12345"]:
        bs.add(m)
    print("裁剪后保留:", bs.messages(), "当前总Token:", bs.total_tokens())

