import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 61 单元测试：多 Agent 路由、MCP 工具审计、多轮记忆与 HITL 审批"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day61_multi_agent_hitl import StarMindMultiAgent


def test_knowledge_agent_routing():
    app = StarMindMultiAgent()
    res = app.chat("s1", "出差住宿标准是多少？")
    assert res.routed_agent == "knowledge_agent"
    assert res.status == "COMPLETED"
    assert "[DOC-01]" in res.reply


def test_low_risk_action_auto_executes():
    app = StarMindMultiAgent()
    res = app.chat("s2", "帮我报销打车费 350 元")
    assert res.routed_agent == "action_agent"
    assert res.status == "COMPLETED"
    assert len(app.registry.audit_log) == 1


def test_high_risk_action_hitl_approve_and_idempotency():
    app = StarMindMultiAgent()
    res = app.chat("s3", "帮我提交差旅报销 3800 元")
    assert res.status == "PENDING_APPROVAL"
    assert res.ticket_id is not None
    # 挂起期间工具尚未真正执行
    assert len(app.registry.audit_log) == 0

    done = app.resolve_approval(res.ticket_id, approve=True, approver="陈经理", note="核对发票无误")
    assert done.status == "APPROVED_EXECUTED"
    assert done.execution_result is not None
    assert len(app.registry.audit_log) == 1

    # 二次审批必须拦截，防止重复打款
    with pytest.raises(RuntimeError):
        app.resolve_approval(res.ticket_id, approve=True, approver="陈经理")


def test_high_risk_action_reject_and_memory_window():
    app = StarMindMultiAgent()
    app.chat("s4", "住宿标准")
    app.chat("s4", "报错 4291 怎么办")
    res = app.chat("s4", "申请报销 5000 元")
    rejected = app.resolve_approval(res.ticket_id, approve=False, approver="陈经理", note="缺少发票")
    assert rejected.status == "REJECTED"
    ctx = app.memory.get_context("s4")
    assert len(ctx["recent_messages"]) == 4
    assert ctx["summary"] != ""

