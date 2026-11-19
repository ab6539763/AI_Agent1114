"""
Day 40 课后作业 2（企业实战）：编写工具执行超时保护装饰器
工单：STARMIND-040
"""

"""Day 40 作业 2 参考答案：工具超时隔离执行器。"""

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from typing import Any, Callable, Dict


def run_with_timeout(func: Callable[..., Any], kwargs: Dict[str, Any], timeout_sec: float = 1.0) -> str:
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(func, **kwargs)
    try:
        return str(future.result(timeout=timeout_sec))
    except FuturesTimeout:
        return f"工具执行超时（>{timeout_sec}s），请降级处理或跳过该工具。"
    finally:
        pool.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    def slow_api(q: str) -> str:
        time.sleep(0.5)
        return q

    res_timeout = run_with_timeout(slow_api, {"q": "hello"}, timeout_sec=0.1)
    res_ok = run_with_timeout(lambda q: f"ok:{q}", {"q": "fast"}, timeout_sec=1.0)
    print(res_timeout, "|", res_ok)
    assert "超时" in res_timeout and res_ok == "ok:fast"

