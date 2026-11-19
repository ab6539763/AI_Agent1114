"""
Day 58 - 模块二：星辰智脑 v1.0 毕业设计架构评审门禁检查器
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

REQUIRED_SUBSYSTEMS: Set[str] = {
    "core_infra",
    "hybrid_rag",
    "multi_agent_mcp",
    "fastapi_sse_ui",
    "eval_and_benchmark",
    "docker_ops_guardrail",
}


@dataclass
class ArchProposal:
    """架构设计提案"""
    project_name: str
    version: str
    subsystems: Set[str]
    target_p95_ttft_ms: float
    target_recall_at_5: float
    has_security_guardrail: bool
    has_hitl_approval: bool
    milestone_days: Dict[int, str] = field(default_factory=dict)


def review_architecture(proposal: ArchProposal) -> Dict[str, object]:
    """执行企业级架构评审，返回是否通过与整改意见"""
    blockers: List[str] = []
    missing = sorted(REQUIRED_SUBSYSTEMS - proposal.subsystems)
    if missing:
        blockers.append(f"缺少必备核心子系统: {missing}")
    if proposal.target_p95_ttft_ms > 2000:
        blockers.append("目标首字延迟 P95 超过 2000ms，交互体验不达标")
    if proposal.target_recall_at_5 < 0.85:
        blockers.append("RAG Recall@5 验收目标低于 85%，请引入混合检索与 Rerank")
    if not proposal.has_security_guardrail:
        blockers.append("缺少输入/输出安全护栏与 Token 熔断设计")
    if not proposal.has_hitl_approval:
        blockers.append("高危工具调用缺少人工审批(HITL)拦截节点")
    if len(proposal.milestone_days) < 6:
        blockers.append("未完整拆分 6 天冲刺里程碑(Day 59 ~ Day 64)")

    return {
        "project": f"{proposal.project_name} {proposal.version}",
        "approved": len(blockers) == 0,
        "blocker_count": len(blockers),
        "blockers": blockers,
    }


if __name__ == "__main__":
    starmind_v1 = ArchProposal(
        project_name="星辰智脑 (StarMind)",
        version="v1.0.0",
        subsystems=set(REQUIRED_SUBSYSTEMS),
        target_p95_ttft_ms=1200.0,
        target_recall_at_5=0.90,
        has_security_guardrail=True,
        has_hitl_approval=True,
        milestone_days={
            59: "项目骨架与配置/日志/数据库底座",
            60: "混合检索RAG+Rerank+引用溯源",
            61: "LangGraph多Agent+MCP+记忆+HITL",
            62: "FastAPI全量SSE/REST与前端联调",
            63: "自动化测试+Ragas评估+并发压测优化",
            64: "Docker部署+巡检脚本+交付文档",
        },
    )
    print("架构评审结果:", review_architecture(starmind_v1))

