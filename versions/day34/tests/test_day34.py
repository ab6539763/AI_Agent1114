import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 34 自动化单元测试：验证 Ragas 四维指标计算、幻觉捕获与 CI 门禁逻辑。"""

from src.day34_rag_metrics import (
    compute_answer_relevancy,
    compute_context_precision,
    compute_context_recall,
    compute_faithfulness,
)
from src.day34_ragas_runner import MiniRagasEvaluator, build_demo_eval_datasets


def test_faithfulness_detects_number_hallucination():
    ctx = ["一线城市出差酒店住宿上限为每晚600元，需提前3天OA申请。"]
    good_ans = "一线城市出差酒店住宿上限每晚600元，需提前3天OA申请。"
    bad_ans = "一线城市出差酒店住宿上限每晚800元，需提前3天OA申请。"

    f_good = compute_faithfulness(good_ans, ctx)
    f_bad = compute_faithfulness(bad_ans, ctx)
    assert f_good == 1.0
    assert f_bad < 0.6


def test_context_precision_rewards_top_ranking():
    q = "北京出差住宿上限是多少？"
    gt = "北京出差住宿上限每晚600元。"
    rel_ctx = "一线城市（北京、上海）出差住宿上限每晚600元。"
    noise_ctx = "公司每周五下午三点提供下午茶水果。"

    p_top1 = compute_context_precision(q, [rel_ctx, noise_ctx], gt)
    p_top2 = compute_context_precision(q, [noise_ctx, rel_ctx], gt)
    assert p_top1 == 1.0
    assert p_top2 == 0.5
    assert p_top1 > p_top2


def test_context_recall_and_relevancy():
    gt = "错误码ERR-5042表示网关超时，需检查显存水位。"
    ctx_full = ["错误码ERR-5042表示统一网关超时，请第一时间检查上游显存水位。"]
    ctx_miss = ["园区班车发车时间为早8点。"]

    assert compute_context_recall(gt, ctx_full) == 1.0
    assert compute_context_recall(gt, ctx_miss) == 0.0
    assert compute_answer_relevancy("ERR-5042 怎么排查", "抱歉，我不知道。") <= 0.2


def test_mini_ragas_ci_gate_blocks_v1_and_passes_v2():
    datasets = build_demo_eval_datasets()
    evaluator = MiniRagasEvaluator(
        min_faithfulness=0.85,
        min_answer_relevancy=0.70,
        min_context_precision=0.75,
        min_context_recall=0.80,
    )
    rep_v1 = evaluator.evaluate_dataset("v1_naive_rag", datasets["v1_naive_rag"])
    rep_v2 = evaluator.evaluate_dataset("v2_hybrid_rerank", datasets["v2_hybrid_rerank"])

    assert rep_v1.gate_passed is False
    assert len(rep_v1.failed_gates) >= 1
    assert rep_v2.gate_passed is True
    assert rep_v2.summary["faithfulness"] > rep_v1.summary["faithfulness"]

    md = evaluator.render_markdown_comparison(rep_v1, rep_v2)
    assert "v1_naive_rag" in md and "v2_hybrid_rerank" in md

