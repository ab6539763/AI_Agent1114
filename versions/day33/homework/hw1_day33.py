"""
Day 33 课后作业 1（基础巩固）：作业一：实现自适应动态权重 RRF 融合器（Query 路由调权）
工单：STARMIND-033
"""

"""Day 33 作业一参考答案：自适应动态权重 RRF 路由器"""
import re
from typing import Tuple


def adaptive_rrf_weights(query: str) -> Tuple[float, float]:
    """返回 (bm25_weight, dense_weight)。"""
    has_code = bool(re.search(r"[A-Za-z]{2,}[-_][0-9]+|[A-Z]{3,}", query))
    if has_code:
        return (0.75, 0.25)
    return (0.35, 0.65)


if __name__ == "__main__":
    w1 = adaptive_rrf_weights("ERR-5042 网关超时咋处理")
    w2 = adaptive_rrf_weights("去魔都出差住店能报多少")
    print("错误码查询权重:", w1)
    print("口语语义查询权重:", w2)
    assert w1 == (0.75, 0.25) and w2 == (0.35, 0.65)

