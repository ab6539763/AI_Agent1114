"""Day 43 - 步骤二：星辰行业研究多 Agent 团队（搜索员 + 分析师 + 撰写员）。"""

from __future__ import annotations

from typing import Any, Dict, List

from src.day43_multi_agent_patterns import (
    FINISH,
    MultiAgentResult,
    RouteDecision,
    SupervisorOrchestrator,
)

# 本地模拟企业行业情报库（保证 100% 离线确定性运行）
MOCK_INDUSTRY_DB: Dict[str, List[Dict[str, Any]]] = {
    "企业级Agent": [
        {"source": "2025中国AI应用白皮书", "metric": "市场规模(亿元)", "y2024": 180.0, "y2025": 315.0},
        {"source": "星辰客户调研库", "metric": "头部企业落地率(%)", "y2024": 22.0, "y2025": 48.0},
        {"source": "运维成本报告", "metric": "平均人效提升(%)", "y2024": 18.0, "y2025": 36.0},
    ],
    "工业视觉": [
        {"source": "智能制造年鉴", "metric": "市场规模(亿元)", "y2024": 120.0, "y2025": 156.0},
        {"source": "产线质检基准", "metric": "缺陷漏检率下降(%)", "y2024": 25.0, "y2025": 40.0},
    ],
}


class ResearcherAgent:
    """搜索员：只拥有情报检索权限，负责收集带出处的结构化事实。"""

    name = "researcher"
    role_desc = "行业情报搜索员，负责检索权威数据与来源"
    allowed_tools = ["industry_search"]

    def run(self, state: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
        topic = state["topic"]
        records = MOCK_INDUSTRY_DB.get(
            topic,
            [{"source": "公开研报库", "metric": "行业指数", "y2024": 100.0, "y2025": 125.0}],
        )
        return {"facts": records, "fact_count": len(records)}


class AnalystAgent:
    """分析师：不触网，仅基于黑板上的 facts 进行同比增速与关键洞察测算。"""

    name = "analyst"
    role_desc = "量化数据分析师，负责计算同比增速并提炼核心趋势"
    allowed_tools = ["metric_calculator"]

    def run(self, state: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
        facts = state.get("facts", [])
        insights: List[Dict[str, Any]] = []
        for item in facts:
            base = item["y2024"]
            curr = item["y2025"]
            yoy_pct = round(((curr - base) / base) * 100.0, 2) if base else 0.0
            insights.append(
                {
                    "metric": item["metric"],
                    "source": item["source"],
                    "y2024": base,
                    "y2025": curr,
                    "yoy_growth_pct": yoy_pct,
                }
            )
        avg_growth = round(sum(x["yoy_growth_pct"] for x in insights) / max(len(insights), 1), 2)
        return {
            "analysis": {
                "metrics": insights,
                "avg_yoy_growth_pct": avg_growth,
                "verdict": "高速扩张期" if avg_growth >= 50.0 else "稳健增长期",
            }
        }


class WriterAgent:
    """撰写员：基于分析师结论撰写研报，并响应主管的质检打回意见定向修订。"""

    name = "writer"
    role_desc = "资深行业研报撰写员，负责结构化公文排版与修订"
    allowed_tools = ["markdown_formatter"]

    def run(self, state: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
        topic = state["topic"]
        analysis = state["analysis"]
        revisions = int(state.get("writer_revisions", 0)) + 1

        lines = [
            f"# 《{topic}》行业深度研究报告",
            "",
            f"## 一、核心结论（阶段判定：{analysis['verdict']}）",
            f"综合各核心维度测算，该赛道平均同比增速达到 **{analysis['avg_yoy_growth_pct']}%**。",
            "",
            "## 二、关键量化指标",
        ]
        for m in analysis["metrics"]:
            lines.append(
                f"- {m['metric']}：2024年 {m['y2024']} -> 2025年 {m['y2025']}（同比 +{m['yoy_growth_pct']}%，来源：{m['source']}）"
            )

        # 演示真实质检闭环：首版未包含风险提示，待主管打回并给出 feedback 后补齐
        if "风险提示" in feedback or revisions >= 2:
            lines.extend(
                [
                    "",
                    "## 三、风险提示与落地建议",
                    "- 需重点防范模型幻觉引发的合规风险，建议引入 Human-in-the-loop 审批护栏。",
                    "- 建议优先从高 ROI 内部提效场景切入，控制 Token 推理成本。",
                ]
            )

        return {"draft": "\n".join(lines), "writer_revisions": revisions}


def research_supervisor_router(state: Dict[str, Any], _workers: List[str]) -> RouteDecision:
    """主管路由决策函数：按 情报 -> 分析 -> 撰写 -> 质检验收 的状态推进。"""
    if not state.get("facts"):
        return RouteDecision(next_agent="researcher", reason="缺少行业原始情报，派发搜索员")
    if not state.get("analysis"):
        return RouteDecision(next_agent="analyst", reason="已有原始事实，派发分析师测算同比增速")
    draft = state.get("draft", "")
    if not draft:
        return RouteDecision(next_agent="writer", reason="量化分析完成，派发撰写员起草初稿")
    if "风险提示" not in draft:
        return RouteDecision(
            next_agent="writer",
            reason="质检未通过：研报缺少合规与风险提示章节，打回重写",
            feedback="请补充「风险提示」章节，说明模型幻觉与成本控制建议。",
        )
    return RouteDecision(next_agent=FINISH, reason="研报数据完整且通过风险提示质检，准予发布")


def build_research_team(max_rounds: int = 8) -> SupervisorOrchestrator:
    orch = SupervisorOrchestrator(router_fn=research_supervisor_router, max_rounds=max_rounds)
    orch.register_worker(ResearcherAgent())
    orch.register_worker(AnalystAgent())
    orch.register_worker(WriterAgent())
    return orch


if __name__ == "__main__":
    team = build_research_team()
    result: MultiAgentResult = team.invoke({"topic": "企业级Agent"})
    print(f"协作完成: {result.completed} | 总调度轮次: {result.rounds}")
    for step in result.routing_history:
        print(f"  Round {step['round']}: -> {step['next_agent']} ({step['reason']})")
    print("\n" + result.final_state["draft"])

