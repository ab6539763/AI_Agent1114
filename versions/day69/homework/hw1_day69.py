"""
Day 69 课后作业 1（基础巩固）：基础巩固：计算多次模拟面试的进步趋势（Score Delta）
工单：STARMIND-069
"""

def calc_progress(r1: dict[str, float], r2: dict[str, float]) -> dict[str, float]:
    return {k: round(r2[k] - r1[k], 2) for k in r1}


diff = calc_progress({"coding": 58, "design": 70}, {"coding": 82, "design": 84})
assert diff == {"coding": 24, "design": 14}
print("二轮模拟提分统计通过:", diff)

