"""
Day 54 课后作业 3（架构进阶）：架构进阶：实现量化精度-显存-吞吐量三维权衡选型器
工单：STARMIND-054
"""

def select_quant_precision(params_b: float, vram_gb: float) -> str:
    budget = vram_gb * 0.70
    for name, bpp in [("BF16", 2.0), ("FP8", 1.05), ("AWQ-INT4", 0.60)]:
        if params_b * bpp <= budget:
            return f"推荐 {name}（权重约 {params_b * bpp:.1f}GB，为KV Cache预留 >=30% 显存）"
    return "单卡显存不足，请启用张量并行(Tensor Parallel)多卡部署"


for v in (24, 16, 8):
    print(f"7.6B @ {v}G ->", select_quant_precision(7.6, v))

