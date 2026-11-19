"""
轻量级全链路可观测性与指标统计模块（类 LangSmith / OpenTelemetry 风格）。

核心能力：
1. 记录每一次对话、RAG 检索、Agent 推理与工具执行的 Trace 与 Span（含耗时、状态、输入/输出摘要）。
2. 实时计算接口/模型延迟分位数 P50、P95 与平均耗时。
3. 汇总累计 Token 消耗、人民币成本（CNY）、错误率与最近链路记录，供监控大盘 `/api/v1/metrics` 实时展示。
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import deque
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Iterator, List, Optional

from starmind_platform.app.core.logging_utils import get_trace_id
from starmind_platform.app.core.token_counter import TokenCounter


@dataclass
class SpanRecord:
    """单个执行跨度（Span）记录，例如一次 LLM 调用、一次向量检索或一次工具执行。"""

    span_id: str
    trace_id: str
    name: str
    category: str
    status: str
    latency_ms: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_cny: float = 0.0
    model: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _percentile(values: List[float], pct: float) -> float:
    """计算升序样本的分位数（pct 取值 0~100）。"""
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = (len(ordered) - 1) * (pct / 100.0)
    low = int(idx)
    high = min(low + 1, len(ordered) - 1)
    weight = idx - low
    return round(ordered[low] * (1 - weight) + ordered[high] * weight, 2)


class ObservabilityTracker:
    """线程安全的轻量级链路追踪与指标聚合器。"""

    def __init__(self, max_history: int = 500) -> None:
        self._lock = threading.Lock()
        self._spans: Deque[SpanRecord] = deque(maxlen=max_history)
        self._total_requests: int = 0
        self._error_requests: int = 0
        self._total_prompt_tokens: int = 0
        self._total_completion_tokens: int = 0
        self._total_cost_cny: float = 0.0
        self._category_counts: Dict[str, int] = {}

    def record_span(
        self,
        *,
        name: str,
        category: str,
        latency_ms: float,
        status: str = "ok",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        model: str = "",
        trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SpanRecord:
        """写入一条已完成的 Span 指标记录。"""
        cost = 0.0
        if prompt_tokens or completion_tokens:
            cost = TokenCounter.estimate_cost(model or "deepseek-chat", prompt_tokens, completion_tokens).total_cost_cny

        span = SpanRecord(
            span_id=f"sp-{uuid.uuid4().hex[:10]}",
            trace_id=trace_id or get_trace_id(),
            name=name,
            category=category,
            status=status,
            latency_ms=round(latency_ms, 2),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_cny=round(cost, 6),
            model=model,
            metadata=metadata or {},
        )

        with self._lock:
            self._spans.append(span)
            self._total_requests += 1
            if status != "ok":
                self._error_requests += 1
            self._total_prompt_tokens += prompt_tokens
            self._total_completion_tokens += completion_tokens
            self._total_cost_cny += cost
            self._category_counts[category] = self._category_counts.get(category, 0) + 1

        return span

    @contextmanager
    def start_span(
        self,
        name: str,
        category: str = "general",
        model: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """
        上下文管理器：自动计时并记录 Span。
        调用方可在 `with` 块内向返回的字典写入 `prompt_tokens` / `completion_tokens` / `metadata`。
        """
        ctx: Dict[str, Any] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "model": model,
            "metadata": dict(metadata or {}),
        }
        start = time.perf_counter()
        status = "ok"
        try:
            yield ctx
        except Exception as exc:
            status = "error"
            ctx["metadata"]["error"] = str(exc)
            raise
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_span(
                name=name,
                category=category,
                latency_ms=elapsed_ms,
                status=status,
                prompt_tokens=int(ctx.get("prompt_tokens", 0)),
                completion_tokens=int(ctx.get("completion_tokens", 0)),
                model=str(ctx.get("model", model)),
                metadata=ctx.get("metadata"),
            )

    def get_summary(self, recent_limit: int = 20) -> Dict[str, Any]:
        """导出供监控面板与运维接口展示的全局汇总指标。"""
        with self._lock:
            spans = list(self._spans)
            latencies = [s.latency_ms for s in spans]
            avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
            error_rate = (
                round(self._error_requests / self._total_requests, 4) if self._total_requests else 0.0
            )
            recent = [s.to_dict() for s in spans[-recent_limit:]][::-1]

            return {
                "total_spans": self._total_requests,
                "error_spans": self._error_requests,
                "error_rate": error_rate,
                "latency_ms": {
                    "avg": avg_latency,
                    "p50": _percentile(latencies, 50),
                    "p95": _percentile(latencies, 95),
                },
                "tokens": {
                    "prompt_tokens": self._total_prompt_tokens,
                    "completion_tokens": self._total_completion_tokens,
                    "total_tokens": self._total_prompt_tokens + self._total_completion_tokens,
                },
                "total_cost_cny": round(self._total_cost_cny, 6),
                "by_category": dict(self._category_counts),
                "recent_traces": recent,
            }

    def reset(self) -> None:
        """清空内存统计数据（常用于单元测试隔离）。"""
        with self._lock:
            self._spans.clear()
            self._total_requests = 0
            self._error_requests = 0
            self._total_prompt_tokens = 0
            self._total_completion_tokens = 0
            self._total_cost_cny = 0.0
            self._category_counts.clear()


_GLOBAL_OBSERVABILITY = ObservabilityTracker()


def get_observability() -> ObservabilityTracker:
    """获取平台全局单例可观测性追踪器。"""
    return _GLOBAL_OBSERVABILITY
