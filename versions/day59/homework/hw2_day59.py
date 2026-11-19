"""
Day 59 课后作业 2（企业实战）：企业实战：给日志格式化器增加自动密钥字段脱敏（防 api_key 泄露）
工单：STARMIND-059
"""

from src.day59_core_infra import format_json_log

SENSITIVE_KEYS = ("key", "secret", "token", "password")


def safe_json_log(level: str, event: str, trace_id: str, extra: dict) -> str:
    clean = {
        k: ("***REDACTED***" if any(s in k.lower() for s in SENSITIVE_KEYS) else v)
        for k, v in extra.items()
    }
    return format_json_log(level, event, trace_id, clean)


out = safe_json_log("info", "llm_call", "tr-1", {"model": "qwen", "api_key": "sk-123456"})
assert "sk-123456" not in out and "***REDACTED***" in out
print("安全日志脱敏通过:", out)

