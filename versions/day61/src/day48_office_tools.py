"""Day 48 - 步骤一：阶段项目三 5 大企业办公工具集与统一工作区底座。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


@dataclass
class ToolResult:
    ok: bool
    tool_name: str
    risk_level: str  # "LOW" | "HIGH_RISK"
    data: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


class OfficeWorkspaceStore:
    """可隔离的企业办公内存工作区（日程/邮件草稿/知识文档/外部资讯/审批单）。"""

    def __init__(self) -> None:
        self.meetings: List[Dict[str, Any]] = [
            {
                "meeting_id": "MTG-001",
                "title": "星辰智脑架构周会",
                "date": "2026-11-20",
                "start_hour": 10,
                "end_hour": 11,
                "attendees": ["老陈", "阿杰", "林产品"],
            }
        ]
        self.email_drafts: Dict[str, Dict[str, Any]] = {}
        self.approvals: Dict[str, Dict[str, Any]] = {}
        self.audit_logs: List[Dict[str, Any]] = []
        self.internal_docs: List[Dict[str, str]] = [
            {
                "doc_id": "DOC-TRAVEL-2026",
                "title": "2026年星辰数科差旅报销管理制度",
                "content": "一线城市住宿上限 600 元/晚，餐补 120 元/天；单笔报销超过 5000 元须经部门总监人工复核。",
            },
            {
                "doc_id": "DOC-LEAVE-2026",
                "title": "员工年假与病假审批规范",
                "content": "年假 3 天及以内由直属主管审批，超过 3 天须部门负责人审批；需提前至少 1 个工作日提交 OA 审批单。",
            },
            {
                "doc_id": "DOC-SECURITY-2026",
                "title": "AI 办公助手数据安全红线",
                "content": "禁止对外发邮件中包含未脱敏客户手机号与内部密钥；高危写操作必须经过 Human-in-the-loop 人工确认。",
            },
        ]
        self.web_news: List[Dict[str, str]] = [
            {
                "title": "2026 企业级多 Agent 协同落地白皮书发布",
                "snippet": "报告指出采用 LangGraph 状态机与 MCP 协议的企业，AI 办公自动化交付周期缩短 45%。",
            },
            {
                "title": "金融与政企加速推进 Text-to-SQL 只读安全问数",
                "snippet": "双重只读防护与语义指标宽表成为企业智能问数标配架构。",
            },
        ]

    def log_audit(self, tool_name: str, actor: str, status: str, detail: str) -> None:
        self.audit_logs.append(
            {"tool": tool_name, "actor": actor, "status": status, "detail": detail}
        )


class EnterpriseOfficeToolkit:
    """封装 5 大企业办公工具：日程、邮件草拟、资讯搜索、文档 RAG、审批单。"""

    def __init__(self, store: OfficeWorkspaceStore) -> None:
        self.store = store

    # 工具 1：日程冲突检测与会议预定
    def calendar_tool(
        self,
        title: str,
        date: str,
        start_hour: int,
        end_hour: int,
        attendees: List[str],
        actor: str = "employee",
    ) -> ToolResult:
        if start_hour >= end_hour or not (0 <= start_hour <= 23 and 1 <= end_hour <= 24):
            self.store.log_audit("calendar_tool", actor, "REJECTED", "非法会议时段")
            return ToolResult(False, "calendar_tool", "LOW", {}, "会议起止时间不合法，要求 start_hour < end_hour")

        for m in self.store.meetings:
            if m["date"] == date and (start_hour < m["end_hour"] and m["start_hour"] < end_hour):
                self.store.log_audit("calendar_tool", actor, "CONFLICT", f"与 {m['meeting_id']} 冲突")
                return ToolResult(
                    False,
                    "calendar_tool",
                    "LOW",
                    {"conflict_with": m},
                    f"日程冲突：{date} {start_hour}:00-{end_hour}:00 与《{m['title']}》({m['start_hour']}:00-{m['end_hour']}:00) 重叠",
                )

        mtg_id = f"MTG-{len(self.store.meetings) + 1:03d}"
        record = {
            "meeting_id": mtg_id,
            "title": title,
            "date": date,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "attendees": attendees,
        }
        self.store.meetings.append(record)
        self.store.log_audit("calendar_tool", actor, "OK", f"已预定 {mtg_id}")
        return ToolResult(True, "calendar_tool", "LOW", record, f"会议《{title}》预定成功（编号 {mtg_id}）")

    # 工具 2：邮件草拟与收件人校验（标记为 HIGH_RISK，需人工确认外发）
    def email_draft_tool(
        self,
        to_email: str,
        subject: str,
        body: str,
        actor: str = "employee",
    ) -> ToolResult:
        if not EMAIL_RE.match(to_email.strip()):
            self.store.log_audit("email_draft_tool", actor, "REJECTED", f"非法邮箱 {to_email}")
            return ToolResult(False, "email_draft_tool", "HIGH_RISK", {}, f"收件人邮箱格式非法: {to_email}")

        draft_id = f"MAIL-{len(self.store.email_drafts) + 1:03d}"
        draft = {
            "draft_id": draft_id,
            "to": to_email.strip(),
            "subject": subject.strip(),
            "body": body.strip(),
            "status": "PENDING_CONFIRMATION",
        }
        self.store.email_drafts[draft_id] = draft
        self.store.log_audit("email_draft_tool", actor, "DRAFTED", f"草稿 {draft_id} 待人工确认")
        return ToolResult(
            True,
            "email_draft_tool",
            "HIGH_RISK",
            draft,
            f"已生成待确认邮件草稿 {draft_id}（收件人: {draft['to']}），等待人工确认后外发",
        )

    # 工具 3：行业资讯模拟网络搜索
    def web_search_tool(self, query: str, actor: str = "employee") -> ToolResult:
        q_chars = {c for c in query.lower() if c.strip()}
        hits = []
        for item in self.store.web_news:
            text = (item["title"] + item["snippet"]).lower()
            score = sum(1 for c in q_chars if c in text)
            if score > 0:
                hits.append((score, item))
        hits.sort(key=lambda x: x[0], reverse=True)
        matched = [x[1] for x in hits[:2]]
        self.store.log_audit("web_search_tool", actor, "OK", f"命中 {len(matched)} 条资讯")
        return ToolResult(True, "web_search_tool", "LOW", {"results": matched}, f"检索到 {len(matched)} 条行业资讯")

    # 工具 4：内部企业文档 RAG 检索
    def doc_rag_tool(self, query: str, actor: str = "employee") -> ToolResult:
        q_chars = {c for c in query.lower() if c.strip()}
        scored = []
        for doc in self.store.internal_docs:
            text = (doc["title"] + doc["content"]).lower()
            overlap = sum(1 for c in q_chars if c in text)
            if overlap > 0:
                scored.append((overlap, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        top_docs = [x[1] for x in scored[:2]]
        self.store.log_audit("doc_rag_tool", actor, "OK", f"召回 {len(top_docs)} 篇制度文档")
        return ToolResult(True, "doc_rag_tool", "LOW", {"docs": top_docs}, f"召回 {len(top_docs)} 篇企业制度文档")

    # 工具 5：费用/请假审批单创建
    def approval_tool(
        self,
        approval_type: str,  # "expense" | "leave"
        applicant: str,
        amount_or_days: float,
        reason: str,
    ) -> ToolResult:
        if approval_type not in ("expense", "leave") or amount_or_days <= 0:
            return ToolResult(False, "approval_tool", "HIGH_RISK", {}, "审批类型必须为 expense/leave 且数值大于 0")

        is_high_risk = (approval_type == "expense" and amount_or_days > 5000) or (
            approval_type == "leave" and amount_or_days > 3
        )
        risk = "HIGH_RISK" if is_high_risk else "LOW"
        app_id = f"OA-{len(self.store.approvals) + 1:03d}"
        record = {
            "approval_id": app_id,
            "type": approval_type,
            "applicant": applicant,
            "value": amount_or_days,
            "reason": reason,
            "status": "PENDING_HUMAN_APPROVAL" if is_high_risk else "AUTO_SUBMITTED",
        }
        self.store.approvals[app_id] = record
        self.store.log_audit("approval_tool", applicant, record["status"], f"{app_id} ({risk})")
        return ToolResult(
            True,
            "approval_tool",
            risk,
            record,
            f"审批单 {app_id} 已创建（风险等级: {risk}，状态: {record['status']}）",
        )


if __name__ == "__main__":
    store = OfficeWorkspaceStore()
    kit = EnterpriseOfficeToolkit(store)
    print(kit.doc_rag_tool("差旅住宿报销标准"))
    print(kit.calendar_tool("项目三评审", "2026-11-20", 14, 15, ["老陈", "林产品"]))
    print(kit.email_draft_tool("partner@client.com", "合作方案确认", "您好，附件为星辰智脑方案。"))
    print(kit.approval_tool("expense", "阿杰", 6800.0, "华东客户现场实施差旅费"))

