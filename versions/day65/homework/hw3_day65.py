"""
Day 65 课后作业 3（架构进阶）：架构进阶：统计多轮彩排的演示稳定性（Live 成功率）
工单：STARMIND-065
"""

from src.day65_live_demo_runner import DemoStepOutcome


def calc_live_stability(outcomes: list[DemoStepOutcome]) -> float:
    ok = sum(1 for o in outcomes if o.mode == "LIVE" and o.passed)
    return round(ok / max(1, len(outcomes)), 4)


res = calc_live_stability([
    DemoStepOutcome("s1", "LIVE", "ok", True),
    DemoStepOutcome("s2", "LIVE", "ok", True),
    DemoStepOutcome("s3", "FALLBACK", "ok", True),
])
assert res == 0.6667
print("彩排实时稳定性评估:", res)

