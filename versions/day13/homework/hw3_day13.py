"""
Day 13 课后作业 3（架构进阶）：架构进阶：带并发限流的异步多节点健康探活器
工单：STARMIND-013
"""

"""Day 13 课后题 3：带并发限流与超时判定的异步服务探活器。"""

import asyncio
from typing import Dict, List, Tuple


async def async_health_check_all(
    services: List[Tuple[str, float]],
    timeout_sec: float = 0.05,
    max_concurrency: int = 3,
) -> Dict[str, str]:
    """并发探活多个微服务节点，按超时阈值标记 healthy / unhealthy。"""
    sem = asyncio.Semaphore(max_concurrency)

    async def _probe(name: str, latency: float) -> Tuple[str, str]:
        async with sem:
            try:
                await asyncio.wait_for(asyncio.sleep(latency), timeout=timeout_sec)
                return name, "healthy"
            except asyncio.TimeoutError:
                return name, "unhealthy"

    pairs = await asyncio.gather(*(_probe(n, d) for n, d in services))
    return dict(pairs)


if __name__ == "__main__":
    nodes = [
        ("deepseek-gateway", 0.01),
        ("qwen-gateway", 0.02),
        ("slow-legacy-rag", 0.12),
    ]
    print(asyncio.run(async_health_check_all(nodes, timeout_sec=0.05)))

