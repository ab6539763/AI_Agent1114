"""
Day 54 - 模块一：微调前后自动化 A/B 评测与上线质量门禁引擎
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class EvalCase:
    """单条评测用例"""
    case_id: str
    category: str               # "domain" | "general"
    required_keywords: List[str]
    require_numbered_steps: bool = False


@dataclass
class GateReport:
    """微调上线门禁报告"""
    base_domain_score: float
    ft_domain_score: float
    domain_gain: float
    base_general_score: float
    ft_general_score: float
    general_drop: float
    passed: bool
    reason: str


def score_single_response(case: EvalCase, response: str) -> float:
    """对单条模型回复进行综合打分 [0.0, 1.0]"""
    if not response.strip():
        return 0.0
    hits = sum(1 for kw in case.required_keywords if kw in response)
    kw_score = hits / max(1, len(case.required_keywords))

    if case.require_numbered_steps:
        has_steps = bool(re.search(r"1\..*2\.", response, re.DOTALL))
        return round(0.7 * kw_score + 0.3 * (1.0 if has_steps else 0.0), 4)
    return round(kw_score, 4)


def run_ab_eval_gate(
    cases: List[EvalCase],
    base_outputs: Dict[str, str],
    ft_outputs: Dict[str, str],
    min_domain_gain: float = 0.15,
    max_general_drop: float = 0.05,
) -> GateReport:
    """对比微调前后得分并执行上线门禁判定"""
    dom_base, dom_ft, gen_base, gen_ft = [], [], [], []
    for c in cases:
        sb = score_single_response(c, base_outputs.get(c.case_id, ""))
        sf = score_single_response(c, ft_outputs.get(c.case_id, ""))
        if c.category == "domain":
            dom_base.append(sb)
            dom_ft.append(sf)
        else:
            gen_base.append(sb)
            gen_ft.append(sf)

    b_dom = round(sum(dom_base) / max(1, len(dom_base)), 4)
    f_dom = round(sum(dom_ft) / max(1, len(dom_ft)), 4)
    b_gen = round(sum(gen_base) / max(1, len(gen_base)), 4)
    f_gen = round(sum(gen_ft) / max(1, len(gen_ft)), 4)

    gain = round(f_dom - b_dom, 4)
    drop = round(max(0.0, b_gen - f_gen), 4)

    if gain < min_domain_gain:
        passed, reason = False, f"拒绝上线：领域得分仅提升 {gain*100:.1f}%，低于门禁要求 {min_domain_gain*100:.1f}%。"
    elif drop > max_general_drop:
        passed, reason = False, f"拒绝上线：通用回归能力下降 {drop*100:.1f}%，发生灾难性遗忘！"
    else:
        passed, reason = True, f"门禁通过：领域能力提升 +{gain*100:.1f}%，通用能力退化仅 {drop*100:.1f}%。"

    return GateReport(b_dom, f_dom, gain, b_gen, f_gen, drop, passed, reason)


if __name__ == "__main__":
    cases = [
        EvalCase("D1", "domain", ["OCR", "50MB", "工单"], require_numbered_steps=True),
        EvalCase("D2", "domain", ["费用中心", "税号", "工作日"], require_numbered_steps=True),
        EvalCase("G1", "general", ["Python", "列表"], require_numbered_steps=False),
    ]
    base_out = {
        "D1": "PDF 解析失败可能是文件损坏，请重新上传试试。",
        "D2": "您可以联系客服申请发票。",
        "G1": "Python 列表支持 append 和 extend。",
    }
    ft_out = {
        "D1": "1. 请确认是否为扫描件并开启OCR开关，单文件上限50MB。\n2. 若仍失败请携带文档ID提交工单。",
        "D2": "1. 登录费用中心填写企业税号。\n2. 提交后1~3个工作日开具数电专票。",
        "G1": "Python 列表是可变序列，常用方法有 append。",
    }
    print(run_ab_eval_gate(cases, base_out, ft_out))

