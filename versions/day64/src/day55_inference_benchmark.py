"""
Day 55 - 模块二：大模型推理服务异步并发压测基准工具（TTFT / TPOT / TPS）
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import AsyncIterator, Callable, List


@dataclass
class RequestMetric:
    """单次流式推理请求指标"""
    ttft_ms: float
    e2e_ms: float
    output_tokens: int
    tpot_ms: float
    success: bool


@dataclass
class BenchmarkSummary:
    """并发压测汇总报告"""
    total_requests: int
    concurrency: int
    success_rate: float
    p50_ttft_ms: float
    p95_ttft_ms: float
    avg_tpot_ms: float
    throughput_tokens_per_sec: float
    total_wall_sec: float


def percentile(values: List[float], p: float) -> float:
    """计算百分位数（如 p=0.95 表示 P95）"""
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * p))))
    return round(ordered[idx], 2)


async def mock_vllm_stream(prompt: str, output_tokens: int = 24) -> AsyncIterator[str]:
    """模拟 vLLM 流式输出（Prefill 首字延迟 + Decode 逐字输出）"""
    await asyncio.sleep(0.015 + min(0.02, len(prompt) * 0.0001))
    for i in range(output_tokens):
        await asyncio.sleep(0.004)
        yield f"tok{i}"


async def run_benchmark(
    prompts: List[str],
    concurrency: int = 5,
    stream_fn: Callable[[str], AsyncIterator[str]] = mock_vllm_stream,
) -> BenchmarkSummary:
    """以指定并发度压测推理服务并输出 TTFT / TPOT / 吞吐量报告"""
    sem = asyncio.Semaphore(concurrency)
    metrics: List[RequestMetric] = []

    async def _worker(prompt: str) -> None:
        async with sem:
            t0 = time.perf_counter()
            first_token_at: float | None = None
            tok_count = 0
            try:
                async for _ in stream_fn(prompt):
                    if first_token_at is None:
                        first_token_at = time.perf_counter()
                    tok_count += 1
                t_end = time.perf_counter()
                ttft = ((first_token_at or t_end) - t0) * 1000.0
                e2e = (t_end - t0) * 1000.0
                decode_ms = max(0.0, e2e - ttft)
                tpot = decode_ms / max(1, tok_count - 1)
                metrics.append(RequestMetric(ttft, e2e, tok_count, tpot, True))
            except Exception:
                t_end = time.perf_counter()
                metrics.append(RequestMetric(0.0, (t_end - t0) * 1000.0, 0, 0.0, False))

    wall_start = time.perf_counter()
    await asyncio.gather(*(_worker(p) for p in prompts))
    wall_sec = max(1e-6, time.perf_counter() - wall_start)

    ok = [m for m in metrics if m.success]
    total_tokens = sum(m.output_tokens for m in ok)
    return BenchmarkSummary(
        total_requests=len(prompts),
        concurrency=concurrency,
        success_rate=round(len(ok) / max(1, len(prompts)), 4),
        p50_ttft_ms=percentile([m.ttft_ms for m in ok], 0.50),
        p95_ttft_ms=percentile([m.ttft_ms for m in ok], 0.95),
        avg_tpot_ms=round(sum(m.tpot_ms for m in ok) / max(1, len(ok)), 2),
        throughput_tokens_per_sec=round(total_tokens / wall_sec, 2),
        total_wall_sec=round(wall_sec, 3),
    )


if __name__ == "__main__":
    test_prompts = [f"请解释星辰智脑工单处理规范第{i}条" for i in range(15)]
    summary = asyncio.run(run_benchmark(test_prompts, concurrency=5))
    print("压测报告:", summary)

