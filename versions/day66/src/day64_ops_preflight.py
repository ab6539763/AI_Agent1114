"""
Day 64 - 模块二：生产上线前异步健康巡检引擎（Preflight Check）
"""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Awaitable, Callable, Dict, List


@dataclass
class ProbeResult:
    service: str
    healthy: bool
    latency_ms: float
    detail: str


@dataclass
class PreflightReport:
    decision: str  # GO_LIVE | HOLD
    results: List[ProbeResult]
    failed_services: List[str]


async def run_preflight_checks(
    probes: Dict[str, Callable[[], Awaitable[bool]]],
    max_latency_ms: float = 500.0,
) -> PreflightReport:
    async def _check(name: str, fn: Callable[[], Awaitable[bool]]) -> ProbeResult:
        t0 = time.perf_counter()
        try:
            ok = await fn()
            dt = round((time.perf_counter() - t0) * 1000.0, 2)
            if not ok:
                return ProbeResult(name, False, dt, "探针返回非健康状态")
            if dt > max_latency_ms:
                return ProbeResult(name, False, dt, f"响应超时({dt}ms > {max_latency_ms}ms)")
            return ProbeResult(name, True, dt, "OK")
        except Exception as exc:
            dt = round((time.perf_counter() - t0) * 1000.0, 2)
            return ProbeResult(name, False, dt, f"探测异常: {exc}")

    results = await asyncio.gather(*(_check(k, v) for k, v in probes.items()))
    failed = [r.service for r in results if not r.healthy]
    decision = "GO_LIVE" if not failed else "HOLD"
    return PreflightReport(decision=decision, results=list(results), failed_services=failed)


if __name__ == "__main__":
    async def ok_probe() -> bool:
        await asyncio.sleep(0.005)
        return True

    rep = asyncio.run(
        run_preflight_checks(
            {
                "api_healthz": ok_probe,
                "api_readyz": ok_probe,
                "redis_cache": ok_probe,
                "llm_gateway": ok_probe,
            }
        )
    )
    print("上线巡检结论:", rep.decision, [(r.service, r.healthy, r.latency_ms) for r in rep.results])

