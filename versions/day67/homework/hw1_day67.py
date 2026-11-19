"""
Day 67 课后作业 1（基础巩固）：基础巩固：手写 Top-K 采样过滤器
工单：STARMIND-067
"""

from src.day67_handwritten_transformer import stable_softmax


def top_k_filter(logits: dict[str, float], k: int) -> dict[str, float]:
    top = sorted(logits.items(), key=lambda x: x[1], reverse=True)[:k]
    probs = stable_softmax([v for _, v in top])
    return {tok: round(p, 6) for (tok, _), p in zip(top, probs)}


res = top_k_filter({"a": 3.0, "b": 2.0, "c": 1.0, "d": -2.0}, k=2)
assert set(res.keys()) == {"a", "b"} and abs(sum(res.values()) - 1.0) < 1e-5
print("Top-K 过滤通过:", res)

