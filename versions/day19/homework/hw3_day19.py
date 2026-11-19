"""
Day 19 课后作业 3（架构进阶）：高危工具人工确认拦截器（Human-in-the-Loop Gate）
工单：STARMIND-019
"""

import json
from typing import Any, Callable, Dict, Set
from src.day19_tool_registry import ToolRegistry, ToolSpec


class GuardedToolExecutor:
    """带人工二次确认（Human-in-the-Loop）的高危工具执行守卫。"""

    def __init__(self, registry: ToolRegistry, sensitive_tools: Set[str]) -> None:
        self.registry = registry
        self.sensitive_tools = sensitive_tools

    def execute_with_approval(
        self,
        name: str,
        arguments: Dict[str, Any],
        approval_cb: Callable[[str, Dict[str, Any]], bool],
    ) -> str:
        if name in self.sensitive_tools and not approval_cb(name, arguments):
            return json.dumps(
                {"status": "rejected_by_human", "tool": name, "message": "操作已被人工审核员拒绝"},
                ensure_ascii=False,
            )
        return self.registry.execute(name, arguments)


if __name__ == "__main__":
    reg = ToolRegistry()
    reg.register(
        ToolSpec(
            name="approve_refund",
            description="自动执行大额退款",
            parameters={"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
            handler=lambda order_id: {"status": "refunded", "order_id": order_id},
        )
    )
    guard = GuardedToolExecutor(reg, sensitive_tools={"approve_refund"})
    print("拒绝演示:", guard.execute_with_approval("approve_refund", {"order_id": "ORD-99"}, lambda n, a: False))
    print("批准演示:", guard.execute_with_approval("approve_refund", {"order_id": "ORD-99"}, lambda n, a: True))

