"""
Day 63 - 模块一：Ragas 风格四维 RAG 量化评估器与发布门禁报告
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Set


def _tokens(text: str) -> Set[str]:
    low = text.lower()
    alnum = re.findall(r"[a-z0-9_]+", low)
    cjk = re.findall(r"[\u4e00-\u9fff]", low)
    return set(alnum + cjk)


def _overlap_ratio(source: Set[str], target: Set[str]) -> float:
    if not source:
        return 0.0
    return len(source & target) / len(source)


@dataclass
class EvalSample:
    question: str
    answer: str
    contexts: List[str]
    ground_truth: str


@dataclass
class RagasReport:
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    passed: bool
    markdown: str


def evaluate_ragas(
    samples: List[EvalSample],
    min_faithfulness: float = 0.65,
    min_recall: float = 0.65,
) -> RagasReport:
    """计算四维均值并判定是否通过上线质量门禁"""
    f_list, rel_list, prec_list, rec_list = [], [], [], []
    for s in samples:
        ans_t = _tokens(s.answer)
        q_t = _tokens(s.question)
        gt_t = _tokens(s.ground_truth)
        ctx_all = set().union(*(_tokens(c) for c in s.contexts)) if s.contexts else set()

        # Faithfulness: 答案中多少比例的语义单元被上下文直接支撑
        faith = _overlap_ratio(ans_t, ctx_all)
        # Answer Relevancy: 答案覆盖提问与标准答案核心语义的综合程度
        relev = 0.5 * _overlap_ratio(q_t, ans_t) + 0.5 * _overlap_ratio(gt_t, ans_t)
        # Context Precision: 有多少比例的召回切片真正包含标准答案线索
        useful_ctx = sum(1 for c in s.contexts if _overlap_ratio(gt_t, _tokens(c)) >= 0.35)
        prec = useful_ctx / max(1, len(s.contexts))
        # Context Recall: 标准答案核心要点被上下文覆盖的比例
        rec = _overlap_ratio(gt_t, ctx_all)

        f_list.append(faith)
        rel_list.append(relev)
        prec_list.append(prec)
        rec_list.append(rec)

    n = max(1, len(samples))
    avg_f = round(sum(f_list) / n, 4)
    avg_rel = round(sum(rel_list) / n, 4)
    avg_prec = round(sum(prec_list) / n, 4)
    avg_rec = round(sum(rec_list) / n, 4)
    passed = (avg_f >= min_faithfulness) and (avg_rec >= min_recall)

    md = (
        "# 星辰智脑 Ragas 量化评估报告\n"
        f"- 样本数量: {len(samples)}\n"
        f"- Faithfulness (忠实度): {avg_f:.2%}\n"
        f"- Answer Relevancy (相关性): {avg_rel:.2%}\n"
        f"- Context Precision (上下文精度): {avg_prec:.2%}\n"
        f"- Context Recall (上下文召回): {avg_rec:.2%}\n"
        f"- 上线质量门禁: {'PASS' if passed else 'FAIL'}\n"
    )
    return RagasReport(avg_f, avg_rel, avg_prec, avg_rec, passed, md)


if __name__ == "__main__":
    golden = [
        EvalSample(
            question="一线城市差旅住宿标准是多少？",
            answer="一线城市差旅住宿上限650元/晚，需上传电子专票核销。",
            contexts=["一线城市出差住宿上限650元/晚，需在费用中心上传电子专票核销。"],
            ground_truth="一线城市住宿上限650元/晚，需上传电子专票。",
        ),
        EvalSample(
            question="ERR_4291 错误码什么意思？",
            answer="ERR_4291 表示部门日Token配额已触发硬熔断，请联系管理员提额。",
            contexts=["错误码ERR_4291表示部门日Token配额已触发硬熔断，请联系管理员提额。"],
            ground_truth="ERR_4291 代表部门日Token配额硬熔断，需联系管理员提额。",
        ),
    ]
    rep = evaluate_ragas(golden)
    print(rep.markdown)

