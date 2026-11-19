"""Day 48 - 步骤二：多 Agent 智能办公助手三大领域专家 Agent。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from src.day48_office_tools import EnterpriseOfficeToolkit, OfficeWorkspaceStore, ToolResult


@dataclass
class AgentResponse:
    agent_name: str
    summary: str
    requires_human_confirmation: bool
    tool_results: List[ToolResult]


class KnowledgeAgent:
    """知识检索专员：仅拥有只读权限（doc_rag_tool + web_search_tool）。"""

    name = "knowledge_agent"
    allowed_tools = ["doc_rag_tool", "web_search_tool"]

    def __init__(self, toolkit: EnterpriseOfficeToolkit) -> None:
        self.toolkit = toolkit

    def handle(self, query: str, params: Dict[str, Any] | None = None) -> AgentResponse:
        results: List[ToolResult] = []
        if any(k in query for k in ("行业", "趋势", "资讯", "白皮书", "新闻")):
            r = self.toolkit.web_search_tool(query)
            results.append(r)
            snippets = [x["snippet"] for x in r.data.get("results", [])]
            summary = "；".join(snippets) or "未检索到相关行业资讯。"
        else:
            r = self.toolkit.doc_rag_tool(query)
            results.append(r)
            docs = r.data.get("docs", [])
            summary = "；".join(f"《{d['title']}》:{d['content']}" for d in docs) or "未检索到相关内部制度。"
        return AgentResponse(self.name, summary, False, results)


class SchedulerAgent:
    """日程与邮件专员：绑定 calendar_tool 与 email_draft_tool。"""

    name = "scheduler_agent"
    allowed_tools = ["calendar_tool", "email_draft_tool"]

    def __init__(self, toolkit: EnterpriseOfficeToolkit) -> None:
        self.toolkit = toolkit

    def handle(self, query: str, params: Dict[str, Any] | None = None) -> AgentResponse:
        p = params or {}
        if "邮件" in query or "email" in query.lower():
            res = self.toolkit.email_draft_tool(
                to_email=p.get("to_email", "client@example.com"),
                subject=p.get("subject", "星辰数科项目同步"),
                body=p.get("body", query),
                actor=p.get("actor", "employee"),
            )
            return AgentResponse(
                self.name,
                res.message,
                requires_human_confirmation=(res.ok and res.risk_level == "HIGH_RISK"),
                tool_results=[res],
            )

        res = self.toolkit.calendar_tool(
            title=p.get("title", "项目沟通会"),
            date=p.get("date", "2026-11-20"),
            start_hour=int(p.get("start_hour", 14)),
            end_hour=int(p.get("end_hour", 15)),
            attendees=list(p.get("attendees", ["老陈", "林产品"])),
            actor=p.get("actor", "employee"),
        )
        return AgentResponse(self.name, res.message, False, [res])


class ApprovalAgent:
    """审批流程专员：绑定 approval_tool，大额报销/长假自动要求人工确认。"""

    name = "approval_agent"
    allowed_tools = ["approval_tool"]

    def __init__(self, toolkit: EnterpriseOfficeToolkit) -> None:
        self.toolkit = toolkit

    def handle(self, query: str, params: Dict[str, Any] | None = None) -> AgentResponse:
        p = params or {}
        app_type = p.get("approval_type", "leave" if "请假" in query or "年假" in query else "expense")
        value = float(p.get("value", 1000.0 if app_type == "expense" else 1.0))
        res = self.toolkit.approval_tool(
            approval_type=app_type,
            applicant=p.get("actor", "employee"),
            amount_or_days=value,
            reason=p.get("reason", query),
        )
        return AgentResponse(
            self.name,
            res.message,
            requires_human_confirmation=(res.ok and res.risk_level == "HIGH_RISK"),
            tool_results=[res],
        )


if __name__ == "__main__":
    store = OfficeWorkspaceStore()
    kit = EnterpriseOfficeToolkit(store)
    ka = KnowledgeAgent(kit)
    sa = SchedulerAgent(kit)
    aa = ApprovalAgent(kit)

    print("知识专员:", ka.handle("差旅报销制度"))
    print("日程专员:", sa.handle("帮我发邮件给客户", {"to_email": "boss@partner.cn", "subject": "报价确认"}))
    print("审批专员:", aa.handle("提交 8000 元差旅报销", {"approval_type": "expense", "value": 8000.0}))

