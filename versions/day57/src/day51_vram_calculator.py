"""
Day 51 - 模块二：大模型微调 GPU 显存精确估算器与国内算力选型工具
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ModelSpec:
    """主流开源大模型基础参数规格"""
    name: str
    params_billion: float   # 参数量(十亿), 如 Qwen2.5-7B 实际约 7.6B
    num_layers: int         # Transformer 层数
    hidden_size: int        # 隐藏层维度


MODEL_PRESETS: Dict[str, ModelSpec] = {
    "Qwen2.5-7B": ModelSpec("Qwen2.5-7B-Instruct", 7.6, 28, 3584),
    "Qwen2.5-14B": ModelSpec("Qwen2.5-14B-Instruct", 14.8, 48, 5120),
    "Llama3.1-8B": ModelSpec("Llama-3.1-8B-Instruct", 8.0, 32, 4096),
}

GPU_CATALOG: List[Dict[str, object]] = [
    {"name": "魔搭免费单卡 (A10/V100 16G)", "vram_gb": 16, "price_cny_per_hour": 0.0},
    {"name": "AutoDL RTX 4090 (24G)", "vram_gb": 24, "price_cny_per_hour": 2.0},
    {"name": "AutoDL A40 / L40S (48G)", "vram_gb": 48, "price_cny_per_hour": 5.5},
    {"name": "AutoDL A800 / A100 (80G)", "vram_gb": 80, "price_cny_per_hour": 9.8},
    {"name": "双卡 A800 (160G DeepSpeed)", "vram_gb": 160, "price_cny_per_hour": 19.6},
]


@dataclass
class VRAMBreakdown:
    """显存明细(单位: GB)"""
    model_name: str
    method: str
    weights_gb: float
    gradients_gb: float
    optimizer_gb: float
    activations_gb: float
    cuda_overhead_gb: float
    total_gb: float
    recommended_gpu: str
    estimated_cost_cny: float


def estimate_finetune_vram(
    model_key: str,
    method: str = "lora",           # "full" | "lora" | "qlora"
    batch_size: int = 2,
    seq_len: int = 2048,
    lora_rank: int = 16,
    gradient_checkpointing: bool = True,
    train_hours: float = 2.0,
) -> VRAMBreakdown:
    """精确估算大模型微调所需 GPU 显存(GB)及国内平台推荐"""
    if model_key not in MODEL_PRESETS:
        raise ValueError(f"不支持的模型预设: {model_key}，可选: {list(MODEL_PRESETS.keys())}")
    if method not in ("full", "lora", "qlora"):
        raise ValueError("method 必须是 'full'、'lora' 或 'qlora'")

    spec = MODEL_PRESETS[model_key]
    total_params = spec.params_billion * 1e9
    gb = 1024 ** 3

    # 1. 模型权重显存
    if method == "qlora":
        # 4-bit NF4 + 双重量化缩放常数，工程实测约 0.58 Bytes/参数
        weights_bytes = total_params * 0.58
    else:
        # BF16 / FP16: 2 Bytes/参数
        weights_bytes = total_params * 2.0

    # 2. 可训练参数比例与梯度/优化器显存
    if method == "full":
        trainable_params = total_params
        # 全量混合精度训练：BF16梯度(2B) + FP32主权重(4B) + AdamW一二阶矩(8B)
        gradients_bytes = trainable_params * 2.0
        optimizer_bytes = trainable_params * 12.0
    else:
        # LoRA 挂载全部线性层(q,k,v,o,gate,up,down)，可训练参数约 2 * 7 * L * hidden * r
        trainable_params = 2 * 7 * spec.num_layers * spec.hidden_size * lora_rank
        gradients_bytes = trainable_params * 2.0
        # QLoRA 通常搭配 paged_adamw_8bit (约 4B/可训练参数)，普通 LoRA 用 FP32 AdamW (12B)
        opt_bytes_per_param = 4.0 if method == "qlora" else 12.0
        optimizer_bytes = trainable_params * opt_bytes_per_param

    # 3. 激活值显存估算（经验工程公式，与 batch_size * seq_len * hidden * layers 成正比）
    # 开启梯度检查点(Gradient Checkpointing)时仅缓存每层输入，显存约降为原来的 28%
    raw_act_bytes = batch_size * seq_len * spec.hidden_size * spec.num_layers * 10
    act_factor = 0.28 if gradient_checkpointing else 1.0
    activations_bytes = raw_act_bytes * act_factor

    # 4. PyTorch + CUDA Context 固定缓冲开销
    cuda_overhead_gb = 1.4

    weights_gb = round(weights_bytes / gb, 2)
    gradients_gb = round(gradients_bytes / gb, 2)
    optimizer_gb = round(optimizer_bytes / gb, 2)
    activations_gb = round(activations_bytes / gb, 2)
    total_gb = round(
        weights_gb + gradients_gb + optimizer_gb + activations_gb + cuda_overhead_gb, 2
    )

    # 留出 12% 安全余量防止峰值抖动 OOM
    required_safe_gb = total_gb * 1.12
    matched_gpu = GPU_CATALOG[-1]
    for gpu in GPU_CATALOG:
        if float(gpu["vram_gb"]) >= required_safe_gb:
            matched_gpu = gpu
            break

    cost = round(float(matched_gpu["price_cny_per_hour"]) * train_hours, 2)
    return VRAMBreakdown(
        model_name=spec.name,
        method=method,
        weights_gb=weights_gb,
        gradients_gb=gradients_gb,
        optimizer_gb=optimizer_gb,
        activations_gb=activations_gb,
        cuda_overhead_gb=cuda_overhead_gb,
        total_gb=total_gb,
        recommended_gpu=str(matched_gpu["name"]),
        estimated_cost_cny=cost,
    )


if __name__ == "__main__":
    for m in ("full", "lora", "qlora"):
        res = estimate_finetune_vram("Qwen2.5-7B", method=m, batch_size=2, seq_len=2048)
        print(
            f"[{res.method.upper():5s}] 总显存={res.total_gb:6.2f} GB "
            f"(权重={res.weights_gb}G, 梯度={res.gradients_gb}G, 优化器={res.optimizer_gb}G, 激活={res.activations_gb}G) "
            f"-> 推荐: {res.recommended_gpu} (预计 {res.estimated_cost_cny} 元)"
        )

