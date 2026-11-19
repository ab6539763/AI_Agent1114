"""
Day 50 课后作业 3（架构进阶）：对比两个版本的基准回归报告并自动检测性能/通过率劣化
工单：STARMIND-050
"""

"""Day 50 作业 3 参考答案：Agent CI 回归劣化自动门禁检测器。"""

from typing import Dict, Tuple


def check_regression(
    baseline: Dict[str, float],
    candidate: Dict[str, float],
    max_p95_increase_pct: float = 20.0,
) -> Tuple[bool, str]:
    if candidate["pass_rate_pct"] < baseline["pass_rate_pct"]:
        return False, f"通过率劣化: {baseline['pass_rate_pct']}% -> {candidate['pass_rate_pct']}%"
    base_p95 = max(baseline["p95_latency_ms"], 0.001)
    inc_pct = ((candidate["p95_latency_ms"] - base_p95) / base_p95) * 100.0
    if inc_pct > max_p95_increase_pct:
        return False, f"P95 延迟涨幅 {inc_pct:.1f}% 超过门禁阈值 {max_p95_increase_pct}%"
    return True, "PASS"


if __name__ == "__main__":
    base = {"pass_rate_pct": 100.0, "p95_latency_ms": 10.0}
    assert check_regression(base, {"pass_rate_pct": 100.0, "p95_latency_ms": 11.5})[0] is True
    assert check_regression(base, {"pass_rate_pct": 95.0, "p95_latency_ms": 10.0})[0] is False
    assert check_regression(base, {"pass_rate_pct": 100.0, "p95_latency_ms": 15.0})[0] is False
    print("CI 回归门禁检测通过")

