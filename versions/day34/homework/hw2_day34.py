"""
Day 34 课后作业 2（企业实战）：作业二：实现回归退化检测器（Regression Guard）
工单：STARMIND-034
"""

"""Day 34 作业二参考答案：CI 回归退化守卫（Regression Guard）"""
from typing import Dict, List, Tuple


def check_regression(
    baseline: Dict[str, float],
    candidate: Dict[str, float],
    max_drop: float = 0.02,
) -> Tuple[bool, List[str]]:
    alerts: List[str] = []
    for metric, base_val in baseline.items():
        cand_val = candidate.get(metric, 0.0)
        drop = round(base_val - cand_val, 4)
        if drop > max_drop:
            alerts.append(f"{metric} 退化 {drop:.4f} (baseline={base_val} -> cand={cand_val})")
    return (len(alerts) > 0, alerts)


if __name__ == "__main__":
    base = {"faithfulness": 0.92, "context_recall": 0.90}
    cand_bad = {"faithfulness": 0.88, "context_recall": 0.93}
    blocked, msgs = check_regression(base, cand_bad, max_drop=0.02)
    print("是否阻断合并:", blocked, "告警:", msgs)
    assert blocked is True and "faithfulness" in msgs[0]

