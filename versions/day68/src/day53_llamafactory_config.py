"""
Day 53 - 模块一：LLaMA-Factory LoRA 微调 YAML 配置生成器（带防呆校验）
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict

MODEL_TEMPLATE_MAP: Dict[str, str] = {
    "Qwen/Qwen2.5-7B-Instruct": "qwen",
    "Qwen/Qwen2.5-14B-Instruct": "qwen",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": "deepseek3",
    "meta-llama/Meta-Llama-3.1-8B-Instruct": "llama3",
}


@dataclass
class LoRATrainPlan:
    """微调训练超参计划"""
    model_name_or_path: str = "Qwen/Qwen2.5-7B-Instruct"
    dataset_name: str = "starmind_cs_alpaca"
    dataset_size: int = 450
    output_dir: str = "saves/qwen2.5-7b/lora/starmind_cs_v1"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    learning_rate: float = 1e-4
    num_train_epochs: float = 4.0
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    num_gpus: int = 1
    cutoff_len: int = 2048
    use_qlora_4bit: bool = False


def validate_and_render_yaml(plan: LoRATrainPlan) -> str:
    """校验超参合理性并渲染标准 LLaMA-Factory YAML 配置"""
    if plan.model_name_or_path not in MODEL_TEMPLATE_MAP:
        raise ValueError(f"未注册的模型模板映射: {plan.model_name_or_path}")
    if not (1e-5 <= plan.learning_rate <= 5e-4):
        raise ValueError(
            f"LoRA 学习率 {plan.learning_rate} 超出安全区间 [1e-5, 5e-4]，易导致欠拟合或梯度爆炸"
        )
    if plan.lora_rank <= 0 or plan.lora_alpha < plan.lora_rank:
        raise ValueError("lora_rank 必须为正整数，且建议 lora_alpha >= lora_rank")

    template = MODEL_TEMPLATE_MAP[plan.model_name_or_path]
    ebs = plan.per_device_train_batch_size * plan.gradient_accumulation_steps * plan.num_gpus
    steps_per_epoch = max(1, math.ceil(plan.dataset_size / ebs))
    total_steps = int(steps_per_epoch * plan.num_train_epochs)
    eval_steps = max(10, total_steps // 6)

    quant_block = "quantization_bit: 4\nquantization_method: bitsandbytes\n" if plan.use_qlora_4bit else ""

    yaml_text = f"""### 自动生成：星辰智脑 LLaMA-Factory LoRA 微调配置 ###
### 预估 Effective Batch Size = {ebs}, 总步数 ≈ {total_steps} steps ###

### model
model_name_or_path: {plan.model_name_or_path}
{quant_block}trust_remote_code: true

### method
stage: sft
do_train: true
finetuning_type: lora
lora_rank: {plan.lora_rank}
lora_alpha: {plan.lora_alpha}
lora_dropout: {plan.lora_dropout}
lora_target: all

### dataset
dataset: {plan.dataset_name}
template: {template}
cutoff_len: {plan.cutoff_len}
overwrite_cache: true
preprocessing_num_workers: 4

### output
output_dir: {plan.output_dir}
logging_steps: 5
save_steps: {eval_steps}
plot_loss: true
overwrite_output_dir: true

### train
per_device_train_batch_size: {plan.per_device_train_batch_size}
gradient_accumulation_steps: {plan.gradient_accumulation_steps}
learning_rate: {plan.learning_rate:.1e}
num_train_epochs: {plan.num_train_epochs}
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
gradient_checkpointing: true

### eval
val_size: 0.1
per_device_eval_batch_size: 2
eval_strategy: steps
eval_steps: {eval_steps}
load_best_model_at_end: true
"""
    return yaml_text


if __name__ == "__main__":
    cfg = validate_and_render_yaml(LoRATrainPlan())
    print(cfg)

