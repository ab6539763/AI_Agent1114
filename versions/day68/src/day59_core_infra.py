"""
Day 59 - 模块一：星辰智脑核心底座（配置中心 + 统一异常 + JSON结构化日志）
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StarMindSettings(BaseSettings):
    """星辰智脑强类型配置中心"""
    model_config = SettingsConfigDict(env_prefix="STARMIND_", extra="ignore")

    app_name: str = "StarMind-Enterprise"
    env: str = "dev"
    database_url: str = "sqlite:///:memory:"
    default_model: str = "starmind-7b-local"
    daily_budget_cny: float = Field(default=100.0, gt=0.0)
    rag_top_k: int = Field(default=5, ge=1, le=20)


class StarMindError(Exception):
    """统一业务异常基类"""

    def __init__(self, code: int, message: str, http_status: int = 400, trace_id: str = "") -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.trace_id = trace_id or new_trace_id()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "trace_id": self.trace_id,
        }


def new_trace_id() -> str:
    return f"tr-{uuid.uuid4().hex[:12]}"


def format_json_log(
    level: str,
    event: str,
    trace_id: str,
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    """生成单行 JSON 结构化日志，适配 ELK / 阿里云 SLS"""
    payload: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "trace_id": trace_id,
        "event": event,
    }
    if extra:
        payload["extra"] = extra
    return json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    cfg = StarMindSettings()
    tid = new_trace_id()
    print(format_json_log("info", "app_boot", tid, {"app": cfg.app_name, "top_k": cfg.rag_top_k}))
    err = StarMindError(4291, "部门日配额已耗尽触发熔断", http_status=429, trace_id=tid)
    print("异常封包:", err.to_dict())

