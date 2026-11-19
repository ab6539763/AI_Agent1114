"""
Day 47 课后作业 1（基础巩固）：为 Text-to-SQL 增加表名白名单校验
工单：STARMIND-047
"""

"""Day 47 作业 1 参考答案：Text-to-SQL 表名白名单校验器。"""

import re
from typing import Set


def check_allowed_tables(sql: str, allowed_tables: Set[str]) -> bool:
    tables = re.findall(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
    return all(t.lower() in {a.lower() for a in allowed_tables} for t in tables)


if __name__ == "__main__":
    allowed = {"products", "sales_orders"}
    assert check_allowed_tables("SELECT * FROM sales_orders JOIN products ON 1=1", allowed) is True
    assert check_allowed_tables("SELECT * FROM hr_salaries", allowed) is False
    print("表名白名单校验通过")

