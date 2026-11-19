"""
Day 19 课后作业 2（企业实战）：Python 函数签名自动转 OpenAI Tool Schema 装饰器
工单：STARMIND-019
"""

import inspect
from typing import Any, Callable, Dict

PY_TO_JSON_TYPE = {str: "string", int: "integer", float: "number", bool: "boolean"}


def function_to_tool_schema(func: Callable[..., Any]) -> Dict[str, Any]:
    """根据函数签名与类型注解自动生成 OpenAI Function Calling Schema。"""
    sig = inspect.signature(func)
    properties: Dict[str, Any] = {}
    required = []
    for name, param in sig.parameters.items():
        json_type = PY_TO_JSON_TYPE.get(param.annotation, "string")
        properties[name] = {"type": json_type}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


def create_jira_ticket(title: str, priority: int = 2) -> dict:
    """在企业工单系统中创建一条新研发工单。"""
    return {"title": title, "priority": priority}


if __name__ == "__main__":
    print(function_to_tool_schema(create_jira_ticket))

