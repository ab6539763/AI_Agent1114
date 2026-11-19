"""
Day 52 课后作业 3（架构进阶）：架构进阶：构建防灾难性遗忘的通用语料混洗采样器
工单：STARMIND-052
"""

import random
from typing import Dict, List


def mix_with_general_replay(
    domain_data: List[Dict[str, str]],
    general_data: List[Dict[str, str]],
    replay_ratio: float = 0.1,
    seed: int = 42,
) -> List[Dict[str, str]]:
    if not (0.0 <= replay_ratio < 0.5):
        raise ValueError("replay_ratio 建议控制在 [0, 0.5)")
    rng = random.Random(seed)
    need = int(len(domain_data) * replay_ratio / max(1e-6, 1.0 - replay_ratio))
    sampled_general = rng.sample(general_data, min(need, len(general_data)))
    mixed = list(domain_data) + sampled_general
    rng.shuffle(mixed)
    return mixed


res = mix_with_general_replay([{"id": i} for i in range(90)], [{"id": f"g{i}"} for i in range(50)], 0.1)
print(f"混洗后总样本数: {len(res)}")

