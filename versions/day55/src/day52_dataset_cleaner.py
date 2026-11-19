"""
Day 52 - 模块一：微调数据集清洗、隐私脱敏、近似去重与格式转换工具
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

BANNED_PHRASES = (
    "作为一个AI",
    "作为一名人工智能",
    "我只是一个语言模型",
    "无法为您提供帮助",
)


@dataclass
class CleaningStats:
    """清洗漏斗统计指标"""
    total_input: int = 0
    dropped_invalid: int = 0
    dropped_low_quality: int = 0
    dropped_exact_dup: int = 0
    dropped_near_dup: int = 0
    pii_masked_count: int = 0
    kept_count: int = 0


def mask_pii(text: str) -> Tuple[str, int]:
    """对手机号与邮箱进行隐私脱敏，返回(脱敏后文本, 替换次数)"""
    masked, c1 = PHONE_RE.subn("<PHONE_MASKED>", text)
    masked, c2 = EMAIL_RE.subn("<EMAIL_MASKED>", masked)
    return masked, c1 + c2


def _char_ngrams(text: str, n: int = 3) -> Set[str]:
    cleaned = re.sub(r"\s+", "", text.lower())
    if len(cleaned) < n:
        return {cleaned} if cleaned else set()
    return {cleaned[i : i + n] for i in range(len(cleaned) - n + 1)}


def jaccard_similarity(a: str, b: str, n: int = 3) -> float:
    """计算两段文本的字符 N-gram Jaccard 相似度"""
    sa, sb = _char_ngrams(a, n), _char_ngrams(b, n)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def clean_alpaca_dataset(
    records: List[Dict[str, str]],
    min_output_len: int = 12,
    near_dup_threshold: float = 0.88,
) -> Tuple[List[Dict[str, str]], CleaningStats]:
    """执行五步清洗漏斗：校验 -> 脱敏 -> 质量过滤 -> 精确去重 -> 近似去重"""
    stats = CleaningStats(total_input=len(records))
    seen_hashes: Set[str] = set()
    kept: List[Dict[str, str]] = []
    kept_prompts: List[str] = []

    for row in records:
        inst = str(row.get("instruction", "")).strip()
        inp = str(row.get("input", "")).strip()
        out = str(row.get("output", "")).strip()
        sys_prompt = str(row.get("system", "")).strip()

        # 1. 字段完整性校验
        if not inst or not out:
            stats.dropped_invalid += 1
            continue

        # 2. 隐私脱敏
        inst, m1 = mask_pii(inst)
        inp, m2 = mask_pii(inp)
        out, m3 = mask_pii(out)
        stats.pii_masked_count += m1 + m2 + m3

        # 3. 质量与黑名单过滤
        if len(out) < min_output_len or any(p in out for p in BANNED_PHRASES):
            stats.dropped_low_quality += 1
            continue

        # 4. 精确指纹去重
        norm_key = re.sub(r"\s+", "", f"{inst}|{inp}|{out}").lower()
        fp = hashlib.sha256(norm_key.encode("utf-8")).hexdigest()
        if fp in seen_hashes:
            stats.dropped_exact_dup += 1
            continue

        # 5. 近似去重（仅对 prompt 部分快速比对）
        prompt_text = f"{inst} {inp}".strip()
        is_near_dup = any(
            jaccard_similarity(prompt_text, prev) >= near_dup_threshold
            for prev in kept_prompts[-200:]  # 滑动窗口兼顾精度与速度
        )
        if is_near_dup:
            stats.dropped_near_dup += 1
            continue

        seen_hashes.add(fp)
        kept_prompts.append(prompt_text)
        item = {"instruction": inst, "input": inp, "output": out}
        if sys_prompt:
            item["system"] = sys_prompt
        kept.append(item)

    stats.kept_count = len(kept)
    return kept, stats


def alpaca_to_sharegpt(records: List[Dict[str, str]]) -> List[Dict[str, object]]:
    """将 Alpaca 格式无损转换为 LLaMA-Factory 兼容的 ShareGPT 格式"""
    result: List[Dict[str, object]] = []
    for r in records:
        user_msg = r["instruction"] if not r.get("input") else f"{r['instruction']}\n{r['input']}"
        entry: Dict[str, object] = {
            "conversations": [
                {"from": "human", "value": user_msg},
                {"from": "gpt", "value": r["output"]},
            ]
        }
        if r.get("system"):
            entry["system"] = r["system"]
        result.append(entry)
    return result


if __name__ == "__main__":
    demo = [
        {"instruction": "如何开具增值税专票？", "input": "我手机号13812345678", "output": "您好，请登录星辰数科企业控制台-费用中心-发票管理，填写税号后申请，3个工作日内电子交付。"},
        {"instruction": "如何开具增值税专票？", "input": "我手机号13812345678", "output": "您好，请登录星辰数科企业控制台-费用中心-发票管理，填写税号后申请，3个工作日内电子交付。"},
        {"instruction": "你好", "input": "", "output": "作为一个AI语言模型，我无法回答。"},
    ]
    cleaned, st = clean_alpaca_dataset(demo)
    print("清洗统计:", st)
    print("ShareGPT 转换示例:", alpaca_to_sharegpt(cleaned)[0])

