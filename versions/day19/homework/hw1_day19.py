"""
Day 19 课后作业 1（基础巩固）：为 ToolRegistry 新增企业货币汇率换算工具
工单：STARMIND-019
"""

import json
from src.day19_tool_registry import ToolSpec, build_default_registry

RATES_TO_CNY = {"CNY": 1.0, "USD": 7.25, "EUR": 7.85, "JPY": 0.048}


def convert_currency(amount: float, from_currency: str, to_currency: str):
    if from_currency not in RATES_TO_CNY or to_currency not in RATES_TO_CNY:
        raise ValueError("不支持的币种")
    cny = amount * RATES_TO_CNY[from_currency]
    converted = round(cny / RATES_TO_CNY[to_currency], 2)
    return {"status": "ok", "amount": amount, "from": from_currency, "to": to_currency, "converted": converted}


if __name__ == "__main__":
    reg = build_default_registry()
    reg.register(
        ToolSpec(
            name="convert_currency",
            description="进行常用企业外币汇率换算",
            parameters={
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_currency": {"type": "string", "enum": list(RATES_TO_CNY)},
                    "to_currency": {"type": "string", "enum": list(RATES_TO_CNY)},
                },
                "required": ["amount", "from_currency", "to_currency"],
            },
            handler=convert_currency,
        )
    )
    print(reg.execute("convert_currency", json.dumps({"amount": 100, "from_currency": "USD", "to_currency": "CNY"})))

