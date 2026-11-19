"""
Day 38 课后作业 2（企业实战）：作业二：实现慢查询日志采集器（SlowQueryLogger）
工单：STARMIND-038
"""

"""Day 38 作业二参考答案：生产慢查询采集与 Top-N 分析器"""
from typing import Dict, List


class SlowQueryLogger:
    def __init__(self, threshold_ms: float = 50.0) -> None:
        self.threshold_ms = threshold_ms
        self.records: List[Dict[str, object]] = []

    def record(self, query: str, latency_ms: float) -> None:
        if latency_ms >= self.threshold_ms:
            self.records.append({"query": query, "latency_ms": round(latency_ms, 2)})

    def top_slowest(self, n: int = 3) -> List[Dict[str, object]]:
        return sorted(self.records, key=lambda x: float(x["latency_ms"]), reverse=True)[:n]


if __name__ == "__main__":
    logger = SlowQueryLogger(threshold_ms=50.0)
    logger.record("年假几天", 12.5)
    logger.record("复杂跨部门长问题1", 180.4)
    logger.record("复杂跨部门长问题2", 320.8)
    top = logger.top_slowest(2)
    print("Top-2 慢查询:", top)
    assert len(top) == 2 and top[0]["latency_ms"] == 320.8

