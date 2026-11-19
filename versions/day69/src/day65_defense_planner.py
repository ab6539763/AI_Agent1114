"""
Day 65 - 模块一：15 分钟毕业答辩结构校验器与企业评委评分模型
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DefenseSection:
    name: str
    minutes: int
    is_core_tech: bool


@dataclass
class JudgeScoreCard:
    architecture: float   # 0~100 (权重 30%)
    live_demo: float      # 0~100 (权重 25%)
    metrics_cost: float   # 0~100 (权重 25%)
    qa_defense: float     # 0~100 (权重 20%)

    def weighted_total(self) -> float:
        total = (
            self.architecture * 0.30
            + self.live_demo * 0.25
            + self.metrics_cost * 0.25
            + self.qa_defense * 0.20
        )
        return round(total, 2)

    def grade(self) -> str:
        s = self.weighted_total()
        if s >= 90:
            return "优秀 (S)"
        if s >= 80:
            return "良好 (A)"
        if s >= 70:
            return "合格 (B)"
        return "需复辩 (C)"


def validate_defense_plan(sections: List[DefenseSection], target_minutes: int = 15) -> Dict[str, object]:
    total = sum(s.minutes for s in sections)
    core_minutes = sum(s.minutes for s in sections if s.is_core_tech)
    core_ratio = round(core_minutes / max(1, total), 4)
    issues: List[str] = []
    if total != target_minutes:
        issues.append(f"总时长应为 {target_minutes} 分钟，当前为 {total} 分钟")
    if core_ratio < 0.65:
        issues.append(f"核心技术与演示占比 {core_ratio:.0%} 低于 65% 红线，背景铺垫过长")
    return {"valid": len(issues) == 0, "total_minutes": total, "core_ratio": core_ratio, "issues": issues}


JUDGE_QA_BANK = [
    {
        "topic": "RAG 幻觉控制",
        "question": "如何证明你们的 RAG 不会胡编乱造财务制度？",
        "key_points": ["BM25+向量+RRF混合召回", "Rerank低分置信度拒答门禁", "强制[DOC-xx]引用溯源", "Ragas Faithfulness 量化报告"],
    },
    {
        "topic": "Agent 安全边界",
        "question": "如果大模型抽风把 5 万元报销单直接提交了怎么办？",
        "key_points": ["确定性代码层风险策略拦截", "超2000元挂起PENDING_APPROVAL", "HITL主管审批恢复与终态幂等校验"],
    },
    {
        "topic": "成本与并发",
        "question": "全公司几千人用，Token 费用会不会爆炸？",
        "key_points": ["L1公共FAQ语义缓存", "L2本地7B与云端旗舰分级路由", "租户日配额80%预警/100%硬熔断"],
    },
]


if __name__ == "__main__":
    plan = [
        DefenseSection("业务痛点与PRD目标", 2, False),
        DefenseSection("核心架构与技术选型", 4, True),
        DefenseSection("端到端现场Demo演示", 4, True),
        DefenseSection("Ragas评测、压测与降本", 3, True),
        DefenseSection("踩坑复盘与演进路线", 2, False),
    ]
    print("答辩节奏校验:", validate_defense_plan(plan))
    score = JudgeScoreCard(architecture=92, live_demo=95, metrics_cost=90, qa_defense=88)
    print("模拟评委得分:", score.weighted_total(), score.grade())

