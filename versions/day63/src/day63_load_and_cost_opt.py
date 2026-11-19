"""
Day 63 - 模块二：异步并发压测引擎 + 语义缓存与分级路由 Token 降本优化器
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, List, Tuple


@dataclass
class LoadTestResult:
    total_requests: int
    concurrency: int
    success_count: int
    error_rate: float
    qps: float
    p50_ms: float
    p95_ms: float
    p99_ms: float


def percentile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, int(round((p / 100.0) * (len(sorted_vals) - 1))))
    return round(sorted_vals[idx], 2)


async def run_load_test(
    worker_fn: Callable[[int], Awaitable[bool]],
    total_requests: int = 30,
    concurrency: int = 10,
) -> LoadTestResult:
    sem = asyncio.Semaphore(concurrency)
    latencies_ms: List[float] = []
    success = 0

    async def _one(i: int) -> None:
        nonlocal success
        async with sem:
            t0 = time.perf_counter()
            ok = await worker_fn(i)
            dt = (time.perf_counter() - t0) * 1000.0
            latencies_ms.append(dt)
            if ok:
                success += 1

    start = time.perf_counter()
    await asyncio.gather(*(_one(i) for i in range(total_requests)))
    elapsed = max(1e-6, time.perf_counter() - start)

    latencies_ms.sort()
    err_rate = round((total_requests - success) / max(1, total_requests), 4)
    return LoadTestResult(
        total_requests=total_requests,
        concurrency=concurrency,
        success_count=success,
        error_rate=err_rate,
        qps=round(total_requests / elapsed, 2),
        p50_ms=percentile(latencies_ms, 50),
        p95_ms=percentile(latencies_ms, 95),
        p99_ms=percentile(latencies_ms, 99),
    )


class TokenCostOptimizer:
    """L1 精确/规范化缓存 + L2 难度分级路由（7B 本地 vs 旗舰云 API）"""

    # 单次请求均价估算（元/千Token）：旗舰 0.020，本地 7B 0.002
    PRICE_PER_1K = {"flagship": 0.020, "local_7b": 0.002, "cache": 0.0}

    def __init__(self) -> None:
        self._cache: Dict[str, str] = {}

    @staticmethod
    def _norm(q: str) -> str:
        return "".join(q.strip().lower().split())

    @staticmethod
    def _is_complex(q: str) -> bool:
        return len(q) > 28 or any(k in q for k in ("多步", "对比", "架构", "合同审查", "代码重构"))

    def simulate_traffic(self, queries: List[Tuple[str, int]]) -> Dict[str, float]:
        """对比全量直连旗舰模型 vs 启用缓存+分级路由后的总成本"""
        baseline_cost = 0.0
        optimized_cost = 0.0
        cache_hits, local_hits, flagship_hits = 0, 0, 0

        for query, total_tokens in queries:
            baseline_cost += (total_tokens / 1000.0) * self.PRICE_PER_1K["flagship"]
            key = self._norm(query)
            if key in self._cache:
                cache_hits += 1
                continue
            self._cache[key] = "cached_ok"
            if self._is_complex(query):
                flagship_hits += 1
                optimized_cost += (total_tokens / 1000.0) * self.PRICE_PER_1K["flagship"]
            else:
                local_hits += 1
                optimized_cost += (total_tokens / 1000.0) * self.PRICE_PER_1K["local_7b"]

        saving_pct = round((baseline_cost - optimized_cost) / max(1e-9, baseline_cost) * 100.0, 2)
        return {
            "baseline_cny": round(baseline_cost, 4),
            "optimized_cny": round(optimized_cost, 4),
            "saving_pct": saving_pct,
            "cache_hits": cache_hits,
            "local_7b_hits": local_hits,
            "flagship_hits": flagship_hits,
        }


if __name__ == "__main__":
    async def mock_api(i: int) -> bool:
        await asyncio.sleep(0.005 if i % 10 != 0 else 0.015)
        return True

    lt = asyncio.run(run_load_test(mock_api, total_requests=30, concurrency=10))
    print("并发压测结果:", lt)

    opt = TokenCostOptimizer()
    traffic = [
        ("出差住宿标准是多少", 1200),
        ("出差住宿标准是多少", 1200),
        ("年假有几天", 900),
        ("年假有几天", 900),
        ("请多步对比三份采购合同审查风险并给出条款修改建议", 3200),
    ]
    print("Token 成本优化报告:", opt.simulate_traffic(traffic))

