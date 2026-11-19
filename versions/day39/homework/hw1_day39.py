"""
Day 39 课后作业 1（基础巩固）：扩展企业日期工作日计算工具
工单：STARMIND-039
"""

"""Day 39 作业 1 参考答案：工作日计算工具。"""

from datetime import date, timedelta


def workday_counter(date_range: str) -> str:
    """计算起止日期（含两端）之间的周一至周五工作日天数。"""
    try:
        start_str, end_str = [p.strip() for p in date_range.split(",")]
        start = date.fromisoformat(start_str)
        end = date.fromisoformat(end_str)
        if end < start:
            return "错误：结束日期不能早于开始日期"
        days = 0
        cur = start
        while cur <= end:
            if cur.weekday() < 5:
                days += 1
            cur += timedelta(days=1)
        return f"{start_str} 至 {end_str} 共有 {days} 个工作日"
    except Exception as exc:
        return f"日期格式错误（期望 YYYY-MM-DD,YYYY-MM-DD）：{exc}"


if __name__ == "__main__":
    print(workday_counter("2026-05-01,2026-05-10"))
    assert "6 个工作日" in workday_counter("2026-05-01,2026-05-10")

