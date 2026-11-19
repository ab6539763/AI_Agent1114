"""
Day 17 课后作业 3（架构进阶）：健壮的 JSON 输出修复与 Schema 类型校验器
工单：STARMIND-017
"""

import json
import re
from typing import Any, Dict, Type


def parse_and_validate_json(
    raw_text: str, schema_types: Dict[str, Type[Any]]
) -> Dict[str, Any]:
    """容错解析 LLM 输出的 JSON 并执行字段类型校验。"""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.I)
    # 清理 LLM 偶尔多写的尾随逗号
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("顶层 JSON 必须为对象")
    for field, expected_type in schema_types.items():
        if field not in data:
            raise ValueError(f"缺少必填字段: {field}")
        if not isinstance(data[field], expected_type):
            raise TypeError(f"字段 {field} 类型不符，期望 {expected_type.__name__}，实际 {type(data[field]).__name__}")
    return data


if __name__ == "__main__":
    dirty = '```json\n{"priority": "P0", "need_human": true,}\n```'
    print(parse_and_validate_json(dirty, {"priority": str, "need_human": bool}))

