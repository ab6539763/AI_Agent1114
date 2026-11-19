import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 15 自动化单元测试：验证 Token 分词估算、Self-Attention 归一化与企业成本预测。"""

import pytest
from src.day15_tokenizer import StarMindTokenizer, scaled_dot_product_attention
from src.day15_cost_estimator import EnterpriseCostEstimator


def test_tokenizer_cn_vs_global_profile():
    text = "杭州星辰数科正在构建企业级智能体平台 StarMind 2026！"
    cn = StarMindTokenizer("cn_optimized").analyze(text)
    gl = StarMindTokenizer("global_bpe").analyze(text)

    assert cn.cjk_chars == 18
    assert cn.ascii_words == 1
    assert cn.numbers == 1
    assert cn.estimated_tokens > 0
    # 中文主导文本在 global_bpe 下消耗的 Token 应高于国产中文优化词表
    assert gl.estimated_tokens > cn.estimated_tokens


def test_tokenizer_empty_and_invalid_profile():
    tok = StarMindTokenizer("cn_optimized")
    assert tok.count_tokens("") == 0
    with pytest.raises(ValueError):
        StarMindTokenizer("unknown_profile")


def test_scaled_dot_product_attention_weights_sum_to_one():
    q = [[1.0, 0.0, 0.5], [0.2, 0.8, 0.1]]
    k = [[1.0, 0.0, 0.5], [0.0, 1.0, 0.0], [0.5, 0.5, 0.5]]
    v = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    outputs, weights = scaled_dot_product_attention(q, k, v)

    assert len(outputs) == 2
    assert len(weights) == 2
    for row in weights:
        assert abs(sum(row) - 1.0) < 1e-6
        assert all(w > 0 for w in row)


def test_enterprise_cost_estimator_and_budget_alert():
    est = EnterpriseCostEstimator()
    # 验证单次精确计费：100万输入 + 100万输出 = input_price + output_price
    cost = est.estimate_single_cost("deepseek-chat", 1_000_000, 1_000_000)
    assert cost == pytest.approx(10.0)

    reports = est.compare_all_models(
        sample_prompt="请总结星辰数科季度研发报告" * 30,
        sample_reply="核心指标达成率105%，风险可控。" * 15,
        daily_active_users=500,
        avg_calls_per_user=20,
        monthly_budget_cny=500.0,
    )
    assert len(reports) == 4
    # 结果按月度成本升序排列，deepseek-chat 应显著低于 gpt-4o
    assert reports[0].monthly_total_cny < reports[-1].monthly_total_cny
    assert reports[-1].model_id == "gpt-4o"
    assert reports[-1].exceeds_budget is True

