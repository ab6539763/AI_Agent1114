"""
Day 57 课后作业 3（架构进阶）：架构进阶：结合 Redis 思路设计滑动窗口 QPS 限流 + Token 预算双保险装饰器
工单：STARMIND-057
"""

import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 5, window_sec: float = 10.0) -> None:
        self.max_requests = max_requests
        self.window_sec = window_sec
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, tenant_id: str, now: float | None = None) -> bool:
        ts = now if now is not None else time.monotonic()
        q = self._hits[tenant_id]
        while q and ts - q[0] > self.window_sec:
            q.popleft()
        if len(q) >= self.max_requests:
            return False
        q.append(ts)
        return True


rl = SlidingWindowRateLimiter(max_requests=2, window_sec=10.0)
assert rl.allow("u1", 1.0) is True
assert rl.allow("u1", 2.0) is True
assert rl.allow("u1", 3.0) is False
assert rl.allow("u1", 12.0) is True
print("滑动窗口限流器验证通过！")

