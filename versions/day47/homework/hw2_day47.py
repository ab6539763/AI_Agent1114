"""
Day 47 课后作业 2（企业实战）：实现 Text-to-SQL 结果集行数截断与列脱敏
工单：STARMIND-047
"""

"""Day 47 作业 2 参考答案：SQL 结果集敏感列自动脱敏。"""

from typing import Any, Dict, List, Set


def mask_sensitive_columns(rows: List[Dict[str, Any]], sensitive_cols: Set[str]) -> List[Dict[str, Any]]:
    return [
        {k: ("***" if k.lower() in sensitive_cols else v) for k, v in row.items()}
        for row in rows
    ]


if __name__ == "__main__":
    raw = [{"customer": "星辰客户A", "phone": "13800138000", "amount": 50000}]
    safe = mask_sensitive_columns(raw, {"phone", "email"})
    print(safe)
    assert safe[0]["phone"] == "***" and safe[0]["amount"] == 50000

