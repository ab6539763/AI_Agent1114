"""
Day 53 课后作业 2（企业实战）：企业实战：解析真实 LLaMA-Factory 的 trainer_log.jsonl 并诊断
工单：STARMIND-053
"""

import json
from src.day53_loss_diagnostics import LossPoint, diagnose_loss_curve


def parse_and_diagnose_jsonl(jsonl_text: str):
    points = []
    last_train = None
    for line in jsonl_text.strip().splitlines():
        row = json.loads(line)
        if "loss" in row:
            last_train = float(row["loss"])
        if "eval_loss" in row and last_train is not None:
            points.append(LossPoint(int(row["current_steps"]), last_train, float(row["eval_loss"])))
    return diagnose_loss_curve(points)


sample_log = """
{"current_steps": 40, "loss": 2.1}
{"current_steps": 40, "eval_loss": 2.15}
{"current_steps": 80, "loss": 1.2}
{"current_steps": 80, "eval_loss": 1.28}
{"current_steps": 120, "loss": 0.75}
{"current_steps": 120, "eval_loss": 0.92}
"""
print(parse_and_diagnose_jsonl(sample_log))

