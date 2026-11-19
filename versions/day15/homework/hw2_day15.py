"""
Day 15 课后作业 2（企业实战）：Prompt Caching 缓存命中降本计算器
工单：STARMIND-015
"""

from typing import Dict


def calculate_cache_savings(
    input_tokens: int,
    output_tokens: int,
    input_price_per_1m: float,
    output_price_per_1m: float,
    monthly_calls: int,
    cache_ratio: float = 0.6,
    cache_discount: float = 0.2,
) -> Dict[str, float]:
    """计算开启前缀 Prompt Caching 后的月度成本与节省比例。"""
    base_single = (
        (input_tokens / 1_000_000) * input_price_per_1m
        + (output_tokens / 1_000_000) * output_price_per_1m
    )
    cached_in = input_tokens * cache_ratio
    uncached_in = input_tokens * (1.0 - cache_ratio)
    opt_single = (
        (cached_in / 1_000_000) * input_price_per_1m * cache_discount
        + (uncached_in / 1_000_000) * input_price_per_1m
        + (output_tokens / 1_000_000) * output_price_per_1m
    )
    base_monthly = round(base_single * monthly_calls, 2)
    opt_monthly = round(opt_single * monthly_calls, 2)
    saved = round(base_monthly - opt_monthly, 2)
    saved_pct = round((saved / base_monthly) * 100, 2) if base_monthly > 0 else 0.0
    return {
        "base_monthly_cny": base_monthly,
        "optimized_monthly_cny": opt_monthly,
        "saved_cny": saved,
        "saved_pct": saved_pct,
    }


if __name__ == "__main__":
    print(calculate_cache_savings(2000, 400, 2.0, 8.0, monthly_calls=200_000))

