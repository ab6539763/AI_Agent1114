"""
Day 63 课后作业 1（基础巩固）：基础巩固：为压测报告增加 SLA 达标判定函数
工单：STARMIND-063
"""

from src.day63_load_and_cost_opt import LoadTestResult


def check_sla(res: LoadTestResult, max_p95_ms: float = 500.0, max_error_rate: float = 0.01) -> bool:
    return res.p95_ms <= max_p95_ms and res.error_rate <= max_error_rate


ok_res = LoadTestResult(100, 10, 100, 0.0, 220.0, 40.0, 180.0, 240.0)
bad_res = LoadTestResult(100, 10, 95, 0.05, 180.0, 50.0, 620.0, 900.0)
assert check_sla(ok_res) is True and check_sla(bad_res) is False
print("压测 SLA 门禁校验通过")

