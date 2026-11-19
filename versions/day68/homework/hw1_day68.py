"""
Day 68 课后作业 1（基础巩固）：基础巩固：比较 1 万 / 10 万 / 50 万 DAU 三个规模下的 GPU 需求曲线
工单：STARMIND-068
"""

from src.day68_capacity_estimator import ScaleSpec, estimate_capacity

for d in (10_000, 100_000, 500_000):
    r = estimate_capacity(ScaleSpec(dau=d))
    print(f"DAU={d:>7} -> Peak QPS={r.peak_qps:>6}, GPUs={r.required_gpus}, 月混合成本={r.monthly_hybrid_cny}")

