"""
Day 09 课后作业 3（架构进阶）：架构进阶：支持上下文管理器（with 语句）的耗时统计器
工单：STARMIND-009
"""

"""Day 9 课后题 3：基于 __enter__ / __exit__ 的模型调用耗时监控器。"""

import time


class TimerContext:
    def __init__(self, label: str) -> None:
        self.label = label
        self.elapsed_ms: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> "TimerContext":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.elapsed_ms = round((time.perf_counter() - self._start) * 1000.0, 3)
        # 返回 False 表示不吞掉代码块内部的异常
        return False


if __name__ == "__main__":
    with TimerContext("模拟推理") as timer:
        _ = sum(range(10000))
    print(f"[{timer.label}] 耗时: {timer.elapsed_ms} ms")

