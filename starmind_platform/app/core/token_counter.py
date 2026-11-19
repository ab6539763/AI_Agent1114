"""
中英文 Token 估算器与 API 人民币成本核算器模块。

说明：
1. 在无需下载 tiktoken 词表（离线/私有化内网环境）的前提下，
   基于中文汉字约 0.65~0.85 Token/字、英文约 0.28 Token/字符、数字/标点约 0.5 Token 的工程经验公式，
   提供高精度 Token 估算。
2. 内置国内企业常用主流大模型（DeepSeek-V3 / DeepSeek-R1 / Qwen-Max / Qwen-Plus / GPT-4o / local_mock）
   每百万 Token 人民币（CNY）实时参考单价，用于企业级 FinOps 成本分摊与预算告警。
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Tuple

# 主流大模型参考单价表：单位为 人民币元 / 百万 Token (input_cny_per_1m, output_cny_per_1m)
MODEL_PRICING_CNY_PER_1M: Dict[str, Tuple[float, float]] = {
    "deepseek-chat": (2.0, 8.0),          # DeepSeek-V3 标准价
    "deepseek-v3": (2.0, 8.0),            # DeepSeek-V3 别名
    "deepseek-reasoner": (4.0, 16.0),     # DeepSeek-R1 推理模型
    "deepseek-r1": (4.0, 16.0),           # DeepSeek-R1 别名
    "qwen-max": (20.0, 60.0),             # 通义千问 Qwen-Max
    "qwen-plus": (0.8, 2.0),              # 通义千问 Qwen-Plus
    "qwen-turbo": (0.3, 0.6),             # 通义千问 Qwen-Turbo
    "gpt-4o": (18.0, 72.0),               # OpenAI GPT-4o (折合人民币)
    "gpt-4o-mini": (1.1, 4.4),            # OpenAI GPT-4o-mini
    "local_mock": (0.0, 0.0),             # 本地模拟引擎零成本
}

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_ASCII_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class CostEstimate:
    """单次大模型调用的 Token 统计与人民币成本核算结果。"""

    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost_cny: float
    output_cost_cny: float
    total_cost_cny: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "input_cost_cny": round(self.input_cost_cny, 6),
            "output_cost_cny": round(self.output_cost_cny, 6),
            "total_cost_cny": round(self.total_cost_cny, 6),
        }


class TokenCounter:
    """中英文混合文本 Token 估算与成本核算工具类。"""

    @staticmethod
    def count_text(text: str) -> int:
        """
        估算单段文本的 Token 数量。
        算法思路：
        - 每个中文汉字按 0.85 Token 估算（涵盖 DeepSeek/Qwen BPE 词表特点）；
        - 每个英文/数字连续词按 `max(1, ceil(len(word) / 4))` 估算；
        - 其余标点、换行与特殊符号按 0.5 Token 估算。
        """
        if not text:
            return 0

        cjk_chars = len(_CJK_RE.findall(text))
        ascii_words = _ASCII_WORD_RE.findall(text)
        ascii_tokens = sum(max(1, math.ceil(len(w) / 4)) for w in ascii_words)
        ascii_char_count = sum(len(w) for w in ascii_words)
        other_chars = max(0, len(text) - cjk_chars - ascii_char_count)

        estimated = cjk_chars * 0.85 + ascii_tokens + other_chars * 0.5
        return max(1, int(math.ceil(estimated)))

    @classmethod
    def count_messages(cls, messages: Iterable[Dict[str, Any]]) -> int:
        """
        估算 OpenAI 格式多轮对话消息列表的总 Token 数（包含每条消息约 4 Token 的角色封装开销）。
        """
        total = 3  # 对话回复引导头开销
        for msg in messages:
            total += 4
            content = msg.get("content") or ""
            if isinstance(content, str):
                total += cls.count_text(content)
            else:
                total += cls.count_text(str(content))
            if msg.get("name"):
                total += 1
        return total

    @staticmethod
    def resolve_pricing(model: str) -> Tuple[float, float]:
        """根据模型名称匹配每百万 Token 人民币单价（支持模糊前缀匹配）。"""
        key = (model or "deepseek-chat").strip().lower()
        if key in MODEL_PRICING_CNY_PER_1M:
            return MODEL_PRICING_CNY_PER_1M[key]
        for known, price in MODEL_PRICING_CNY_PER_1M.items():
            if known in key:
                return price
        # 默认按 DeepSeek-V3 口径估算
        return MODEL_PRICING_CNY_PER_1M["deepseek-chat"]

    @classmethod
    def estimate_cost(
        cls,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> CostEstimate:
        """计算单次调用的人民币费用明细。"""
        in_price, out_price = cls.resolve_pricing(model)
        input_cost = (prompt_tokens / 1_000_000.0) * in_price
        output_cost = (completion_tokens / 1_000_000.0) * out_price
        return CostEstimate(
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            input_cost_cny=round(input_cost, 6),
            output_cost_cny=round(output_cost, 6),
            total_cost_cny=round(input_cost + output_cost, 6),
        )
