"""
Day 46 课后作业 3（架构进阶）：将 Trace 列表导出为按耗时排序的火焰图瓶颈报告
工单：STARMIND-046
"""

"""Day 46 作业 3 参考答案：Trace 耗时瓶颈 Top-K 分析器。"""

from typing import Dict, List


def find_slowest_spans(spans: List[Dict[str, object]], top_k: int = 2) -> List[Dict[str, object]]:
    total = sum(float(s["latency_ms"]) for s in spans) or 1.0
    ordered = sorted(spans, key=lambda s: float(s["latency_ms"]), reverse=True)[:top_k]
    return [
        {
            "name": s["name"],
            "latency_ms": s["latency_ms"],
            "pct": round(float(s["latency_ms"]) / total * 100, 1),
        }
        for s in ordered
    ]


if __name__ == "__main__":
    sample = [
        {"name": "guardrail", "latency_ms": 2.0},
        {"name": "llm_plan", "latency_ms": 480.0},
        {"name": "sql_tool", "latency_ms": 118.0},
    ]
    top2 = find_slowest_spans(sample, top_k=2)
    print("Top-2 瓶颈:", top2)
    assert top2[0]["name"] == "llm_plan" and top2[0]["pct"] == 80.0

