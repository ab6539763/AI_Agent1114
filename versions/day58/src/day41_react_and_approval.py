"""Day 41 - 步骤二：基于 StateGraph 的 ReAct 循环图与企业采购审批工作流。"""

from __future__ import annotations

import operator
from typing import Any, Callable, Dict

try:
    from src.day41_state_graph import CompiledGraph, END, START, StateGraph
except ImportError:
    from day41_state_graph import CompiledGraph, END, START, StateGraph


# =========================================================================
# 场景一：用 StateGraph 重写 ReAct Agent (agent <-> tools 循环图)
# =========================================================================

def build_react_graph() -> CompiledGraph:
    """构建标准 LangGraph 风格的 ReAct 状态图。"""
    inventory_db = {"MacBook Pro": 14999, "显示器": 2200, "机械键盘": 650}

    def agent_node(state: Dict[str, Any]) -> Dict[str, Any]:
        question = state["question"]
        tool_results = state.get("tool_results", [])
        # 如果还没查过价格，先发出工具调用指令
        if not tool_results:
            for item_name in inventory_db:
                if item_name in question:
                    return {
                        "pending_tool": {"name": "query_price", "arg": item_name},
                        "messages": [f"Agent思考: 需要查询 {item_name} 的采购单价"],
                    }
            return {
                "pending_tool": None,
                "final_answer": "未识别到库存目录中的设备名称。",
                "messages": ["Agent思考: 无需工具，直接回复"],
            }

        # 已拿到工具结果，汇总得出最终答案
        latest = tool_results[-1]
        return {
            "pending_tool": None,
            "final_answer": f"查询完成：{latest}。如需提交采购申请请告知数量。",
            "messages": ["Agent思考: 已获得价格信息，生成最终答复"],
        }

    def tools_node(state: Dict[str, Any]) -> Dict[str, Any]:
        call = state["pending_tool"]
        item_name = call["arg"]
        price = inventory_db.get(item_name, -1)
        result_str = f"{item_name} 企业协议采购价为 {price} 元"
        return {
            "tool_results": [result_str],
            "messages": [f"Tools执行: query_price({item_name}) -> {result_str}"],
        }

    def should_continue(state: Dict[str, Any]) -> str:
        return "tools" if state.get("pending_tool") else "end"

    graph = StateGraph(reducers={"messages": operator.add, "tool_results": operator.add})
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()


# =========================================================================
# 场景二：带人工审批节点的企业 IT 采购工作流
# =========================================================================

def build_procurement_approval_graph(
    human_approver: Callable[[Dict[str, Any]], Dict[str, Any]],
    auto_approve_limit: float = 5000.0,
) -> CompiledGraph:
    """
    企业采购审批状态图：
    - 金额 <= auto_approve_limit：自动放行 -> 创建采购单
    - 金额 > auto_approve_limit：强制路由至人工审批节点 -> 通过则下单，驳回则通知
    """

    def parse_request(state: Dict[str, Any]) -> Dict[str, Any]:
        total = float(state["unit_price"]) * int(state["quantity"])
        return {
            "total_amount": total,
            "audit_logs": [f"解析申请: {state['applicant']} 申请采购 {state['item']} x{state['quantity']}，总价 {total:.2f} 元"],
        }

    def route_by_amount(state: Dict[str, Any]) -> str:
        return "need_human" if state["total_amount"] > auto_approve_limit else "auto"

    def auto_approve(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "approved": True,
            "approver": "SystemAutoRule",
            "audit_logs": [f"金额未超 {auto_approve_limit} 元红线，系统自动审批通过"],
        }

    def human_approval(state: Dict[str, Any]) -> Dict[str, Any]:
        decision = human_approver(state)
        approved = bool(decision.get("approved", False))
        comment = decision.get("comment", "")
        approver = decision.get("approver", "财务总监")
        return {
            "approved": approved,
            "approver": approver,
            "approval_comment": comment,
            "audit_logs": [f"人工审批({approver}): {'通过' if approved else '驳回'} - {comment}"],
        }

    def route_after_human(state: Dict[str, Any]) -> str:
        return "approved" if state.get("approved") else "rejected"

    def execute_order(state: Dict[str, Any]) -> Dict[str, Any]:
        po_id = f"PO-2026-{abs(hash(state['item'])) % 10000:04d}"
        return {
            "order_status": "ORDERED",
            "po_id": po_id,
            "audit_logs": [f"已调用 ERP 创建采购单 {po_id}"],
        }

    def reject_notify(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "order_status": "REJECTED",
            "audit_logs": [f"已向 {state['applicant']} 发送驳回通知：{state.get('approval_comment', '无')}"],
        }

    g = StateGraph(reducers={"audit_logs": operator.add})
    g.add_node("parse_request", parse_request)
    g.add_node("auto_approve", auto_approve)
    g.add_node("human_approval", human_approval)
    g.add_node("execute_order", execute_order)
    g.add_node("reject_notify", reject_notify)

    g.add_edge(START, "parse_request")
    g.add_conditional_edges(
        "parse_request",
        route_by_amount,
        {"auto": "auto_approve", "need_human": "human_approval"},
    )
    g.add_edge("auto_approve", "execute_order")
    g.add_conditional_edges(
        "human_approval",
        route_after_human,
        {"approved": "execute_order", "rejected": "reject_notify"},
    )
    g.add_edge("execute_order", END)
    g.add_edge("reject_notify", END)
    return g.compile()


if __name__ == "__main__":
    react_app = build_react_graph()
    print("=== ReAct Mermaid 拓扑 ===")
    print(react_app.draw_mermaid())
    r = react_app.invoke({"question": "查一下 MacBook Pro 采购价", "messages": [], "tool_results": []})
    print("ReAct 结果:", r["final_answer"], "| 经过节点:", r["_visited_nodes"])

    approval_app = build_procurement_approval_graph(
        human_approver=lambda s: {"approved": True, "approver": "王总监", "comment": "项目急需，同意采购"}
    )
    p = approval_app.invoke(
        {"applicant": "阿杰", "item": "MacBook Pro", "unit_price": 14999, "quantity": 1, "audit_logs": []}
    )
    print("采购审批状态:", p["order_status"], "| 经过节点:", p["_visited_nodes"])

