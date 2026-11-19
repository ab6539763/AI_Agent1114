"""
Day 54 - 模块二：LoRA 权重合并数学验证与 GPTQ/AWQ/GGUF 量化导出配置器
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

Matrix = List[List[float]]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """纯 Python 矩阵乘法"""
    rows, inner, cols = len(a), len(a[0]), len(b[0])
    return [
        [sum(a[i][k] * b[k][j] for k in range(inner)) for j in range(cols)]
        for i in range(rows)
    ]


def merge_lora_weights(
    w0: Matrix, lora_a: Matrix, lora_b: Matrix, lora_alpha: float, lora_rank: int
) -> Matrix:
    """计算合并权重 W_merged = W0 + (alpha / r) * (B @ A)"""
    scale = lora_alpha / float(lora_rank)
    delta = matmul(lora_b, lora_a)
    return [
        [w0[i][j] + scale * delta[i][j] for j in range(len(w0[0]))]
        for i in range(len(w0))
    ]


def verify_merge_equivalence(
    x: Matrix, w0: Matrix, lora_a: Matrix, lora_b: Matrix, lora_alpha: float, lora_rank: int
) -> float:
    """验证合并前(W0x + scale*B(Ax))与合并后(W_merged*x)的最大绝对误差"""
    scale = lora_alpha / float(lora_rank)
    base_y = matmul(w0, x)
    lora_y = matmul(lora_b, matmul(lora_a, x))
    unmerged_y = [
        [base_y[i][j] + scale * lora_y[i][j] for j in range(len(base_y[0]))]
        for i in range(len(base_y))
    ]
    w_merged = merge_lora_weights(w0, lora_a, lora_b, lora_alpha, lora_rank)
    merged_y = matmul(w_merged, x)

    max_err = max(
        abs(unmerged_y[i][j] - merged_y[i][j])
        for i in range(len(merged_y))
        for j in range(len(merged_y[0]))
    )
    return max_err


@dataclass
class QuantPlan:
    """量化方案推荐"""
    target_runtime: str
    quant_format: str
    estimated_size_gb: float
    export_yaml: str
    next_command: str


def build_export_and_quant_plan(
    base_model: str,
    adapter_path: str,
    export_dir: str,
    target_runtime: str = "vllm",  # "vllm" | "ollama"
    params_billion: float = 7.6,
) -> QuantPlan:
    """根据部署引擎生成 LLaMA-Factory 合并导出 YAML 与量化命令"""
    if target_runtime not in ("vllm", "ollama"):
        raise ValueError("target_runtime 仅支持 'vllm' 或 'ollama'")

    export_yaml = f"""### LLaMA-Factory 无损合并导出配置（严禁开启低比特量化参数）###
model_name_or_path: {base_model}
adapter_name_or_path: {adapter_path}
template: qwen
finetuning_type: lora
export_dir: {export_dir}
export_size: 4
export_device: cpu
export_legacy_format: false
"""
    if target_runtime == "vllm":
        return QuantPlan(
            target_runtime="vllm",
            quant_format="AWQ-INT4",
            estimated_size_gb=round(params_billion * 0.60, 2),
            export_yaml=export_yaml,
            next_command=f"autoawq --model {export_dir} --out {export_dir}-awq --bits 4 --group-size 128",
        )
    return QuantPlan(
        target_runtime="ollama",
        quant_format="GGUF-Q4_K_M",
        estimated_size_gb=round(params_billion * 0.62, 2),
        export_yaml=export_yaml,
        next_command=f"python llama.cpp/convert_hf_to_gguf.py {export_dir} --outtype q8_0 && llama-quantize model.gguf starmind-7b-q4_k_m.gguf Q4_K_M",
    )


if __name__ == "__main__":
    w0 = [[1.0, 0.5], [-0.2, 0.8]]
    a = [[0.1, 0.2]]
    b = [[0.3], [-0.4]]
    x = [[2.0], [3.0]]
    err = verify_merge_equivalence(x, w0, a, b, lora_alpha=2.0, lora_rank=1)
    print(f"LoRA 合并前后数值误差: {err:.2e}")
    plan = build_export_and_quant_plan("Qwen/Qwen2.5-7B-Instruct", "saves/lora_v1", "exports/starmind-7b", "vllm")
    print(f"推荐量化格式: {plan.quant_format}, 预估体积: {plan.estimated_size_gb} GB")

