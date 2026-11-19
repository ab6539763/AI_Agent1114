import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 55 单元测试：PagedAttention 模拟与异步推理压测工具"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day55_inference_benchmark import percentile, run_benchmark
from src.day55_paged_attention_sim import simulate_kv_cache_allocation


def test_paged_attention_dramatically_reduces_waste():
    lens = [200, 350, 600, 150, 820, 400]
    cmp = simulate_kv_cache_allocation(lens, max_model_len=4096, block_size=16)
    assert cmp.naive_waste_ratio > 0.80
    assert cmp.paged_waste_ratio < 0.05
    assert cmp.memory_saved_ratio > 0.85


def test_percentile_calculation():
    assert percentile([10.0, 20.0, 30.0, 40.0, 50.0], 0.50) == 30.0
    assert percentile([10.0, 20.0, 30.0, 40.0, 50.0], 0.95) == 50.0


def test_async_benchmark_runs_and_reports_metrics():
    prompts = [f"测试问题 {i}" for i in range(8)]
    report = asyncio.run(run_benchmark(prompts, concurrency=4))
    assert report.total_requests == 8
    assert report.success_rate == 1.0
    assert report.p50_ttft_ms > 0
    assert report.p95_ttft_ms >= report.p50_ttft_ms
    assert report.throughput_tokens_per_sec > 0

