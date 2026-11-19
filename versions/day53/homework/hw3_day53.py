"""
Day 53 课后作业 3（架构进阶）：架构进阶：实现 Cosine Learning Rate Scheduler 模拟曲线
工单：STARMIND-053
"""

import math


def cosine_lr(step: int, total_steps: int, base_lr: float, warmup_ratio: float = 0.1) -> float:
    warmup_steps = max(1, int(total_steps * warmup_ratio))
    if step < warmup_steps:
        return base_lr * (step / warmup_steps)
    progress = min(1.0, (step - warmup_steps) / max(1, total_steps - warmup_steps))
    return 0.5 * base_lr * (1.0 + math.cos(math.pi * progress))


for s in (0, 10, 20, 100, 200):
    print(f"step={s:3d} -> lr={cosine_lr(s, 200, 1e-4):.6e}")

