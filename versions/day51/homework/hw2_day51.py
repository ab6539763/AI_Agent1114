"""
Day 51 课后作业 2（企业实战）：企业实战：多卡 DeepSpeed ZeRO-2 / ZeRO-3 显存分摊计算
工单：STARMIND-051
"""

from src.day51_vram_calculator import estimate_finetune_vram


def estimate_zero_per_gpu_vram(model_key: str, num_gpus: int, zero_stage: int) -> float:
    """估算 DeepSpeed ZeRO-2 / ZeRO-3 下的单卡显存占用(GB)"""
    if num_gpus < 1 or zero_stage not in (2, 3):
        raise ValueError("num_gpus>=1 且 zero_stage 需为 2 或 3")
    base = estimate_finetune_vram(model_key, method="full", batch_size=1, seq_len=2048)
    if zero_stage == 2:
        per_gpu = base.weights_gb + (base.gradients_gb + base.optimizer_gb) / num_gpus
    else:
        per_gpu = (base.weights_gb + base.gradients_gb + base.optimizer_gb) / num_gpus
    return round(per_gpu + base.activations_gb + base.cuda_overhead_gb, 2)


if __name__ == "__main__":
    for stage in (2, 3):
        print(f"Qwen2.5-7B 4卡 ZeRO-{stage} 单卡显存: {estimate_zero_per_gpu_vram('Qwen2.5-7B', 4, stage)} GB")

