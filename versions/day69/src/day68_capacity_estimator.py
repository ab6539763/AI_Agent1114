"""
Day 68 - 模块一：十万 DAU 企业级 RAG + Agent 平台系统设计容量与成本估算引擎
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class ScaleSpec:
    dau: int = 100_000
    queries_per_user_day: float = 10.0
    peak_factor: float = 5.0
    cache_hit_rate: float = 0.35
    avg_tokens_per_query: int = 2000
    total_chunks: int = 10_000_000
    embedding_dim: int = 1024
    use_sq8_quant: bool = True
    single_gpu_tps: float = 1500.0  # 单张 A100/L40S 跑 7B vLLM 吞吐估算(tokens/s)
    local_route_ratio: float = 0.70


@dataclass
class CapacityReport:
    daily_requests: int
    avg_qps: float
    peak_qps: float
    llm_peak_qps: float
    vector_ram_gb: float
    required_gpus: int
    monthly_cloud_only_cny: float
    monthly_hybrid_cny: float


def estimate_capacity(spec: ScaleSpec) -> CapacityReport:
    daily_reqs = int(spec.dau * spec.queries_per_user_day)
    avg_qps = daily_reqs / 86400.0
    peak_qps = avg_qps * spec.peak_factor
    llm_peak_qps = peak_qps * (1.0 - spec.cache_hit_rate)

    # 向量内存估算：FP32 为 4 bytes/dim，SQ8 标量量化为 1 byte/dim，HNSW 图索引开销约 1.5x
    bytes_per_dim = 1 if spec.use_sq8_quant else 4
    raw_bytes = spec.total_chunks * spec.embedding_dim * bytes_per_dim * 1.5
    vector_ram_gb = round(raw_bytes / (1024 ** 3), 2)

    # 本地 7B 峰值输出吞吐需求（按总 token 的 30% 为输出 decode token 估算 + 30% 冗余）
    local_peak_decode_tps = llm_peak_qps * spec.local_route_ratio * (spec.avg_tokens_per_query * 0.30)
    required_gpus = max(1, math.ceil((local_peak_decode_tps * 1.3) / max(1.0, spec.single_gpu_tps)))

    # 月度成本对比（云旗舰均价 0.02 元/千Token；单 GPU 月租 6000 元）
    monthly_tokens_k = (daily_reqs * 30 * spec.avg_tokens_per_query) / 1000.0
    cloud_only_cny = round(monthly_tokens_k * 0.02, 2)
    hybrid_cloud_part = monthly_tokens_k * (1.0 - spec.cache_hit_rate) * (1.0 - spec.local_route_ratio) * 0.02
    hybrid_cny = round(hybrid_cloud_part + required_gpus * 6000.0, 2)

    return CapacityReport(
        daily_requests=daily_reqs,
        avg_qps=round(avg_qps, 2),
        peak_qps=round(peak_qps, 2),
        llm_peak_qps=round(llm_peak_qps, 2),
        vector_ram_gb=vector_ram_gb,
        required_gpus=required_gpus,
        monthly_cloud_only_cny=cloud_only_cny,
        monthly_hybrid_cny=hybrid_cny,
    )


if __name__ == "__main__":
    rep = estimate_capacity(ScaleSpec())
    print("十万 DAU 容量估算报告:", rep)

