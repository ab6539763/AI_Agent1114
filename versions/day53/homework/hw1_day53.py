"""
Day 53 课后作业 1（基础巩固）：基础巩固：为 YAML 生成器新增 DeepSpeed ZeRO-2 选项
工单：STARMIND-053
"""

from src.day53_llamafactory_config import LoRATrainPlan, validate_and_render_yaml


def render_with_deepspeed(plan: LoRATrainPlan) -> str:
    base_yaml = validate_and_render_yaml(plan)
    if plan.num_gpus >= 2:
        base_yaml += "deepspeed: examples/deepspeed/ds_z2_config.json\n"
    return base_yaml


out = render_with_deepspeed(LoRATrainPlan(num_gpus=2))
assert "ds_z2_config.json" in out
print("双卡 DeepSpeed 配置追加成功！")

