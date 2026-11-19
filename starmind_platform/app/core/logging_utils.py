"""
结构化中文工程日志与 TraceID 上下文管理模块。

核心能力：
1. 基于 `contextvars.ContextVar` 实现协程与线程安全的 TraceID 透传。
2. 输出标准化 JSON 结构日志，天然兼容 ELK / Loki / 阿里云 SLS 日志采集。
3. 内置上下文管理器 `trace_context`，便于在 HTTP 中间件、Agent 步骤和异步任务中自动绑定链路 ID。
"""

from __future__ import annotations

import contextvars
import json
import logging
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, Optional

# 协程级 TraceID 上下文变量，默认值为 "-"
_trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("starmind_trace_id", default="-")


def generate_trace_id(prefix: str = "tr") -> str:
    """生成短小且全局唯一的链路追踪 ID，例如 `tr-9f3a2c1b8e7d`。"""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def get_trace_id() -> str:
    """获取当前协程上下文中的 TraceID。"""
    return _trace_id_var.get()


def set_trace_id(trace_id: str) -> contextvars.Token[str]:
    """设置当前协程上下文中的 TraceID，返回 Token 以便精确恢复。"""
    return _trace_id_var.set(trace_id)


@contextmanager
def trace_context(trace_id: Optional[str] = None) -> Iterator[str]:
    """
    TraceID 上下文管理器。
    进入上下文时自动绑定（或新建）TraceID，退出时自动恢复原上下文，避免污染复用线程。
    """
    tid = trace_id or generate_trace_id()
    token = _trace_id_var.set(tid)
    try:
        yield tid
    finally:
        _trace_id_var.reset(token)


class StructuredChineseFormatter(logging.Formatter):
    """
    结构化中文工程日志格式化器。
    每条日志输出单行 UTF-8 JSON（`ensure_ascii=False`），兼顾可读性与机器解析。
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "trace_id": get_trace_id(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        # 支持通过 extra={"extra_fields": {...}} 注入业务维度字段
        extra_fields = getattr(record, "extra_fields", None)
        if isinstance(extra_fields, dict) and extra_fields:
            payload["fields"] = extra_fields

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "starmind", level: str = "INFO") -> logging.Logger:
    """
    获取已配置结构化输出格式的工程日志器。
    多次调用对同一 name 幂等，不会重复挂载 Handler。
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredChineseFormatter())
        logger.addHandler(handler)
        logger.propagate = False

    return logger
