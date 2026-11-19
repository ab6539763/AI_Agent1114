"""
Day 34 - 步骤一：类 Ragas 四维核心评估指标实现
包含：Faithfulness、Answer Relevancy、Context Precision (AP@K)、Context Recall
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence, Set


@dataclass
class EvalSample:
    """单条 RAG 评测样本（与 Ragas Dataset 字段对齐）。"""

    sample_id: str
    question: str
    answer: str
    contexts: List[str]
    ground_truth: str


def extract_keywords(text: str) -> Set[str]:
    """提取用于事实核查的核心词元（中文二元词 + 英文/错误码/数字）。"""
    lowered = text.lower()
    tokens: Set[str] = set()
    # 英文词、错误码与数字
    tokens.update(re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", lowered))
    # 中文二元词组（过滤极常见虚词组合）
    stop_bigrams = {"的是", "可以", "需要", "进行", "相关", "以及", "一个", "什么", "怎么", "多少", "请问", "根据"}
    for chunk in re.findall(r"[\u4e00-\u9fff]+", lowered):
        for i in range(len(chunk) - 1):
            bg = chunk[i : i + 2]
            if bg not in stop_bigrams:
                tokens.add(bg)
    return tokens


def extract_numbers(text: str) -> Set[str]:
    """提取文本中的所有关键数字（如 600、15、5042、3），用于严查数字幻觉。"""
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def split_claims(text: str) -> List[str]:
    """将一段自然语言回答拆解为独立的原子事实断言（Claims）。"""
    raw = [s.strip() for s in re.split(r"[。！？；;\n，,]", text) if len(s.strip()) >= 4]
    return raw if raw else ([text.strip()] if text.strip() else [])


def compute_faithfulness(answer: str, contexts: Sequence[str]) -> float:
    """
    忠实度（Faithfulness）：
    衡量模型回答中的所有原子断言是否都能在检索上下文中找到事实依据。
    若某条断言包含上下文中不存在的关键数字（如把 600 编成 800），直接判定为幻觉不支持！
    """
    claims = split_claims(answer)
    if not claims or not contexts:
        return 0.0

    merged_ctx = "\n".join(contexts)
    ctx_tokens = extract_keywords(merged_ctx)
    ctx_numbers = extract_numbers(merged_ctx)

    supported = 0
    for claim in claims:
        c_nums = extract_numbers(claim)
        # 严格数字幻觉检查：断言里提到的数字必须全部出现在检索上下文中
        if c_nums and not c_nums.issubset(ctx_numbers):
            continue
        c_tokens = extract_keywords(claim)
        if not c_tokens:
            supported += 1
            continue
        overlap_ratio = len(c_tokens & ctx_tokens) / len(c_tokens)
        if overlap_ratio >= 0.45:
            supported += 1

    return round(supported / len(claims), 4)


def compute_answer_relevancy(question: str, answer: str) -> float:
    """
    答案相关性（Answer Relevancy）：
    衡量回答是否切中提问核心主题，并对拒答/套话/答非所问施加惩罚。
    """
    if not question.strip() or not answer.strip():
        return 0.0
    evasive_phrases = ("不知道", "无法回答", "抱歉", "与您的问题无关", "天气不错")
    if any(p in answer for p in evasive_phrases):
        return 0.1

    # 去除疑问词后再提取核心意图词，避免「是多少/怎么」拉低正常陈述回答得分
    cleaned_q = re.sub(r"请问|是多少|多少|几天|怎么|如何|什么|是否|吗|呢|需要|报错", " ", question)
    q_tokens = extract_keywords(cleaned_q)
    a_tokens = extract_keywords(answer)
    if not q_tokens:
        return 0.0

    # 问题关键意图在回答中的覆盖度
    intent_coverage = len(q_tokens & a_tokens) / len(q_tokens)
    # 适度考虑回答信息密度（过短或严重跑题都会拉低分数）
    length_factor = min(1.0, len(answer.strip()) / 12.0)
    score = min(1.0, (0.85 * intent_coverage + 0.15 * length_factor))
    return round(score, 4)


def compute_context_precision(
    question: str,
    contexts: Sequence[str],
    ground_truth: str,
) -> float:
    """
    上下文精确率（Context Precision，采用 AP@K 位置加权公式）：
    不仅看检索回来的上下文是否相关，更奖励将相关上下文排在靠前位置（Top-1 > Top-3）。
    """
    if not contexts:
        return 0.0

    ref_tokens = extract_keywords(question) | extract_keywords(ground_truth)
    gt_nums = extract_numbers(ground_truth)

    relevances: List[int] = []
    for ctx in contexts:
        c_tokens = extract_keywords(ctx)
        c_nums = extract_numbers(ctx)
        overlap = len(c_tokens & ref_tokens) / max(1, len(ref_tokens))
        num_match = bool(gt_nums and (gt_nums & c_nums))
        is_rel = 1 if (overlap >= 0.28 or num_match) else 0
        relevances.append(is_rel)

    total_rel = sum(relevances)
    if total_rel == 0:
        return 0.0

    ap_sum = 0.0
    running_rel = 0
    for rank, rel in enumerate(relevances, start=1):
        if rel == 1:
            running_rel += 1
            ap_sum += running_rel / rank
    return round(ap_sum / total_rel, 4)


def compute_context_recall(ground_truth: str, contexts: Sequence[str]) -> float:
    """
    上下文召回率（Context Recall）：
    将标准答案（Ground Truth）拆解为关键事实句，统计有多少比例已被检索上下文覆盖。
    """
    gt_claims = split_claims(ground_truth)
    if not gt_claims or not contexts:
        return 0.0

    merged_ctx = "\n".join(contexts)
    ctx_tokens = extract_keywords(merged_ctx)
    ctx_numbers = extract_numbers(merged_ctx)

    recalled = 0
    for claim in gt_claims:
        c_nums = extract_numbers(claim)
        if c_nums and not c_nums.issubset(ctx_numbers):
            continue
        c_tokens = extract_keywords(claim)
        if not c_tokens:
            recalled += 1
            continue
        if (len(c_tokens & ctx_tokens) / len(c_tokens)) >= 0.45:
            recalled += 1
    return round(recalled / len(gt_claims), 4)


if __name__ == "__main__":
    ctx_good = [
        "一线城市（北京、上海、深圳、广州）出差住宿上限为每晚600元，需提前3天在OA审批。",
        "园区地下车库免费向员工开放。",
    ]
    q = "北京出差住宿上限是多少，需要提前几天OA审批？"
    gt = "北京出差住宿上限每晚600元，需提前3天OA审批。"
    ans_faithful = "北京属于一线城市，出差住宿上限每晚600元，需提前3天在OA审批。"
    ans_hallucinated = "北京出差住宿上限每晚800元，需提前3天在OA审批。"

    print("忠实回答 Faithfulness :", compute_faithfulness(ans_faithful, ctx_good))
    print("幻觉回答 Faithfulness :", compute_faithfulness(ans_hallucinated, ctx_good))
    print("相关上下文排第1 Precision:", compute_context_precision(q, ctx_good, gt))
    print("相关上下文排第2 Precision:", compute_context_precision(q, list(reversed(ctx_good)), gt))
    print("Context Recall        :", compute_context_recall(gt, ctx_good))

