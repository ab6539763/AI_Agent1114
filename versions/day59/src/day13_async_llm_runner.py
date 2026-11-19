"""
STARMIND-013 模块二：asyncio 异步并发大模型调用与超时控制引擎。
演示 async/await、asyncio.wait_for 超时兜底、asyncio.Semaphore 并发限流与 asyncio.gather。
"""

import asyncio
import time
from typing import Any, Dict, List


async def async_mock_llm_call(prompt: str, delay_sec: float = 0.04) -> Dict[str, Any]:
    """模拟异步大模型 I/O 推理请求（非阻塞等待）。"""
    await asyncio.sleep(delay_sec)
    return {
        "prompt": prompt,
        "status": "ok",
        "answer": f"[异步回复] 已处理：{prompt}",
    }


async def invoke_with_timeout(
    prompt: str,
    delay_sec: float,
    timeout_sec: float,
) -> Dict[str, Any]:
    """为单次异步大模型调用增加超时保护，超时后优雅降级而不抛出未捕获异常。"""
    try:
        return await asyncio.wait_for(
            async_mock_llm_call(prompt, delay_sec=delay_sec),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        return {
            "prompt": prompt,
            "status": "timeout",
            "answer": f"请求超时（>{timeout_sec}s），已触发降级兜底。",
        }


async def batch_ask_concurrently(
    prompts: List[str],
    delay_sec: float = 0.04,
    timeout_sec: float = 0.2,
    max_concurrency: int = 5,
) -> List[Dict[str, Any]]:
    """
    带并发上限控制的异步批量提问调度器。
    通过 asyncio.Semaphore 防止瞬时并发过高打爆上游 API 限流。
    """
    if max_concurrency < 1:
        raise ValueError("max_concurrency 必须 >= 1")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def _bounded_task(p: str) -> Dict[str, Any]:
        async with semaphore:
            return await invoke_with_timeout(
                prompt=p,
                delay_sec=delay_sec,
                timeout_sec=timeout_sec,
            )

    tasks = [_bounded_task(p) for p in prompts]
    return list(await asyncio.gather(*tasks))


if __name__ == "__main__":
    questions = [f"批量问题 #{i}" for i in range(1, 6)]
    t0 = time.perf_counter()
    results = asyncio.run(
        batch_ask_concurrently(questions, delay_sec=0.05, timeout_sec=0.3, max_concurrency=5)
    )
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"并发完成 {len(results)} 个任务（单个 50ms），总耗时仅 {elapsed:.1f}ms")
    print("首条结果:", results[0])

