"""
STARMIND-013 模块一：dotenv 配置加载、指数退避重试装饰器与 yield 流式生成器。
演示 python-dotenv、functools.wraps、typing 类型注解与生成器惰性求值。
"""

import functools
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Tuple, Type, TypeVar

from dotenv import dotenv_values

T = TypeVar("T")


@dataclass
class EnvSettings:
    """从 .env 安全加载的应用配置。"""

    model_name: str = "deepseek-chat"
    api_key: str = ""
    timeout_sec: float = 15.0
    max_retries: int = 3


def load_env_settings(env_path: Optional[Path] = None) -> EnvSettings:
    """
    安全解析 .env 文件并返回强类型 EnvSettings。
    文件不存在时平滑回退到默认配置，不污染全局 os.environ。
    """
    raw: dict[str, Optional[str]] = {}
    if env_path is not None and env_path.exists():
        raw = dict(dotenv_values(env_path))

    return EnvSettings(
        model_name=(raw.get("STARMIND_MODEL") or "deepseek-chat").strip(),
        api_key=(raw.get("STARMIND_API_KEY") or "").strip(),
        timeout_sec=float(raw.get("STARMIND_TIMEOUT") or 15.0),
        max_retries=int(raw.get("STARMIND_MAX_RETRIES") or 3),
    )


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 0.01,
    exceptions: Tuple[Type[BaseException], ...] = (RuntimeError, TimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    指数退避重试装饰器。
    当被装饰函数抛出指定 exceptions 时，按 base_delay * 2^attempt 休眠后重试。
    """
    if max_retries < 1:
        raise ValueError("max_retries 必须 >= 1")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: Optional[BaseException] = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == max_retries - 1:
                        break
                    sleep_sec = base_delay * (2 ** attempt)
                    if sleep_sec > 0:
                        time.sleep(sleep_sec)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


def stream_text_chunks(text: str, chunk_size: int = 4) -> Generator[str, None, None]:
    """使用 yield 按固定块大小惰性吐出文本，模拟大模型流式输出。"""
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须为正整数")
    for idx in range(0, len(text), chunk_size):
        yield text[idx : idx + chunk_size]


if __name__ == "__main__":
    # 1. 演示重试装饰器：前两次模拟接口抖动，第三次成功
    state = {"calls": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.005, exceptions=(RuntimeError,))
    def flaky_api_call(prompt: str) -> str:
        state["calls"] += 1
        if state["calls"] < 3:
            raise RuntimeError(f"第 {state['calls']} 次调用触发临时限流")
        return f"第 {state['calls']} 次成功返回：{prompt}"

    print(flaky_api_call("总结星辰数科年假制度"))

    # 2. 演示 yield 流式分块输出
    chunks = list(stream_text_chunks("星辰智脑正在流式生成回答！", chunk_size=4))
    print("流式分块结果:", chunks)

