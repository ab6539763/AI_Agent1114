import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 69 单元测试：模拟面试 HC 评估打分器与 7 天整改清单生成"""
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day69_mock_interview_scorer import evaluate_mock_interview
from src.day69_improvement_planner import generate_7day_plan


def test_strong_hire_decision():
    res = evaluate_mock_interview(
        "张三",
        {"coding_algo": 92, "llm_rag_theory": 90, "project_depth": 94, "system_design": 86, "hr_culture_fit": 88},
    )
    assert res.decision == "STRONG_HIRE"
    assert res.red_flags == [] and res.weak_areas == []


def test_single_red_flag_blocks_hire():
    res = evaluate_mock_interview(
        "李四",
        {"coding_algo": 52, "llm_rag_theory": 90, "project_depth": 92, "system_design": 85, "hr_culture_fit": 85},
    )
    assert res.weighted_score >= 78.0
    assert res.red_flags == ["coding_algo"]
    assert res.decision == "LEAN_NO_HIRE"


def test_7day_plan_prioritizes_red_flag_and_missing_dim_raises():
    res = evaluate_mock_interview(
        "王五",
        {"coding_algo": 58, "llm_rag_theory": 85, "project_depth": 82, "system_design": 70, "hr_culture_fit": 85},
    )
    plan = generate_7day_plan(res)
    assert "P0-红线攻坚 - coding_algo" in plan
    assert "Day 7" in plan

    with pytest.raises(ValueError):
        evaluate_mock_interview("缺项", {"coding_algo": 80})

