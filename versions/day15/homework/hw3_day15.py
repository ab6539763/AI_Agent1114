"""
Day 15 课后作业 3（架构进阶）：因果掩码（Causal Mask）自注意力实现
工单：STARMIND-015
"""

import math
from typing import List


def causal_self_attention_weights(
    queries: List[List[float]],
    keys: List[List[float]],
) -> List[List[float]]:
    """计算带因果掩码（上三角屏蔽）的自注意力权重矩阵。"""
    d_k = len(queries[0])
    scale = math.sqrt(d_k)
    weights_matrix: List[List[float]] = []

    for i, q_vec in enumerate(queries):
        scores = []
        for j, k_vec in enumerate(keys):
            if j > i:
                scores.append(-1e9)
            else:
                dot = sum(a * b for a, b in zip(q_vec, k_vec))
                scores.append(dot / scale)
        max_s = max(scores)
        exps = [math.exp(s - max_s) for s in scores]
        total = sum(exps)
        weights_matrix.append([e / total for e in exps])

    return weights_matrix


if __name__ == "__main__":
    vecs = [[1.0, 0.5], [0.4, 0.9], [0.8, 0.2]]
    w = causal_self_attention_weights(vecs, vecs)
    for idx, row in enumerate(w):
        print(f"Token {idx} 注意力分布:", [round(x, 4) for x in row])

