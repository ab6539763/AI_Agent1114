import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 21 自动化单元测试：验证综合对话引擎与第 3 周自动化周测基准全部通过。"""

from src.day21_integrated_engine import StarMindIntegratedEngine
from src.day21_benchmark_runner import WeeklyBenchmarkRunner


def test_weekly_benchmark_passes_with_full_score():
    runner = WeeklyBenchmarkRunner(StarMindIntegratedEngine(max_history_turns=3))
    summary = runner.run_all()
    assert summary.passed_all is True
    assert summary.total_score == 100
    assert summary.grade == "A+"


def test_multi_session_isolation():
    eng = StarMindIntegratedEngine()
    list(eng.stream_turn("user_a", "你好，我叫老王"))
    list(eng.stream_turn("user_b", "你好，我叫小李"))

    ans_a = "".join(e.data.get("text", "") for e in eng.stream_turn("user_a", "我叫什么？") if e.event_type == "delta")
    ans_b = "".join(e.data.get("text", "") for e in eng.stream_turn("user_b", "我叫什么？") if e.event_type == "delta")

    assert "老王" in ans_a and "小李" not in ans_a
    assert "小李" in ans_b and "老王" not in ans_b

