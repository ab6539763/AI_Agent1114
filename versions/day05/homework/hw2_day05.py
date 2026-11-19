"""
Day 05 课后作业 2（企业实战）：企业实战：多模型账单按部门分组汇总
工单：STARMIND-005
"""

"""Day 5 课后题 2：按部门汇总大模型 Token 消耗账单。"""

import json
from typing import List, Dict, Any


def aggregate_by_dept(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """按部门分组累加 Token 用量。"""
    totals: Dict[str, int] = {}
    for rec in records:
        dept = str(rec.get("dept", "未知部门"))
        tokens = int(rec.get("tokens", 0))
        totals[dept] = totals.get(dept, 0) + tokens
    return totals


if __name__ == "__main__":
    logs = [
        {"dept": "客服部", "tokens": 1200},
        {"dept": "研发部", "tokens": 3500},
        {"dept": "客服部", "tokens": 800},
    ]
    print(json.dumps(aggregate_by_dept(logs), ensure_ascii=False, indent=2))

