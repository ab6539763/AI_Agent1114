"""
Day 55 课后作业 1（基础巩固）：基础巩固：为压测报告增加 SLA 自动达标判定函数
工单：STARMIND-055
"""

from src.day55_inference_benchmark import BenchmarkSummary


def check_sla(
    summary: BenchmarkSummary,
    max_p95_ttft_ms: float = 1500.0,
    min_tps: float = 40.0,
    min_success_rate: float = 0.99,
):
    reasons = []
    if summary.p95_ttft_ms > max_p95_ttft_ms:
        reasons.append(f"P95 TTFT({summary.p95_ttft_ms}ms) 超出 SLA({max_p95_ttft_ms}ms)")
    if summary.throughput_tokens_per_sec < min_tps:
        reasons.append(f"吞吐({summary.throughput_tokens_per_sec}) 低于 SLA({min_tps})")
    if summary.success_rate < min_success_rate:
        reasons.append(f"成功率({summary.success_rate}) 低于 SLA({min_success_rate})")
    return len(reasons) == 0, reasons


demo = BenchmarkSummary(10, 5, 1.0, 20.0, 35.0, 4.0, 320.0, 0.5)
print(check_sla(demo))

