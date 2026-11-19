"""
StarMind Day 16 - 步骤一：大模型 API 核心采样参数校验与数学模拟器
完整还原 frequency_penalty -> temperature -> softmax -> top_p 核采样管线。
"""

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class GenerationConfig:
    """大模型生成参数配置（对齐 OpenAI / DeepSeek Chat Completions 规范）。"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 512
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stream: bool = True

    def validate(self) -> None:
        """在发往模型网关前执行严格的参数边界校验。"""
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError(f"temperature 必须在 [0.0, 2.0] 之间，当前值: {self.temperature}")
        if not (0.0 < self.top_p <= 1.0):
            raise ValueError(f"top_p 必须在 (0.0, 1.0] 之间，当前值: {self.top_p}")
        if self.max_tokens < 1 or self.max_tokens > 32768:
            raise ValueError(f"max_tokens 必须在 [1, 32768] 之间，当前值: {self.max_tokens}")
        if not (-2.0 <= self.frequency_penalty <= 2.0):
            raise ValueError(f"frequency_penalty 必须在 [-2.0, 2.0] 之间")
        if not (-2.0 <= self.presence_penalty <= 2.0):
            raise ValueError(f"presence_penalty 必须在 [-2.0, 2.0] 之间")


# 企业常用场景预设参数
SCENE_PRESETS: Dict[str, GenerationConfig] = {
    "extraction": GenerationConfig(temperature=0.0, top_p=1.0, max_tokens=512, frequency_penalty=0.0),
    "customer_service": GenerationConfig(temperature=0.3, top_p=0.9, max_tokens=800, frequency_penalty=0.2),
    "creative_copy": GenerationConfig(temperature=0.9, top_p=0.95, max_tokens=1200, frequency_penalty=0.5),
}


def compute_token_probabilities(
    logits: Dict[str, float],
    config: GenerationConfig,
    token_counts: Dict[str, int] | None = None,
) -> Dict[str, float]:
    """
    执行完整的采样概率变换：
    1. 施加 frequency_penalty 与 presence_penalty
    2. 施加 temperature 缩放（T=0 时退化为贪婪独热分布）
    3. Softmax 归一化
    4. Top-P 核采样截断并重新归一化
    """
    config.validate()
    if not logits:
        raise ValueError("logits 候选词字典不能为空")

    counts = token_counts or {}
    adjusted: Dict[str, float] = {}
    for token, score in logits.items():
        cnt = counts.get(token, 0)
        penalized = score - cnt * config.frequency_penalty - (1 if cnt > 0 else 0) * config.presence_penalty
        adjusted[token] = penalized

    # 温度为 0：贪婪解码，直接把 100% 概率赋予最高分 Token
    if config.temperature == 0.0:
        best_token = max(adjusted.items(), key=lambda kv: kv[1])[0]
        return {best_token: 1.0}

    # 温度缩放 + 数值稳定 Softmax
    scaled = {tok: val / config.temperature for tok, val in adjusted.items()}
    max_val = max(scaled.values())
    exps = {tok: math.exp(val - max_val) for tok, val in scaled.items()}
    sum_exp = sum(exps.values())
    probs = {tok: e / sum_exp for tok, e in exps.items()}

    # Top-P 核采样：按概率降序累加，保留达到 top_p 阈值的核心候选集合
    sorted_items: List[Tuple[str, float]] = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)
    kept: Dict[str, float] = {}
    cumulative = 0.0
    for tok, p in sorted_items:
        kept[tok] = p
        cumulative += p
        if cumulative >= config.top_p:
            break

    # 对截断后的候选池重新归一化，保证概率之和严格为 1.0
    kept_sum = sum(kept.values())
    return {tok: p / kept_sum for tok, p in kept.items()}


def sample_next_token(
    logits: Dict[str, float],
    config: GenerationConfig,
    token_counts: Dict[str, int] | None = None,
    seed: int | None = None,
) -> Tuple[str, Dict[str, float]]:
    """按计算后的概率分布抽样一个 Token，返回 (选中Token, 最终概率分布)。"""
    probs = compute_token_probabilities(logits, config, token_counts)
    rng = random.Random(seed)
    tokens = list(probs.keys())
    weights = list(probs.values())
    chosen = rng.choices(tokens, weights=weights, k=1)[0]
    return chosen, probs


if __name__ == "__main__":
    demo_logits = {"稳定": 4.2, "高效": 3.8, "智能": 3.5, "神奇": 1.5, "离谱": 0.2}
    for name, cfg in [
        ("低温严谨 T=0.1", GenerationConfig(temperature=0.1, top_p=0.9)),
        ("高温创意 T=1.2", GenerationConfig(temperature=1.2, top_p=0.9)),
        ("复读惩罚 FP=1.5", GenerationConfig(temperature=0.7, top_p=0.9, frequency_penalty=1.5)),
    ]:
        dist = compute_token_probabilities(demo_logits, cfg, token_counts={"稳定": 2})
        pretty = {k: round(v, 4) for k, v in dist.items()}
        print(f"[{name}] -> {pretty}")

