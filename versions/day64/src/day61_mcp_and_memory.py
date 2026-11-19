"""
Day 61 - 模块一：MCP 风格标准化工具注册中心 + 多轮会话滑动窗口记忆
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class MCPToolSpec:
    name: str
    description: str
    required_params: List[str]
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    risk_checker: Callable[[Dict[str, Any]], bool] = lambda args: False


class MCPToolRegistry:
    """统一管理企业 MCP 工具的注册、参数校验、风险评估与审计执行"""

    def __init__(self) -> None:
        self._tools: Dict[str, MCPToolSpec] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def register(self, spec: MCPToolSpec) -> None:
        self._tools[spec.name] = spec

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "required_params": list(t.required_params),
            }
            for t in self._tools.values()
        ]

    def validate_and_check_risk(self, name: str, args: Dict[str, Any]) -> bool:
        if name not in self._tools:
            raise KeyError(f"未注册的 MCP 工具: {name}")
        spec = self._tools[name]
        missing = [p for p in spec.required_params if p not in args or args[p] in (None, "")]
        if missing:
            raise ValueError(f"工具 {name} 缺少必填参数: {missing}")
        return bool(spec.risk_checker(args))

    def invoke(self, name: str, args: Dict[str, Any], operator: str = "agent") -> Dict[str, Any]:
        self.validate_and_check_risk(name, args)
        result = self._tools[name].handler(args)
        self.audit_log.append(
            {"tool": name, "args": dict(args), "operator": operator, "result": result}
        )
        return result


@dataclass
class MemorySession:
    session_id: str
    max_recent_messages: int = 4
    summary: str = ""
    messages: List[Dict[str, str]] = field(default_factory=list)


class SessionMemoryStore:
    """多轮对话记忆管理：保留最近窗口 + 超窗历史自动折叠为摘要"""

    def __init__(self, max_recent_messages: int = 4) -> None:
        self.max_recent_messages = max_recent_messages
        self._sessions: Dict[str, MemorySession] = {}

    def _get(self, session_id: str) -> MemorySession:
        if session_id not in self._sessions:
            self._sessions[session_id] = MemorySession(
                session_id=session_id,
                max_recent_messages=self.max_recent_messages,
            )
        return self._sessions[session_id]

    def add_turn(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        sess = self._get(session_id)
        sess.messages.append({"role": "user", "content": user_msg})
        sess.messages.append({"role": "assistant", "content": assistant_msg})
        if len(sess.messages) > sess.max_recent_messages:
            overflow = sess.messages[:-sess.max_recent_messages]
            sess.messages = sess.messages[-sess.max_recent_messages:]
            folded = " | ".join(f"{m['role']}:{m['content'][:30]}" for m in overflow)
            sess.summary = f"{sess.summary}; {folded}".strip("; ")

    def get_context(self, session_id: str) -> Dict[str, Any]:
        sess = self._get(session_id)
        return {
            "session_id": sess.session_id,
            "summary": sess.summary,
            "recent_messages": list(sess.messages),
        }


if __name__ == "__main__":
    reg = MCPToolRegistry()
    reg.register(
        MCPToolSpec(
            name="submit_expense",
            description="提交差旅费用报销单",
            required_params=["employee", "amount", "reason"],
            handler=lambda a: {"expense_id": "EXP-2026-001", "status": "SUBMITTED", "amount": a["amount"]},
            risk_checker=lambda a: float(a["amount"]) > 2000.0,
        )
    )
    print("工具列表:", reg.list_tools())
    print("3500元是否高危:", reg.validate_and_check_risk("submit_expense", {"employee": "小王", "amount": 3500, "reason": "上海出差"}))
    mem = SessionMemoryStore(max_recent_messages=2)
    mem.add_turn("s1", "查一下住宿标准", "一线城市650元/晚")
    mem.add_turn("s1", "帮我报销1200元", "已自动提交报销单")
    print("记忆上下文:", mem.get_context("s1"))

