import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 48 自动化单元测试：验证 5 大企业办公工具边界与三大领域专家 Agent。"""

from src.day48_office_tools import EnterpriseOfficeToolkit, OfficeWorkspaceStore
from src.day48_office_agents import ApprovalAgent, KnowledgeAgent, SchedulerAgent


def test_five_office_tools_and_boundaries():
    store = OfficeWorkspaceStore()
    kit = EnterpriseOfficeToolkit(store)

    # 1. 日程冲突拦截与空闲预定
    conflict = kit.calendar_tool("冲突会议", "2026-11-20", 10, 11, ["老陈"])
    assert conflict.ok is False and "冲突" in conflict.message
    ok_mtg = kit.calendar_tool("相邻会议", "2026-11-20", 11, 12, ["老陈"])
    assert ok_mtg.ok is True and ok_mtg.data["meeting_id"] == "MTG-002"

    # 2. 邮件格式拦截与高危草稿
    bad_mail = kit.email_draft_tool("invalid-email", "标题", "正文")
    assert bad_mail.ok is False
    ok_mail = kit.email_draft_tool("cto@partner.com", "合作方案", "请查收")
    assert ok_mail.ok is True and ok_mail.risk_level == "HIGH_RISK"

    # 3. 资讯搜索与文档 RAG
    news = kit.web_search_tool("MCP 协议多 Agent")
    assert news.ok is True and len(news.data["results"]) >= 1
    docs = kit.doc_rag_tool("差旅住宿报销")
    assert docs.ok is True and "600 元/晚" in docs.data["docs"][0]["content"]

    # 4. 审批单风险分级
    small_exp = kit.approval_tool("expense", "阿杰", 800.0, "打车费")
    assert small_exp.risk_level == "LOW"
    big_exp = kit.approval_tool("expense", "阿杰", 6500.0, "服务器采购")
    assert big_exp.risk_level == "HIGH_RISK"
    assert len(store.audit_logs) >= 6


def test_three_specialist_office_agents():
    store = OfficeWorkspaceStore()
    kit = EnterpriseOfficeToolkit(store)

    k_resp = KnowledgeAgent(kit).handle("员工年假规范")
    assert k_resp.requires_human_confirmation is False
    assert "3 天" in k_resp.summary

    s_resp = SchedulerAgent(kit).handle("发邮件通知客户", {"to_email": "ops@client.com", "subject": "周报"})
    assert s_resp.requires_human_confirmation is True

    a_resp = ApprovalAgent(kit).handle("申请 5 天年假", {"approval_type": "leave", "value": 5})
    assert a_resp.requires_human_confirmation is True

