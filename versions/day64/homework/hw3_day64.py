"""
Day 64 课后作业 3（架构进阶）：架构进阶：设计灰度发布流量比例校验器（10% -> 50% -> 100%）
工单：STARMIND-064
"""

def next_canary_stage(current_pct: int, error_rate: float) -> int:
    if error_rate > 0.01:
        return 0
    steps = {0: 10, 10: 50, 50: 100, 100: 100}
    return steps.get(current_pct, 0)


assert next_canary_stage(10, 0.002) == 50
assert next_canary_stage(50, 0.03) == 0
print("灰度放量与自动回滚状态机通过")

