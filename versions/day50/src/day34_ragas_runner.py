"""
Day 34 - 步骤二：类 Ragas 自动化评测框架、Bad Case 根因诊断与 CI 门禁报告
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day34_rag_metrics import (
    EvalSample,
    compute_answer_relevancy,
    compute_context_precision,
    compute_context_recall,
    compute_faithfulness,
)


@dataclass
class SampleEvalResult:
    sample_id: str
    question: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    diagnosis: List[str] = field(default_factory=list)


@dataclass
class EvalReport:
    version_name: str
    sample_results: List[SampleEvalResult]
    summary: Dict[str, float]
    gate_passed: bool
    failed_gates: List[str]


class MiniRagasEvaluator:
    """企业级 RAG 自动化评测与 CI 门禁引擎。"""

    def __init__(
        self,
        min_faithfulness: float = 0.85,
        min_answer_relevancy: float = 0.70,
        min_context_precision: float = 0.75,
        min_context_recall: float = 0.80,
    ) -> None:
        self.thresholds = {
            "faithfulness": min_faithfulness,
            "answer_relevancy": min_answer_relevancy,
            "context_precision": min_context_precision,
            "context_recall": min_context_recall,
        }

    def evaluate_dataset(self, version_name: str, samples: Sequence[EvalSample]) -> EvalReport:
        results: List[SampleEvalResult] = []
        for s in samples:
            f_score = compute_faithfulness(s.answer, s.contexts)
            r_score = compute_answer_relevancy(s.question, s.answer)
            p_score = compute_context_precision(s.question, s.contexts, s.ground_truth)
            c_score = compute_context_recall(s.ground_truth, s.contexts)

            diag: List[str] = []
            if c_score < 0.7:
                diag.append("检索漏召回(需优化切分/混合检索)")
            if c_score >= 0.7 and p_score < 0.7:
                diag.append("排序靠后(需开启bge-reranker精排)")
            if f_score < 0.8:
                diag.append("生成幻觉(需收紧Prompt或核查数字约束)")
            if r_score < 0.6:
                diag.append("答非所问(需优化意图对齐)")
            if not diag:
                diag.append("PASS")

            results.append(
                SampleEvalResult(
                    sample_id=s.sample_id,
                    question=s.question,
                    faithfulness=f_score,
                    answer_relevancy=r_score,
                    context_precision=p_score,
                    context_recall=c_score,
                    diagnosis=diag,
                )
            )

        n = max(1, len(results))
        summary = {
            "faithfulness": round(sum(r.faithfulness for r in results) / n, 4),
            "answer_relevancy": round(sum(r.answer_relevancy for r in results) / n, 4),
            "context_precision": round(sum(r.context_precision for r in results) / n, 4),
            "context_recall": round(sum(r.context_recall for r in results) / n, 4),
        }

        failed_gates = [
            f"{metric}={summary[metric]:.4f} < 门禁阈值 {limit:.2f}"
            for metric, limit in self.thresholds.items()
            if summary[metric] < limit
        ]
        return EvalReport(
            version_name=version_name,
            sample_results=results,
            summary=summary,
            gate_passed=(len(failed_gates) == 0),
            failed_gates=failed_gates,
        )

    @staticmethod
    def render_markdown_comparison(report_a: EvalReport, report_b: EvalReport) -> str:
        lines = [
            "## StarMind RAG 自动化评测对比报告",
            f"| 评估维度 | {report_a.version_name} | {report_b.version_name} | 提升幅度 |",
            "| :--- | :---: | :---: | :---: |",
        ]
        for key in ("faithfulness", "answer_relevancy", "context_precision", "context_recall"):
            va = report_a.summary[key]
            vb = report_b.summary[key]
            delta = vb - va
            sign = "+" if delta >= 0 else ""
            lines.append(f"| `{key}` | {va:.4f} | {vb:.4f} | {sign}{delta:.4f} |")
        lines.append(
            f"\n- **{report_a.version_name} CI 门禁**: {'✅ PASS' if report_a.gate_passed else '❌ FAIL (' + '; '.join(report_a.failed_gates) + ')'}"
        )
        lines.append(
            f"- **{report_b.version_name} CI 门禁**: {'✅ PASS' if report_b.gate_passed else '❌ FAIL (' + '; '.join(report_b.failed_gates) + ')'}"
        )
        return "\n".join(lines)


def build_demo_eval_datasets() -> Dict[str, List[EvalSample]]:
    """构造 v1 Naive RAG 与 v2 Hybrid+Rerank RAG 的对照评测样本集。"""
    v1_naive = [
        EvalSample(
            sample_id="Q1",
            question="北京出差住宿上限是多少，需要提前几天OA审批？",
            answer="北京出差住宿上限每晚800元，需提前3天OA审批。",  # 存在数字幻觉
            contexts=[
                "园区班车每天早8点从地铁站发车。",
                "一线城市（北京、上海、深圳、广州）出差住宿上限为每晚600元，需提前3天在OA审批。",
            ],
            ground_truth="北京出差住宿上限每晚600元，需提前3天OA审批。",
        ),
        EvalSample(
            sample_id="Q2",
            question="ERR-5042 报错怎么排查？",
            answer="建议先重启电脑并重新连接公司 Wi-Fi 试试。",  # 漏召回导致瞎答
            contexts=[
                "员工入职当天请前往行政前台领取工牌。",
                "食堂二楼提供杭帮菜和轻食套餐。",
            ],
            ground_truth="错误码ERR-5042为网关超时，需检查上游显存水位并调大超时阈值。",
        ),
    ]

    v2_hybrid_rerank = [
        EvalSample(
            sample_id="Q1",
            question="北京出差住宿上限是多少，需要提前几天OA审批？",
            answer="北京属于一线城市，出差住宿上限每晚600元，需提前3天在OA审批。",
            contexts=[
                "一线城市（北京、上海、深圳、广州）出差住宿上限为每晚600元，需提前3天在OA审批。",
                "餐饮补助按每天100元定额随工资发放。",
            ],
            ground_truth="北京出差住宿上限每晚600元，需提前3天OA审批。",
        ),
        EvalSample(
            sample_id="Q2",
            question="ERR-5042 报错怎么排查？",
            answer="错误码ERR-5042表示网关超时，排查需检查上游显存水位并调大超时阈值。",
            contexts=[
                "错误码ERR-5042表示统一网关调用上游超时，排查需检查上游显存水位并调大超时阈值。",
                "错误码ERR-4019表示零信任VPN动态令牌失效。",
            ],
            ground_truth="错误码ERR-5042为网关超时，需检查上游显存水位并调大超时阈值。",
        ),
    ]
    return {"v1_naive_rag": v1_naive, "v2_hybrid_rerank": v2_hybrid_rerank}


if __name__ == "__main__":
    datasets = build_demo_eval_datasets()
    evaluator = MiniRagasEvaluator()
    rep_v1 = evaluator.evaluate_dataset("v1_naive_rag", datasets["v1_naive_rag"])
    rep_v2 = evaluator.evaluate_dataset("v2_hybrid_rerank", datasets["v2_hybrid_rerank"])
    print(evaluator.render_markdown_comparison(rep_v1, rep_v2))

