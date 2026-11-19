"""
Day 50 课后作业 2（企业实战）：将答辩 SLA 评估报告自动渲染为 Markdown 结项表格
工单：STARMIND-050
"""

"""Day 50 作业 2 参考答案：答辩 SLA 报告 Markdown 自动渲染器。"""

from typing import Any, Dict, List


def render_sla_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = [
        "### 项目三答辩 SLA 验收报告",
        f"- 通过率：**{report['pass_rate_pct']}%** ({report['passed_cases']}/{report['total_cases']})",
        f"- P95 延迟：**{report['p95_latency_ms']} ms**",
        "",
        "| 用例 | 预期状态 | 实际状态 | 结果 |",
        "|---|---|---|---|",
    ]
    for d in report["details"]:
        badge = "PASS" if d["passed"] else "FAIL"
        lines.append(f"| {d['case_id']} | {d['expected']} | {d['actual']} | {badge} |")
    return "\n".join(lines)


if __name__ == "__main__":
    sample = {
        "total_cases": 1,
        "passed_cases": 1,
        "pass_rate_pct": 100.0,
        "p95_latency_ms": 1.2,
        "details": [{"case_id": "C1", "expected": "COMPLETED", "actual": "COMPLETED", "passed": True}],
    }
    md = render_sla_markdown(sample)
    print(md)
    assert "| C1 | COMPLETED | COMPLETED | PASS |" in md

