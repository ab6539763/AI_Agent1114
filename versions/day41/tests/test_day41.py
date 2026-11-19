import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 41 自动化单元测试：验证 StateGraph 引擎、可视化导出、ReAct 状态图与采购审批分支。"""

import pytest
from src.day41_state_graph import StateGraph, START, END
from src.day41_react_and_approval import build_react_graph, build_procurement_approval_graph


def test_state_graph_compile_validation_and_visualization():
    g = StateGraph()
    g.add_node("a", lambda s: {"x": 1})
    g.add_edge(START, "a")
    g.add_edge("a", END)
    app = g.compile()
    assert "graph TD" in app.draw_mermaid()
    assert "__start__ --> a" in app.draw_mermaid()
    assert "[__start__] ===> [a]" in app.draw_ascii()

    bad = StateGraph()
    bad.add_edge(START, "missing_node")
    with pytest.raises(ValueError):
        bad.compile()


def test_react_state_graph_loop():
    app = build_react_graph()
    res = app.invoke({"question": "帮我查显示器单价", "messages": [], "tool_results": []})
    assert "2200" in res["final_answer"]
    assert res["_visited_nodes"] == ["agent", "tools", "agent"]


def test_procurement_auto_approve_branch():
    called = {"human": False}

    def approver(_s):
        called["human"] = True
        return {"approved": True}

    app = build_procurement_approval_graph(human_approver=approver, auto_approve_limit=5000)
    res = app.invoke({"applicant": "小李", "item": "机械键盘", "unit_price": 650, "quantity": 2, "audit_logs": []})
    assert res["order_status"] == "ORDERED"
    assert called["human"] is False
    assert res["_visited_nodes"] == ["parse_request", "auto_approve", "execute_order"]


def test_procurement_human_approve_and_reject_branches():
    app_ok = build_procurement_approval_graph(
        human_approver=lambda _s: {"approved": True, "approver": "总监", "comment": "同意"}
    )
    res_ok = app_ok.invoke({"applicant": "阿杰", "item": "MacBook Pro", "unit_price": 14999, "quantity": 1, "audit_logs": []})
    assert res_ok["order_status"] == "ORDERED"
    assert "human_approval" in res_ok["_visited_nodes"]

    app_rej = build_procurement_approval_graph(
        human_approver=lambda _s: {"approved": False, "approver": "总监", "comment": "预算不足"}
    )
    res_rej = app_rej.invoke({"applicant": "阿杰", "item": "MacBook Pro", "unit_price": 14999, "quantity": 2, "audit_logs": []})
    assert res_rej["order_status"] == "REJECTED"
    assert res_rej["_visited_nodes"] == ["parse_request", "human_approval", "reject_notify"]

