"""
Day 34 课后作业 3（架构进阶）：作业三：实现评测结果 JSONL 审计日志归档与趋势追踪
工单：STARMIND-034
"""

"""Day 34 作业三参考答案：评测审计日志 JSONL 归档与趋势读取"""
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple


def append_eval_audit(log_path: Path, version: str, summary: Dict[str, float]) -> None:
    record = {"version": version, "summary": summary}
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_metric_trend(log_path: Path, metric: str) -> List[Tuple[str, float]]:
    trend: List[Tuple[str, float]] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        trend.append((obj["version"], float(obj["summary"][metric])))
    return trend


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "rag_eval_audit.jsonl"
        append_eval_audit(p, "v1.0", {"faithfulness": 0.65, "context_recall": 0.70})
        append_eval_audit(p, "v1.1", {"faithfulness": 0.86, "context_recall": 0.85})
        append_eval_audit(p, "v2.0", {"faithfulness": 0.95, "context_recall": 0.94})
        trend = load_metric_trend(p, "faithfulness")
        print("Faithfulness 迭代趋势:", trend)
        assert trend[-1][1] > trend[0][1]

