"""
Day 61 - 模块二：星辰智脑 Supervisor 多 Agent 编排与 HITL 人工审批引擎
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.day61_mcp_and_memory import MCPToolRegistry, MCPToolSpec, SessionMemoryStore


@dataclass
class ApprovalTicket:
    ticket_id: str
    session_id: str
    tool_name: str
    tool_args: Dict[str, Any]
    status: str = "PENDING"  # PENDING | APPROVED_EXECUTED | REJECTED
    approver: str = ""
    decision_note: str = ""
    execution_result: Optional[Dict[str, Any]] = None


@dataclass
class AgentResponse:
    session_id: str
    routed_agent: str
    status: str  # COMPLETED | PENDING_APPROVAL | REJECTED
    reply: str
    ticket_id: Optional[str] = None
    trace: List[str] = field(default_factory=list)


class StarMindMultiAgent:
    """多 Agent 编排器：Supervisor -> KnowledgeAgent / ActionAgent + HITL 审批"""

    def __init__(self) -> None:
        self.registry = MCPToolRegistry()
        self.memory = SessionMemoryStore(max_recent_messages=4)
        self.tickets: Dict[str, ApprovalTicket] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.registry.register(
            MCPToolSpec(
                name="rag_search",
                description="检索星辰智脑企业制度知识库",
                required_params=["query"],
                handler=self._mock_rag_tool,
                risk_checker=lambda a: False,
            )
        )
        self.registry.register(
            MCPToolSpec(
                name="submit_expense",
                description="提交员工费用报销单（超2000元需主管人工审批）",
                required_params=["employee", "amount", "reason"],
                handler=lambda a: {
                    "expense_id": f"EXP-{uuid.uuid4().hex[:6].upper()}",
                    "employee": a["employee"],
                    "amount": float(a["amount"]),
                    "reason": a["reason"],
                    "status": "PAID_QUEUED",
                },
                risk_checker=lambda a: float(a["amount"]) > 2000.0,
            )
        )

    @staticmethod
    def _mock_rag_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        q = args["query"]
        if any(k in q for k in ("住宿", "差旅", "酒店")):
            return {"doc_id": "DOC-01", "answer": "一线城市差旅住宿上限为 650 元/晚，需附电子专票。[DOC-01]"}
        if "4291" in q or "熔断" in q:
            return {"doc_id": "DOC-02", "answer": "ERR_4291 为部门日 Token 配额硬熔断，请联系管理员提额。[DOC-02]"}
        return {"doc_id": "NONE", "answer": "知识库未命中明确条款，建议联系人工客服确认。"}

    def _route(self, user_input: str) -> str:
        if any(k in user_input for k in ("报销", "提交", "申请")):
            if re.search(r"\d+", user_input):
                return "action_agent"
        return "knowledge_agent"

    def chat(self, session_id: str, user_input: str, employee: str = "张明") -> AgentResponse:
        trace = ["supervisor:received"]
        agent = self._route(user_input)
        trace.append(f"supervisor:routed->{agent}")

        if agent == "knowledge_agent":
            res = self.registry.invoke("rag_search", {"query": user_input}, operator="knowledge_agent")
            trace.append(f"knowledge_agent:rag_search->{res['doc_id']}")
            reply = res["answer"]
            self.memory.add_turn(session_id, user_input, reply)
            return AgentResponse(session_id, agent, "COMPLETED", reply, trace=trace)

        # ActionAgent 解析金额并走风险门禁
        m = re.search(r"(\d+(?:\.\d+)?)", user_input)
        amount = float(m.group(1)) if m else 0.0
        tool_args = {"employee": employee, "amount": amount, "reason": user_input}
        high_risk = self.registry.validate_and_check_risk("submit_expense", tool_args)

        if high_risk:
            tid = f"APR-{uuid.uuid4().hex[:6].upper()}"
            self.tickets[tid] = ApprovalTicket(
                ticket_id=tid,
                session_id=session_id,
                tool_name="submit_expense",
                tool_args=tool_args,
            )
            trace.append(f"action_agent:hitl_paused->{tid}")
            reply = f"报销金额 {amount:.2f} 元超过自动审批上限(2000元)，已挂起等待主管审批，审批单号：{tid}。"
            self.memory.add_turn(session_id, user_input, reply)
            return AgentResponse(session_id, agent, "PENDING_APPROVAL", reply, ticket_id=tid, trace=trace)

        exec_res = self.registry.invoke("submit_expense", tool_args, operator="action_agent")
        trace.append(f"action_agent:auto_executed->{exec_res['expense_id']}")
        reply = f"报销单已自动提交成功！单号：{exec_res['expense_id']}，金额：{amount:.2f} 元。"
        self.memory.add_turn(session_id, user_input, reply)
        return AgentResponse(session_id, agent, "COMPLETED", reply, trace=trace)

    def resolve_approval(self, ticket_id: str, approve: bool, approver: str, note: str = "") -> ApprovalTicket:
        if ticket_id not in self.tickets:
            raise KeyError(f"审批单不存在: {ticket_id}")
        ticket = self.tickets[ticket_id]
        if ticket.status != "PENDING":
            raise RuntimeError(f"审批单 {ticket_id} 已处于终态 {ticket.status}，禁止重复审批")

        ticket.approver = approver
        ticket.decision_note = note
        if not approve:
            ticket.status = "REJECTED"
            self.memory.add_turn(ticket.session_id, f"[审批通知]{ticket_id}", f"主管 {approver} 已驳回：{note}")
            return ticket

        ticket.execution_result = self.registry.invoke(
            ticket.tool_name, ticket.tool_args, operator=f"hitl_approved_by:{approver}"
        )
        ticket.status = "APPROVED_EXECUTED"
        self.memory.add_turn(
            ticket.session_id,
            f"[审批通知]{ticket_id}",
            f"主管 {approver} 已批准并完成执行：{ticket.execution_result['expense_id']}",
        )
        return ticket


if __name__ == "__main__":
    engine = StarMindMultiAgent()
    r1 = engine.chat("sess-01", "请问北京出差住宿报销标准是多少？")
    r2 = engine.chat("sess-01", "帮我提交差旅报销 800 元")
    r3 = engine.chat("sess-01", "帮我提交服务器采购报销 4500 元")
    print("知识问答:", r1.routed_agent, r1.status, r1.reply)
    print("低危自动:", r2.routed_agent, r2.status, r2.reply)
    print("高危挂起:", r3.routed_agent, r3.status, r3.ticket_id)
    if r3.ticket_id:
        done = engine.resolve_approval(r3.ticket_id, approve=True, approver="林总监", note="同意采购")
        print("审批恢复:", done.status, done.execution_result)

