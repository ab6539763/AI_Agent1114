import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 63 单元测试：Ragas 四维评测、异步并发压测与 Token 降本优化"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day63_ragas_evaluator import EvalSample, evaluate_ragas
from src.day63_load_and_cost_opt import TokenCostOptimizer, run_load_test


def test_ragas_passes_grounded_and_blocks_hallucination():
    good = [
        EvalSample(
            "一线城市住宿标准",
            "一线城市住宿上限650元/晚，需上传电子专票。",
            ["一线城市出差住宿上限650元/晚，需在费用中心上传电子专票核销。"],
            "一线城市住宿上限650元/晚，需电子专票。",
        )
    ]
    bad = [
        EvalSample(
            "一线城市住宿标准",
            "火星移民船票定价五百万星币免费送太空舱。",
            ["一线城市出差住宿上限650元/晚。"],
            "一线城市住宿上限650元/晚。",
        )
    ]
    assert evaluate_ragas(good).passed is True
    assert evaluate_ragas(bad).passed is False


def test_async_load_tester_metrics():
    async def mock_worker(i: int) -> bool:
        await asyncio.sleep(0.002)
        return i != 0

    res = asyncio.run(run_load_test(mock_worker, total_requests=20, concurrency=5))
    assert res.total_requests == 20
    assert res.success_count == 19
    assert res.error_rate == 0.05
    assert res.p95_ms >= res.p50_ms > 0
    assert res.qps > 0


def test_token_cost_optimizer_saves_over_40_percent():
    opt = TokenCostOptimizer()
    traffic = [
        ("住宿标准", 1000),
        ("住宿标准", 1000),
        ("报销流程", 1000),
        ("报销流程", 1000),
        ("请进行多步合同审查与架构对比分析", 2000),
    ]
    rep = opt.simulate_traffic(traffic)
    assert rep["cache_hits"] == 2
    assert rep["local_7b_hits"] == 2
    assert rep["flagship_hits"] == 1
    assert rep["saving_pct"] >= 40.0

