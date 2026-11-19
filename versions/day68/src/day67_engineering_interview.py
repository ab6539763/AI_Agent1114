"""
Day 67 - 模块二：面试高频手撕——令牌桶限流器 (Token Bucket) 与 O(1) TTL-LRU 缓存
"""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Callable, Optional, Tuple


class TokenBucketLimiter:
    """惰性计算令牌桶限流器：O(1) 时间复杂度，无需后台定时线程"""

    def __init__(
        self,
        capacity: float,
        refill_rate: float,
        clock_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)  # tokens per second
        self._clock = clock_fn
        self._tokens = float(capacity)
        self._last_ts = self._clock()

    def allow(self, cost: float = 1.0) -> bool:
        now = self._clock()
        elapsed = max(0.0, now - self._last_ts)
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)
        self._last_ts = now
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False


class TTLLRUCache:
    """O(1) 带 TTL 过期的 LRU 缓存（OrderedDict 实现）"""

    def __init__(
        self,
        maxsize: int = 128,
        ttl_seconds: float = 60.0,
        clock_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self.maxsize = max(1, maxsize)
        self.ttl_seconds = ttl_seconds
        self._clock = clock_fn
        self._store: OrderedDict[str, Tuple[Any, float]] = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        val, expire_at = self._store[key]
        if self._clock() >= expire_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return val

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        ttl = self.ttl_seconds if ttl_seconds is None else ttl_seconds
        expire_at = self._clock() + ttl
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (value, expire_at)
        while len(self._store) > self.maxsize:
            self._store.popitem(last=False)


if __name__ == "__main__":
    fake_now = [0.0]
    tb = TokenBucketLimiter(capacity=2, refill_rate=1.0, clock_fn=lambda: fake_now[0])
    print("突发3次请求:", [tb.allow(), tb.allow(), tb.allow()])
    fake_now[0] += 1.0
    print("1秒后补充1个令牌:", tb.allow())

    cache = TTLLRUCache(maxsize=2, ttl_seconds=10.0, clock_fn=lambda: fake_now[0])
    cache.set("k1", "v1")
    cache.set("k2", "v2")
    _ = cache.get("k1")  # k1 变热
    cache.set("k3", "v3")  # 淘汰最久未用的 k2
    print("LRU 淘汰验证 (k1, k2, k3):", cache.get("k1"), cache.get("k2"), cache.get("k3"))

