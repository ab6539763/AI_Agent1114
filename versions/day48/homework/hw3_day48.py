"""
Day 48 课后作业 3（架构进阶）：将审计日志导出为按工具维度统计的调用报表
工单：STARMIND-048
"""

"""Day 48 作业 3 参考答案：企业办公工具审计日志聚合统计。"""

from collections import defaultdict
from typing import Dict, List


def summarize_audit_logs(logs: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "blocked": 0})
    for entry in logs:
        t = entry["tool"]
        stats[t]["total"] += 1
        if entry["status"] in ("REJECTED", "CONFLICT"):
            stats[t]["blocked"] += 1
    return dict(stats)


if __name__ == "__main__":
    sample = [
        {"tool": "calendar_tool", "status": "CONFLICT"},
        {"tool": "calendar_tool", "status": "OK"},
        {"tool": "email_draft_tool", "status": "REJECTED"},
    ]
    report = summarize_audit_logs(sample)
    print("审计汇总:", report)
    assert report["calendar_tool"] == {"total": 2, "blocked": 1}

