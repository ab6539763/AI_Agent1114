"""Day 46 - 步骤二：死循环检测熔断器、权限隔离缓存与大小模型分层路由。"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple


class LoopBreaker:
    """死循环检测熔断器：同一 (tool_name, args) 指纹连续重复达到阈值立即熔断。"""

    def __init__(self, max_consecutive_repeats: int = 2, max_total_calls: int = 8) -> None:
        self.max_consecutive_repeats = max_consecutive_repeats
        self.max_total_calls = max_total_calls
        self._last_sig: Optional[str] = None
        self._repeat_streak: int = 0
        self._total_calls: int = 0

    def record_and_check(self, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, str]:
        self._total_calls += 1
        if self._total_calls > self.max_total_calls:
            return False, f"触发总步数熔断：累计调用已超过 {self.max_total_calls} 次"

        sig = f"{tool_name}:{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
        if sig == self._last_sig:
            self._repeat_streak += 1
        else:
            self._last_sig = sig
            self._repeat_streak = 1

        if self._repeat_streak > self.max_consecutive_repeats:
            return False, f"触发死循环熔断：工具 {tool_name} 连续 {self._repeat_streak} 次使用完全相同参数调用"
        return True, "OK"


class ScopedPromptCache:
    """带权限维度（role/tenant）隔离的归一化 TTL 缓存，防止不同角色串读敏感缓存。"""

    def __init__(self, ttl_seconds: float = 300.0) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, str]] = {}
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _make_key(role: str, query: str) -> str:
        normalized = " ".join(query.strip().lower().split())
        return hashlib.sha256(f"{role}::{normalized}".encode("utf-8")).hexdigest()

    def get(self, role: str, query: str, now: Optional[float] = None) -> Optional[str]:
        ts = now if now is not None else time.time()
        key = self._make_key(role, query)
        item = self._store.get(key)
        if item and (ts - item[0]) <= self.ttl_seconds:
            self.hits += 1
            return item[1]
        self.misses += 1
        return None

    def set(self, role: str, query: str, response: str, now: Optional[float] = None) -> None:
        ts = now if now is not None else time.time()
        self._store[self._make_key(role, query)] = (ts, response)


class ModelTierRouter:
    """大小模型分层路由器：简单问法走轻量高速模型，复杂分析/多步规划走旗舰模型。"""

    COMPLEX_KEYWORDS = ("分析", "对比", "架构", "SQL", "多步骤", "方案", "排查", "合规")

    def select_model(self, query: str, estimated_tools: int = 0) -> Dict[str, str]:
        if estimated_tools >= 2 or len(query) >= 45 or any(k in query for k in self.COMPLEX_KEYWORDS):
            return {"tier": "pro", "model": "qwen-max", "reason": "复杂推理或多工具编排任务"}
        return {"tier": "fast", "model": "qwen-turbo", "reason": "常规简单查询，走轻量高速模型降本"}


if __name__ == "__main__":
    breaker = LoopBreaker(max_consecutive_repeats=2)
    for i in range(3):
        ok, msg = breaker.record_and_check("search_kb", {"q": "年假"})
        print(f"第 {i + 1} 次调用检查:", ok, msg)

    cache = ScopedPromptCache(ttl_seconds=60.0)
    cache.set("employee", "  差旅  住宿标准 ", "一线城市 600 元/晚")
    print("缓存命中:", cache.get("employee", "差旅 住宿标准"))
    print("跨角色隔离:", cache.get("admin", "差旅 住宿标准"))

    router = ModelTierRouter()
    print("简单路由:", router.select_model("今天几点开周会？"))
    print("复杂路由:", router.select_model("帮我用 SQL 分析华东区 Q3 营收同比并给出架构优化方案", estimated_tools=3))

