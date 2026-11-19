"""
STARMIND-005 模块二：模拟大模型 API JSON 响应解析与审计落盘工具。
演示 json.loads、json.dumps、json.load、json.dump 及 UTF-8 中文无转义持久化。
"""

import json
from pathlib import Path
from typing import Dict, Any

from day05_dict_utils import safe_get_path

# 模拟一条真实的 DeepSeek / 通义千问兼容格式 API JSON 响应
MOCK_API_RESPONSE_JSON = json.dumps(
    {
        "id": "chatcmpl-starmind-005",
        "object": "chat.completion",
        "model": "deepseek-chat",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "您好！您的订单 ORD-20260505 已由顺丰揽收，预计明日送达杭州滨江区。",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 128,
            "completion_tokens": 42,
            "total_tokens": 170,
        },
    },
    ensure_ascii=False,
)


def parse_llm_response(raw_json: str) -> Dict[str, Any]:
    """解析大模型原始 JSON 响应字符串，返回星辰智脑内部标准结果字典。"""
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"JSON 解析失败: {exc.msg}",
            "reply": "",
            "total_tokens": 0,
        }

    # 如果上游返回了错误对象（如限流或鉴权失败）
    if isinstance(payload, dict) and "error" in payload:
        return {
            "ok": False,
            "error": str(safe_get_path(payload, "error.message", payload["error"])),
            "reply": "",
            "total_tokens": 0,
        }

    reply_text = safe_get_path(payload, "choices.0.message.content", "")
    model_name = safe_get_path(payload, "model", "unknown-model")
    finish_reason = safe_get_path(payload, "choices.0.finish_reason", "unknown")
    prompt_tokens = int(safe_get_path(payload, "usage.prompt_tokens", 0))
    completion_tokens = int(safe_get_path(payload, "usage.completion_tokens", 0))
    total_tokens = int(safe_get_path(payload, "usage.total_tokens", prompt_tokens + completion_tokens))

    return {
        "ok": bool(reply_text),
        "request_id": safe_get_path(payload, "id", "N/A"),
        "model": model_name,
        "reply": reply_text,
        "finish_reason": finish_reason,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def save_audit_record(record: Dict[str, Any], file_path: Path) -> Path:
    """将结构化解析结果以可读中文 JSON 写入磁盘文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return file_path


def load_audit_record(file_path: Path) -> Dict[str, Any]:
    """从磁盘 JSON 文件无损读回审计记录。"""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    parsed = parse_llm_response(MOCK_API_RESPONSE_JSON)
    # 使用 json.dumps 格式化打印，ensure_ascii=False 确保中文直接显示
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

