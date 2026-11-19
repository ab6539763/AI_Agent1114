"""
带指数退避与随机抖动（Exponential Backoff + Jitter）的同步/异步重试装饰器模块。

工程实践说明：
- 在调用大模型 API、向量检索或外部企业系统时，网络抖动和 429/503 限流非常常见。
- 固定间隔重试容易引发“惊群效应”，加入全抖动（Full Jitter）能有效打散并发重试流量。
"""

from __future__ import annotations

import asyncio
import functools
import inspect
import random
import time
from typing import Any, Callable, Tuple, Type, TypeVar

from starmind_platform.app.core.logging_utils import get_logger

logger = get_logger("starmind.retry")

F = TypeVar("F", bound=Callable[..., Any])


def compute_backoff_delay(
    attempt: int,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    jitter: bool = True,
) -> float:
    """
    计算第 `attempt` 次失败后的退避等待时间（秒）。

    参数：
        attempt: 已失败次数（从 1 开始计数）。
        base_delay: 初始退避基数（秒）。
        max_delay: 最大退避上限（秒），防止等待过久拖垮请求。
        jitter: 是否开启随机抖动（在 [0.5 * exp, exp] 区间均匀采样）。
    """
    exp_delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
    if not jitter:
        return exp_delay
    return random.uniform(exp_delay * 0.5, exp_delay)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 0.2,
    max_delay: float = 5.0,
    jitter: bool = True,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable[[F], F]:
    """
    通用同步/异步指数退避重试装饰器。
    自动识别被装饰函数是否为协程函数（`async def`），分别使用 `asyncio.sleep` 或 `time.sleep`。

    示例：
        @retry_with_backoff(max_retries=3, exceptions=(LLMTimeoutError, httpx.HTTPError))
        async def call_upstream(): ...
    """

    def decorator(func: F) -> F:
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                last_exc: BaseException | None = None
                for attempt in range(1, max_retries + 2):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as exc:
                        last_exc = exc
                        if attempt > max_retries:
                            logger.error(
                                f"异步调用 {func.__name__} 重试 {max_retries} 次后仍失败: {exc}"
                            )
                            raise
                        delay = compute_backoff_delay(attempt, base_delay, max_delay, jitter)
                        logger.warning(
                            f"异步调用 {func.__name__} 第 {attempt} 次失败({type(exc).__name__})，"
                            f"{delay:.3f}s 后重试..."
                        )
                        await asyncio.sleep(delay)
                assert last_exc is not None
                raise last_exc

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exc: BaseException | None = None
            for attempt in range(1, max_retries + 2):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt > max_retries:
                        logger.error(
                            f"同步调用 {func.__name__} 重试 {max_retries} 次后仍失败: {exc}"
                        )
                        raise
                    delay = compute_backoff_delay(attempt, base_delay, max_delay, jitter)
                    logger.warning(
                        f"同步调用 {func.__name__} 第 {attempt} 次失败({type(exc).__name__})，"
                        f"{delay:.3f}s 后重试..."
                    )
                    time.sleep(delay)
            assert last_exc is not None
            raise last_exc

        return sync_wrapper  # type: ignore[return-value]

    return decorator
