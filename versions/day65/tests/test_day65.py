import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 65 单元测试：15 分钟答辩节奏校验与防翻车演示编排"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day65_defense_planner import DefenseSection, JudgeScoreCard, validate_defense_plan
from src.day65_live_demo_runner import DemoStep, run_demo_rehearsal


def test_defense_plan_validation():
    good = [
        DefenseSection("痛点", 2, False),
        DefenseSection("架构", 4, True),
        DefenseSection("Demo", 4, True),
        DefenseSection("指标", 3, True),
        DefenseSection("复盘", 2, False),
    ]
    bad = [
        DefenseSection("背景废话", 8, False),
        DefenseSection("架构与Demo", 7, True),
    ]
    assert validate_defense_plan(good)["valid"] is True
    assert validate_defense_plan(bad)["valid"] is False


def test_judge_score_card():
    sc = JudgeScoreCard(90, 92, 90, 88)
    assert sc.weighted_total() == 90.1
    assert sc.grade() == "优秀 (S)"


def test_demo_runner_live_and_fallback():
    def broken_api() -> str:
        raise ConnectionError("现场会场Wi-Fi断了")

    steps = [
        DemoStep("实时场景", lambda: "命中 [DOC-01]", "快照 [DOC-01]", "[DOC-01]"),
        DemoStep("断网降级场景", broken_api, "[快照] PENDING_APPROVAL", "PENDING_APPROVAL"),
    ]
    res = run_demo_rehearsal(steps)
    assert res[0].mode == "LIVE" and res[0].passed is True
    assert res[1].mode == "FALLBACK" and res[1].passed is True

