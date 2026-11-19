"""
Day 55 - 模块一：PagedAttention 分页显存 vs 传统连续预分配利用率模拟器
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List


@dataclass
class KVMemoryComparison:
    """KV Cache 显存分配效率对比"""
    num_requests: int
    total_actual_tokens: int
    naive_reserved_tokens: int
    paged_reserved_tokens: int
    naive_waste_ratio: float
    paged_waste_ratio: float
    memory_saved_ratio: float


def simulate_kv_cache_allocation(
    request_lengths: List[int],
    max_model_len: int = 4096,
    block_size: int = 16,
) -> KVMemoryComparison:
    """对比传统按 max_model_len 预分配与 PagedAttention 按 block_size 分页分配的显存开销"""
    if not request_lengths:
        raise ValueError("request_lengths 不能为空")

    total_actual = sum(request_lengths)
    naive_reserved = len(request_lengths) * max_model_len
    paged_reserved = sum(math.ceil(length / block_size) * block_size for length in request_lengths)

    naive_waste = round((naive_reserved - total_actual) / naive_reserved, 4)
    paged_waste = round((paged_reserved - total_actual) / paged_reserved, 4)
    saved_ratio = round((naive_reserved - paged_reserved) / naive_reserved, 4)

    return KVMemoryComparison(
        num_requests=len(request_lengths),
        total_actual_tokens=total_actual,
        naive_reserved_tokens=naive_reserved,
        paged_reserved_tokens=paged_reserved,
        naive_waste_ratio=naive_waste,
        paged_waste_ratio=paged_waste,
        memory_saved_ratio=saved_ratio,
    )


if __name__ == "__main__":
    sample_lens = [320, 510, 185, 920, 410, 260, 1240, 305, 680, 450]
    cmp = simulate_kv_cache_allocation(sample_lens, max_model_len=4096, block_size=16)
    print(f"传统连续分配浪费率: {cmp.naive_waste_ratio*100:.2f}%")
    print(f"PagedAttention浪费率: {cmp.paged_waste_ratio*100:.2f}%")
    print(f"KV Cache 显存直接节省: {cmp.memory_saved_ratio*100:.2f}%")

