"""
Day 16 课后作业 1（基础巩固）：Top-K 采样过滤器实现
工单：STARMIND-016
"""

import math
from typing import Dict


def top_k_probs(logits: Dict[str, float], k: int, temperature: float = 1.0) -> Dict[str, float]:
    """Top-K 截断 + 温度 Softmax 概率计算。"""
    if k < 1:
        raise ValueError("k 必须 >= 1")
    if temperature <= 0:
        raise ValueError("temperature 必须 > 0")
    top_items = sorted(logits.items(), key=lambda kv: kv[1], reverse=True)[:k]
    scaled = {tok: score / temperature for tok, score in top_items}
    max_s = max(scaled.values())
    exps = {tok: math.exp(val - max_s) for tok, val in scaled.items()}
    total = sum(exps.values())
    return {tok: e / total for tok, e in exps.items()}


if __name__ == "__main__":
    print(top_k_probs({"猫": 4.0, "狗": 3.5, "鸟": 2.0, "石头": 0.1}, k=2, temperature=0.8))

