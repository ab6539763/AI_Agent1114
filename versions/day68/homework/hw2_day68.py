"""
Day 68 课后作业 2（企业实战）：企业实战：计算多租户向量分片数量建议
工单：STARMIND-068
"""

import math


def recommend_shards(total_chunks: int, max_per_shard: int = 2_000_000) -> int:
    return max(1, math.ceil(total_chunks / max_per_shard))


assert recommend_shards(10_000_000) == 5
assert recommend_shards(500_000) == 1
print("向量分片数量规划通过")

