"""
Day 10 课后作业 2（企业实战）：企业实战：带最大重试次数的同步重试函数
工单：STARMIND-010
"""

"""Day 10 课后题 2：指定异常重试执行器。"""

from typing import Callable, TypeVar

T = TypeVar("T")


def retry_call(fn: Callable[[], T], max_attempts: int = 3) -> T:
    """遇到 TimeoutError 时自动重试，最多执行 max_attempts 次。"""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except TimeoutError:
            if attempt == max_attempts:
                raise
    raise RuntimeError("unreachable")


if __name__ == "__main__":
    state = {"count": 0}

    def flaky_api() -> str:
        state["count"] += 1
        if state["count"] < 3:
            raise TimeoutError(f"第 {state['count']} 次超时")
        return "第 3 次调用成功！"

    print(retry_call(flaky_api, max_attempts=3))

