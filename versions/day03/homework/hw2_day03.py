"""
Day 03 课后作业 2（企业实战）：企业实战：Token 预算水位监控器
工单：STARMIND-003
"""

"""Day 3 课后题 2：月度 Token 预算熔断监控器。"""

from typing import List, Dict


def consume_budget(costs: List[int], budget: int) -> Dict[str, int]:
    """按顺序扣减 Token 预算，即将超限时停止执行。"""
    spent = 0
    processed = 0
    for cost in costs:
        if cost < 0:
            continue
        if spent + cost > budget:
            break
        spent += cost
        processed += 1
    return {"processed": processed, "spent": spent, "remaining": budget - spent}


if __name__ == "__main__":
    print(consume_budget([3000, 4000, 5000, 2000], budget=10000))

