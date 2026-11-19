"""
Day 38 课后作业 3（架构进阶）：作业三：实现自适应并发熔断保护器（ConcurrencyLimiter）
工单：STARMIND-038
"""

"""Day 38 作业三参考答案：非阻塞并发限流保护器"""
import threading


class ConcurrencyLimiter:
    def __init__(self, max_inflight: int = 2) -> None:
        self._sem = threading.Semaphore(max_inflight)

    def __enter__(self):
        if not self._sem.acquire(blocking=False):
            raise RuntimeError("Service Busy: 超过最大并发承载阈值，触发快速降级")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sem.release()


if __name__ == "__main__":
    limiter = ConcurrencyLimiter(max_inflight=1)
    with limiter:
        rejected = False
        try:
            with limiter:
                pass
        except RuntimeError:
            rejected = True
        assert rejected is True
    print("高并发快速降级熔断验证通过!")

