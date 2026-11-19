"""
Day 51 课后作业 1（基础巩固）：基础巩固：扩展 Qwen2.5-32B 模型规格并对比 QLoRA 显存
工单：STARMIND-051
"""

from src.day51_vram_calculator import MODEL_PRESETS, ModelSpec, estimate_finetune_vram

MODEL_PRESETS["Qwen2.5-32B"] = ModelSpec("Qwen2.5-32B-Instruct", 32.5, 64, 5120)

for method in ("lora", "qlora"):
    res = estimate_finetune_vram("Qwen2.5-32B", method=method, batch_size=1, seq_len=4096)
    fits_4090 = res.total_gb * 1.12 <= 24.0
    print(f"32B {method.upper()}: 总显存={res.total_gb}GB, 单卡4090能否运行={fits_4090}, 推荐={res.recommended_gpu}")

