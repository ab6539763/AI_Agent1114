"""
Day 25 课后作业 3（架构进阶）：作业三：带敏感词脱敏与成本熔断的安全 ChatModel 装饰器
工单：STARMIND-025
"""

"""Day 25 作业三参考答案：敏感词脱敏与 Token 预算熔断装饰器"""
import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import AIMessage, BaseChatModel, BaseMessage, HumanMessage, StarMindChatModel


class GuardedChatModel(BaseChatModel):
    PHONE_PATTERN = re.compile(r"(1[3-9]\d)\d{4}(\d{4})")

    def __init__(self, inner: BaseChatModel, token_budget: int = 500) -> None:
        super().__init__(model_name=f"guarded:{inner.model_name}", temperature=inner.temperature)
        self.inner = inner
        self.token_budget = token_budget
        self.used_tokens = 0

    def _mask_pii(self, text: str) -> str:
        return self.PHONE_PATTERN.sub(r"\1****\2", text)

    def _generate(self, messages: List[BaseMessage]) -> str:
        # 不直接走 _generate，重写 invoke 以复用 inner 的真实统计
        raise NotImplementedError

    def invoke(self, input_data) -> AIMessage:
        if self.used_tokens >= self.token_budget:
            raise RuntimeError(f"Token 预算已耗尽 ({self.used_tokens}/{self.token_budget})，触发熔断！")

        messages = self._normalize_input(input_data)
        sanitized = [
            type(m)(content=self._mask_pii(m.content)) if isinstance(m, HumanMessage) else m
            for m in messages
        ]
        resp = self.inner.invoke(sanitized)
        self.used_tokens += resp.usage_metadata.get("total_tokens", 0)
        resp.response_metadata["pii_masked"] = True
        resp.response_metadata["remaining_budget"] = max(0, self.token_budget - self.used_tokens)
        return resp


if __name__ == "__main__":
    safe_llm = GuardedChatModel(StarMindChatModel(), token_budget=200)
    r = safe_llm.invoke("我手机是13812345678，VPN连不上了")
    print("脱敏后回复:", r.content)
    print("剩余预算:", r.response_metadata["remaining_budget"])
    assert "13812345678" not in r.content

