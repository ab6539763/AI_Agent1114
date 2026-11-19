"""
Day 69 - 模块一：技术面 + HR 面全真模拟评估打分器（大厂 HC 评分卡机制）
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

WEIGHTS = {
    "coding_algo": 0.25,
    "llm_rag_theory": 0.20,
    "project_depth": 0.25,
    "system_design": 0.15,
    "hr_culture_fit": 0.15,
}


@dataclass
class MockInterviewResult:
    candidate: str
    weighted_score: float
    decision: str  # STRONG_HIRE | HIRE | LEAN_NO_HIRE | NO_HIRE
    red_flags: List[str]
    weak_areas: List[str]
    scores: Dict[str, float]


def evaluate_mock_interview(candidate: str, scores: Dict[str, float]) -> MockInterviewResult:
    missing = [k for k in WEIGHTS if k not in scores]
    if missing:
        raise ValueError(f"缺少必填面试评估维度: {missing}")

    weighted = round(sum(scores[k] * w for k, w in WEIGHTS.items()), 2)
    red_flags = [k for k, v in scores.items() if v < 60.0]
    weak_areas = sorted([k for k, v in scores.items() if v < 80.0], key=lambda k: scores[k])

    if red_flags:
        decision = "NO_HIRE" if (len(red_flags) >= 2 or weighted < 70.0) else "LEAN_NO_HIRE"
    elif weighted >= 88.0:
        decision = "STRONG_HIRE"
    elif weighted >= 78.0:
        decision = "HIRE"
    else:
        decision = "LEAN_NO_HIRE"

    return MockInterviewResult(
        candidate=candidate,
        weighted_score=weighted,
        decision=decision,
        red_flags=red_flags,
        weak_areas=weak_areas,
        scores=dict(scores),
    )


if __name__ == "__main__":
    res = evaluate_mock_interview(
        "林同学",
        {
            "coding_algo": 84,
            "llm_rag_theory": 88,
            "project_depth": 90,
            "system_design": 72,
            "hr_culture_fit": 76,
        },
    )
    print("模拟面试评估结论:", res.decision, "总分:", res.weighted_score, "待提升项:", res.weak_areas)

