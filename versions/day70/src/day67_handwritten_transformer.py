"""
Day 67 - 模块一：面试高频手撕——数值稳定 Softmax、Scaled Dot-Product Attention 与 Top-P 采样
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple


def stable_softmax(scores: List[float]) -> List[float]:
    """数值稳定 Softmax：减去最大值防止 exp 溢出；支持 -inf 掩码位"""
    finite = [s for s in scores if not math.isinf(s)]
    if not finite:
        return [0.0 for _ in scores]
    m = max(finite)
    exps = [0.0 if (math.isinf(s) and s < 0) else math.exp(s - m) for s in scores]
    denom = sum(exps)
    return [e / denom for e in exps]


def scaled_dot_product_attention(
    Q: List[List[float]],
    K: List[List[float]],
    V: List[List[float]],
    causal_mask: bool = True,
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    纯 Python 实现 Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k) + mask) V
    返回: (output_matrix, attention_weights)
    """
    seq_len = len(Q)
    d_k = len(Q[0])
    d_v = len(V[0])
    scale = math.sqrt(d_k)

    weights: List[List[float]] = []
    for i in range(seq_len):
        row_scores: List[float] = []
        for j in range(seq_len):
            if causal_mask and j > i:
                row_scores.append(float("-inf"))
            else:
                dot = sum(Q[i][k] * K[j][k] for k in range(d_k))
                row_scores.append(dot / scale)
        weights.append(stable_softmax(row_scores))

    output: List[List[float]] = []
    for i in range(seq_len):
        vec = [0.0] * d_v
        for j in range(seq_len):
            w = weights[i][j]
            for d in range(d_v):
                vec[d] += w * V[j][d]
        output.append([round(x, 6) for x in vec])
    return output, weights


def top_p_filter(logits: Dict[str, float], top_p: float = 0.9, temperature: float = 1.0) -> Dict[str, float]:
    """Top-P (Nucleus) 核采样概率截断与重归一化"""
    if temperature <= 0:
        best_tok = max(logits.items(), key=lambda x: x[1])[0]
        return {best_tok: 1.0}

    tokens = list(logits.keys())
    probs = stable_softmax([logits[t] / temperature for t in tokens])
    ranked = sorted(zip(tokens, probs), key=lambda x: x[1], reverse=True)

    kept: List[Tuple[str, float]] = []
    cum = 0.0
    for tok, p in ranked:
        kept.append((tok, p))
        cum += p
        if cum >= top_p:
            break

    total = sum(p for _, p in kept)
    return {tok: round(p / total, 6) for tok, p in kept}


if __name__ == "__main__":
    Q = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    K = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    V = [[10.0, 0.0], [0.0, 20.0], [5.0, 5.0]]
    out, attn = scaled_dot_product_attention(Q, K, V, causal_mask=True)
    print("因果注意力权重行0:", attn[0])
    print("注意力输出:", out)
    print("Top-P=0.8 截断结果:", top_p_filter({"星": 3.0, "辰": 2.2, "智": 0.5, "脑": -1.0}, top_p=0.8))

