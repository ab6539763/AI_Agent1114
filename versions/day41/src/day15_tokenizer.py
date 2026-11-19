"""
StarMind Day 15 - 步骤一：中英文混合 Token 分词估算器与 Self-Attention 原理演示
无需外部模型文件，纯 Python 实现高精度启发式分词统计与缩放点积注意力计算。
"""

import math
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class TokenBreakdown:
    """文本分词拆解明细结果。"""
    total_chars: int
    cjk_chars: int
    ascii_words: int
    numbers: int
    symbols: int
    estimated_tokens: int
    segments: List[str]


class StarMindTokenizer:
    """
    星辰智脑轻量级中英文混合 Token 估算器。
    支持针对不同词表风格（cn_optimized 国产中文优化 vs global_bpe 通用英文偏重）切换估算倍率。
    """

    # 匹配顺序：英文单词 -> 数字 -> 单个中文汉字 -> 非空白标点符号
    _TOKEN_PATTERN = re.compile(
        r"[A-Za-z_][A-Za-z0-9_]*|\d+(?:\.\d+)?|[\u4e00-\u9fff]|[^\sA-Za-z0-9_\u4e00-\u9fff]"
    )

    PROFILE_WEIGHTS: Dict[str, Dict[str, float]] = {
        # DeepSeek / Qwen / GLM 等对中文词表高度优化的模型
        "cn_optimized": {
            "cjk": 0.75,      # 常见中文双字词常合并，平均约 0.75 token/字
            "word": 1.15,     # 英文单词偶有子词拆分
            "number": 1.0,    # 连续数字通常按 1~3 位切分
            "symbol": 0.8,    # 标点与代码符号
        },
        # 早期偏英文 BPE 词表（如经典 cl100k_base）
        "global_bpe": {
            "cjk": 1.50,      # 中文在英文主导词表中往往消耗 1.5~2 token/字
            "word": 1.05,
            "number": 1.0,
            "symbol": 0.85,
        },
    }

    def __init__(self, profile: str = "cn_optimized") -> None:
        if profile not in self.PROFILE_WEIGHTS:
            raise ValueError(f"不支持的分词配置: {profile}，可选: {list(self.PROFILE_WEIGHTS)}")
        self.profile = profile
        self.weights = self.PROFILE_WEIGHTS[profile]

    def analyze(self, text: str) -> TokenBreakdown:
        """分析文本的语种构成并估算 Token 总数。"""
        if not text:
            return TokenBreakdown(0, 0, 0, 0, 0, 0, [])

        segments = self._TOKEN_PATTERN.findall(text)
        cjk_chars = 0
        ascii_words = 0
        numbers = 0
        symbols = 0

        for seg in segments:
            if "\u4e00" <= seg[0] <= "\u9fff":
                cjk_chars += 1
            elif seg[0].isdigit():
                numbers += 1
            elif seg[0].isalpha() or seg[0] == "_":
                ascii_words += 1
            else:
                symbols += 1

        raw_score = (
            cjk_chars * self.weights["cjk"]
            + ascii_words * self.weights["word"]
            + numbers * self.weights["number"]
            + symbols * self.weights["symbol"]
        )
        # 至少返回 1 个 Token（只要存在有效片段）
        estimated = max(1, math.ceil(raw_score)) if segments else 0

        return TokenBreakdown(
            total_chars=len(text),
            cjk_chars=cjk_chars,
            ascii_words=ascii_words,
            numbers=numbers,
            symbols=symbols,
            estimated_tokens=estimated,
            segments=segments,
        )

    def count_tokens(self, text: str) -> int:
        """快捷方法：直接返回估算的 Token 数量。"""
        return self.analyze(text).estimated_tokens


def scaled_dot_product_attention(
    queries: List[List[float]],
    keys: List[List[float]],
    values: List[List[float]],
) -> Tuple[List[List[float]], List[List[float]]]:
    """
    纯 Python 实现简化版 Transformer Scaled Dot-Product Self-Attention：
    Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V
    返回: (上下文融合输出矩阵, 注意力权重矩阵)
    """
    if not queries or not keys or not values:
        raise ValueError("Q、K、V 矩阵均不能为空")
    d_k = len(queries[0])
    scale = math.sqrt(d_k)

    attention_weights: List[List[float]] = []
    outputs: List[List[float]] = []

    for q_vec in queries:
        # 1. 计算当前 Query 与所有 Key 的缩放点积分数
        scores = [
            sum(q_i * k_i for q_i, k_i in zip(q_vec, k_vec)) / scale
            for k_vec in keys
        ]
        # 2. 数值稳定版 Softmax（减去最大值防止 exp 溢出）
        max_score = max(scores)
        exp_scores = [math.exp(s - max_score) for s in scores]
        sum_exp = sum(exp_scores)
        weights = [e / sum_exp for e in exp_scores]
        attention_weights.append(weights)

        # 3. 使用注意力权重对 Value 进行加权求和
        v_dim = len(values[0])
        out_vec = [0.0] * v_dim
        for w, v_vec in zip(weights, values):
            for idx in range(v_dim):
                out_vec[idx] += w * v_vec[idx]
        outputs.append(out_vec)

    return outputs, attention_weights


if __name__ == "__main__":
    sample = "杭州星辰数科 StarMind 平台支持 DeepSeek-V3 与 Qwen2.5，日均处理 12500 条工单！"
    cn_tok = StarMindTokenizer("cn_optimized")
    gl_tok = StarMindTokenizer("global_bpe")
    print("中文优化词表估算:", cn_tok.analyze(sample))
    print("通用英文词表估算:", gl_tok.analyze(sample))

    # 演示 3 个 Token（如 ["星辰", "智脑", "平台"]）的自注意力计算
    q_demo = [[1.0, 0.2], [0.1, 0.9], [0.8, 0.7]]
    k_demo = [[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]]
    v_demo = [[10.0, 1.0], [2.0, 8.0], [5.0, 5.0]]
    out_mat, w_mat = scaled_dot_product_attention(q_demo, k_demo, v_demo)
    print("注意力权重矩阵:", [[round(x, 4) for x in row] for row in w_mat])
    print("融合输出矩阵:", [[round(x, 3) for x in row] for row in out_mat])

