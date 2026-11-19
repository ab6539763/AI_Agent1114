"""
Day 13 课后作业 1（基础巩固）：基础巩固：带调用计数统计的装饰器 @count_calls
工单：STARMIND-013
"""

"""Day 13 课后题 1：函数调用次数统计装饰器。"""

import functools
from typing import Any, Callable


def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """统计被装饰函数的累计调用次数，挂载在 wrapper.call_count 属性上。"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.call_count += 1  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    wrapper.call_count = 0  # type: ignore[attr-defined]
    return wrapper


@count_calls
def greet(name: str) -> str:
    return f"你好，{name}"


if __name__ == "__main__":
    print(greet("林产品"))
    print(greet("阿杰"))
    print("累计调用次数:", greet.call_count)

