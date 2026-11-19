"""Day 45 - 步骤二：低代码 vs 代码开发量化选型矩阵与第六周自动周测评分器。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ProjectRequirements:
    private_deployment_required: bool   # 是否必须内网私有化部署
    has_complex_cycles_or_hitl: bool    # 是否有复杂循环状态机或跨小时人工审批
    need_strict_rbac_and_ci: bool       # 是否需要行级鉴权与严格 Git/pytest CI
    delivery_days: int                  # 期望首版交付天数
    maintainer_is_non_dev: bool         # 是否主要由非研发/运营人员维护


def recommend_platform(req: ProjectRequirements) -> Dict[str, object]:
    """根据企业项目约束量化打分，推荐 Coze / Dify / LangGraph 自研方案。"""
    scores: Dict[str, int] = {"Coze": 0, "Dify": 0, "LangGraph": 0}
    reasons: List[str] = []

    if req.private_deployment_required:
        scores["Coze"] -= 10
        scores["Dify"] += 4
        scores["LangGraph"] += 4
        reasons.append("要求私有化部署：排除纯公有云 SaaS 方案")
    else:
        scores["Coze"] += 3

    if req.has_complex_cycles_or_hitl:
        scores["LangGraph"] += 6
        scores["Dify"] += 1
        reasons.append("存在复杂循环状态机/跨小时 HITL：代码编排具备绝对优势")
    else:
        scores["Dify"] += 3
        scores["Coze"] += 2

    if req.need_strict_rbac_and_ci:
        scores["LangGraph"] += 5
        scores["Dify"] += 1
        reasons.append("要求细粒度 RBAC 鉴权与自动化 CI 单测：优先代码自研")

    if req.delivery_days <= 3:
        scores["Coze"] += 4
        scores["Dify"] += 3
        reasons.append("超短周期（<=3天）交付：低代码画布可快速上线 POC")

    if req.maintainer_is_non_dev:
        scores["Dify"] += 4
        scores["Coze"] += 4
        scores["LangGraph"] -= 2
        reasons.append("由业务/运营人员长期维护：低代码可视化平台门槛更低")

    best = max(scores.items(), key=lambda kv: kv[1])[0]
    return {"recommended": best, "scores": scores, "reasons": reasons}


WEEK6_ANSWER_KEY: Dict[str, str] = {
    "Q1_react_stop_seq": "Observation:",
    "Q2_langgraph_persistence": "Checkpointer",
    "Q3_mcp_protocol": "JSON-RPC 2.0",
    "Q4_multi_agent_pattern": "Supervisor",
    "Q5_dify_var_syntax": "{{#node.var#}}",
}


def grade_week6_quiz(submissions: Dict[str, str]) -> Dict[str, object]:
    """第六周核心考点自动评分器（满分 100 分，80 分及以上为通过）。"""
    total = len(WEEK6_ANSWER_KEY)
    correct = 0
    wrong_questions: List[str] = []
    for qid, expected in WEEK6_ANSWER_KEY.items():
        actual = submissions.get(qid, "").strip()
        if actual.lower() == expected.lower():
            correct += 1
        else:
            wrong_questions.append(qid)
    score = round((correct / total) * 100)
    return {
        "score": score,
        "passed": score >= 80,
        "correct_count": correct,
        "wrong_questions": wrong_questions,
    }


if __name__ == "__main__":
    rec = recommend_platform(
        ProjectRequirements(
            private_deployment_required=True,
            has_complex_cycles_or_hitl=True,
            need_strict_rbac_and_ci=True,
            delivery_days=14,
            maintainer_is_non_dev=False,
        )
    )
    print("核心交易系统选型推荐:", rec["recommended"], "| 分数:", rec["scores"])
    quiz = grade_week6_quiz(WEEK6_ANSWER_KEY)
    print("第六周周测得分:", quiz)

