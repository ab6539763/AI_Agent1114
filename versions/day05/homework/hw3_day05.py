"""
Day 05 课后作业 3（架构进阶）：架构进阶：JSON Schema 必填字段校验器
工单：STARMIND-005
"""

"""Day 5 课后题 3：轻量级 JSON 响应结构校验器。"""

from typing import Dict, Any, Tuple, List, Type


def validate_payload(
    payload: Dict[str, Any], required_types: Dict[str, Type[Any]]
) -> Tuple[bool, List[str]]:
    """校验字典是否包含全部必填字段且满足类型要求。"""
    errors: List[str] = []
    for field, expected_type in required_types.items():
        if field not in payload:
            errors.append(f"缺少必填字段: {field}")
        elif not isinstance(payload[field], expected_type):
            actual = type(payload[field]).__name__
            errors.append(f"字段 {field} 类型错误: 期望 {expected_type.__name__}, 实际 {actual}")
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    schema = {"intent": str, "confidence": float, "need_human": bool}
    print("合法:", validate_payload({"intent": "退款", "confidence": 0.95, "need_human": False}, schema))
    print("异常:", validate_payload({"intent": "退款", "confidence": "高"}, schema))

