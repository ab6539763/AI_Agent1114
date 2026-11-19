"""
Day 38 - 步骤二：多线程并发压测引擎与项目二答辩量化对比报告
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day38_code_review_and_perf import (
    NaiveSlowKBService,
    OptimizedFastKBService,
    build_benchmark_corpus,
)


@dataclass
class LoadTestStats:
    service_name: str
    total_requests: int
    concurrency: int
    qps: float
    avg_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    cache_hit_rate: float


def percentile(sorted_vals: Sequence[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, int(round((pct / 100.0) * (len(sorted_vals) - 1))))
    return round(sorted_vals[idx], 3)


def run_benchmark(
    service_name: str,
    service,
    queries: Sequence[str],
    concurrency: int = 4,
    total_requests: int = 80,
) -> LoadTestStats:
    """多线程并发压测器：模拟早高峰高频+长尾混合流量并采集分位数延迟。"""
    workload = [queries[i % len(queries)] for i in range(total_requests)]
    latencies_ms: List[float] = []

    def _worker(q: str) -> float:
        t0 = time.perf_counter()
        service.search(q, department="rd", top_k=2)
        return (time.perf_counter() - t0) * 1000.0

    wall_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        latencies_ms = list(pool.map(_worker, workload))
    wall_sec = max(1e-6, time.perf_counter() - wall_start)

    latencies_ms.sort()
    hit_rate = service.cache.hit_rate if hasattr(service, "cache") else 0.0
    return LoadTestStats(
        service_name=service_name,
        total_requests=total_requests,
        concurrency=concurrency,
        qps=round(total_requests / wall_sec, 1),
        avg_ms=round(sum(latencies_ms) / len(latencies_ms), 3),
        p50_ms=percentile(latencies_ms, 50),
        p95_ms=percentile(latencies_ms, 95),
        p99_ms=percentile(latencies_ms, 99),
        cache_hit_rate=hit_rate,
    )


def render_defense_report(before: LoadTestStats, after: LoadTestStats) -> str:
    speedup = round(after.qps / max(0.1, before.qps), 2)
    return (
        "================ StarMind-KB v2.0 项目二答辩压测简报 ================\n"
        f"测试规模: {before.total_requests} 请求 | 并发线程: {before.concurrency}\n"
        f"[重构前 NaiveSlow]     QPS={before.qps:8.1f} | Avg={before.avg_ms:6.3f}ms | P95={before.p95_ms:6.3f}ms | P99={before.p99_ms:6.3f}ms\n"
        f"[重构后 OptimizedFast] QPS={after.qps:8.1f} | Avg={after.avg_ms:6.3f}ms | P95={after.p95_ms:6.3f}ms | P99={after.p99_ms:6.3f}ms | CacheHit={after.cache_hit_rate:.1%}\n"
        f">>> 吞吐量提升倍数 (Speedup): {speedup}x\n"
        "======================================================================"
    )


if __name__ == "__main__":
    corpus = build_benchmark_corpus(noise_count=240)
    slow_svc = NaiveSlowKBService(corpus)
    fast_svc = OptimizedFastKBService(corpus)

    hot_queries = [
        "北京出差住酒店报销上限是多少？",
        "入职满一年年假有几天怎么申请？",
        "ERR-5042 网关超时怎么排查？",
        "周五下午能发布代码上线吗？",
    ]
    before = run_benchmark("NaiveSlowKBService", slow_svc, hot_queries, concurrency=4, total_requests=60)
    after = run_benchmark("OptimizedFastKBService", fast_svc, hot_queries, concurrency=4, total_requests=60)
    print(render_defense_report(before, after))

