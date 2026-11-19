"""
Day 67 课后作业 2（企业实战）：企业实战：手写带指数退避（Exponential Backoff）的异步重试装饰器
工单：STARMIND-067
"""

import asyncio


async def async_retry(fn, max_retries: int = 3, base_delay: float = 0.005):
    last_err = None
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception as exc:
            last_err = exc
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
    raise last_err


calls = {"n": 0}


async def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise RuntimeError("429 rate limit")
    return "OK"


assert asyncio.run(async_retry(flaky)) == "OK" and calls["n"] == 3
print("指数退避重试通过")

