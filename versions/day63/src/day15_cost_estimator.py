"""
StarMind Day 15 - 步骤二：企业级大模型 API 成本估算与月度预算评估器
支持多模型输入/输出阶梯定价对比、月度 DAU 费用预测与超预算告警。
"""

from dataclasses import dataclass
from typing import Dict, List

from src.day15_tokenizer import StarMindTokenizer


@dataclass(frozen=True)
class ModelPricing:
    """大模型 API 定价规范（单位：人民币 元 / 100万 Tokens）。"""
    model_id: str
    provider: str
    input_price_per_1m: float
    output_price_per_1m: float
    context_window: int
    tokenizer_profile: str = "cn_optimized"


# 星辰数科 2026 内部参考模型价目表（示例人民币定价，便于横向选型）
MODEL_CATALOG: Dict[str, ModelPricing] = {
    "deepseek-chat": ModelPricing(
        model_id="deepseek-chat",
        provider="DeepSeek",
        input_price_per_1m=2.0,
        output_price_per_1m=8.0,
        context_window=64_000,
        tokenizer_profile="cn_optimized",
    ),
    "qwen-max": ModelPricing(
        model_id="qwen-max",
        provider="阿里云百炼",
        input_price_per_1m=2.4,
        output_price_per_1m=9.6,
        context_window=32_000,
        tokenizer_profile="cn_optimized",
    ),
    "glm-4-plus": ModelPricing(
        model_id="glm-4-plus",
        provider="智谱AI",
        input_price_per_1m=5.0,
        output_price_per_1m=5.0,
        context_window=128_000,
        tokenizer_profile="cn_optimized",
    ),
    "gpt-4o": ModelPricing(
        model_id="gpt-4o",
        provider="OpenAI",
        input_price_per_1m=18.0,
        output_price_per_1m=72.0,
        context_window=128_000,
        tokenizer_profile="global_bpe",
    ),
}


@dataclass
class CostReport:
    """单次或月度成本预测报告。"""
    model_id: str
    input_tokens: int
    output_tokens: int
    single_call_cny: float
    monthly_total_cny: float
    exceeds_budget: bool
    context_utilization_pct: float
    recommendation: str


class EnterpriseCostEstimator:
    """企业级 FinOps 大模型成本核算器。"""

    def __init__(self, catalog: Dict[str, ModelPricing] | None = None) -> None:
        self.catalog = catalog or MODEL_CATALOG

    def estimate_single_cost(
        self, model_id: str, input_tokens: int, output_tokens: int
    ) -> float:
        """按百万 Token 单价精确计算单次调用成本（人民币元）。"""
        if model_id not in self.catalog:
            raise KeyError(f"未注册的模型: {model_id}")
        if input_tokens < 0 or output_tokens < 0:
            raise ValueError("Token 数量不能为负数")
        p = self.catalog[model_id]
        cost = (
            (input_tokens / 1_000_000) * p.input_price_per_1m
            + (output_tokens / 1_000_000) * p.output_price_per_1m
        )
        return round(cost, 6)

    def forecast_monthly_budget(
        self,
        model_id: str,
        sample_prompt: str,
        sample_reply: str,
        daily_active_users: int,
        avg_calls_per_user: int,
        monthly_budget_cny: float,
        workdays: int = 22,
    ) -> CostReport:
        """根据典型问答样本与日活规模，预测企业月度 API 支出并检查预算红线。"""
        if model_id not in self.catalog:
            raise KeyError(f"未注册的模型: {model_id}")
        pricing = self.catalog[model_id]
        tokenizer = StarMindTokenizer(pricing.tokenizer_profile)

        in_tokens = tokenizer.count_tokens(sample_prompt)
        out_tokens = tokenizer.count_tokens(sample_reply)
        single_cost = self.estimate_single_cost(model_id, in_tokens, out_tokens)

        monthly_calls = daily_active_users * avg_calls_per_user * workdays
        monthly_cost = round(single_cost * monthly_calls, 2)
        exceeds = monthly_cost > monthly_budget_cny
        ctx_pct = round(((in_tokens + out_tokens) / pricing.context_window) * 100, 4)

        if exceeds:
            rec = (
                f"⚠️ 预计月支出 ¥{monthly_cost:.2f} 超出预算 ¥{monthly_budget_cny:.2f}，"
                f"建议将非核心场景路由至 deepseek-chat 或启用 Prompt 缓存降本。"
            )
        else:
            rec = f"✅ 预计月支出 ¥{monthly_cost:.2f} 在预算 ¥{monthly_budget_cny:.2f} 内，可安心上线。"

        return CostReport(
            model_id=model_id,
            input_tokens=in_tokens,
            output_tokens=out_tokens,
            single_call_cny=single_cost,
            monthly_total_cny=monthly_cost,
            exceeds_budget=exceeds,
            context_utilization_pct=ctx_pct,
            recommendation=rec,
        )

    def compare_all_models(
        self,
        sample_prompt: str,
        sample_reply: str,
        daily_active_users: int,
        avg_calls_per_user: int,
        monthly_budget_cny: float,
    ) -> List[CostReport]:
        """横向对比价目表中全部模型的月度成本，按从低到高排序。"""
        reports = [
            self.forecast_monthly_budget(
                model_id=mid,
                sample_prompt=sample_prompt,
                sample_reply=sample_reply,
                daily_active_users=daily_active_users,
                avg_calls_per_user=avg_calls_per_user,
                monthly_budget_cny=monthly_budget_cny,
            )
            for mid in self.catalog
        ]
        reports.sort(key=lambda r: r.monthly_total_cny)
        return reports


if __name__ == "__main__":
    estimator = EnterpriseCostEstimator()
    prompt_text = "请帮我总结以下杭州星辰数科 Q3 研发效能报告的核心指标与风险点：" + ("研发交付周期缩短15%，线上缺陷率下降。" * 20)
    reply_text = "【核心结论】1. 交付效率显著提升；2. 缺陷率稳步下降；3. 建议下季度重点优化代码评审耗时。" * 5

    results = estimator.compare_all_models(
        sample_prompt=prompt_text,
        sample_reply=reply_text,
        daily_active_users=800,
        avg_calls_per_user=15,
        monthly_budget_cny=1000.0,
    )
    for rep in results:
        print(f"{rep.model_id:15s} | 月成本: ¥{rep.monthly_total_cny:8.2f} | {rep.recommendation}")

