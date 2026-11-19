"""
Day 57 - 模块二：多租户 Token 成本实时监控与分级熔断器（FinOps Guard）
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# 主流模型参考单价（单位：人民币元 / 百万 Token）
MODEL_PRICING_CNY_PER_M: Dict[str, Dict[str, float]] = {
    "qwen-max": {"input": 20.0, "output": 60.0},
    "deepseek-chat": {"input": 2.0, "output": 8.0},
    "starmind-7b-local": {"input": 0.2, "output": 0.4},  # 私有化算力折旧摊销成本
}


@dataclass
class BudgetDecision:
    """预算检查与熔断决策"""
    tenant_id: str
    action: str               # "ALLOW" | "WARN_DEGRADE" | "BLOCKED"
    spent_cny: float
    limit_cny: float
    usage_ratio: float
    recommended_model: str
    message: str


class TokenBudgetGuard:
    """部门/租户级 Token 预算监控与熔断器"""

    def __init__(self, warn_ratio: float = 0.80, fallback_model: str = "starmind-7b-local") -> None:
        self.warn_ratio = warn_ratio
        self.fallback_model = fallback_model
        self._limits: Dict[str, float] = {}
        self._spent: Dict[str, float] = {}

    def set_daily_limit(self, tenant_id: str, limit_cny: float) -> None:
        if limit_cny <= 0:
            raise ValueError("预算上限必须大于 0")
        self._limits[tenant_id] = limit_cny
        self._spent.setdefault(tenant_id, 0.0)

    def record_usage(
        self, tenant_id: str, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """记录单次调用消耗并累加人民币成本"""
        price = MODEL_PRICING_CNY_PER_M.get(model, {"input": 5.0, "output": 15.0})
        cost = (prompt_tokens * price["input"] + completion_tokens * price["output"]) / 1_000_000.0
        self._spent[tenant_id] = self._spent.get(tenant_id, 0.0) + cost
        return round(cost, 6)

    def check_before_call(self, tenant_id: str, requested_model: str) -> BudgetDecision:
        """调用模型前执行预算水位检查与分级熔断判定"""
        limit = self._limits.get(tenant_id, 50.0)
        spent = round(self._spent.get(tenant_id, 0.0), 4)
        ratio = round(spent / limit, 4)

        if ratio >= 1.0:
            return BudgetDecision(
                tenant_id=tenant_id,
                action="BLOCKED",
                spent_cny=spent,
                limit_cny=limit,
                usage_ratio=ratio,
                recommended_model="",
                message=f"租户 {tenant_id} 今日预算已耗尽({spent}/{limit}元)，触发硬熔断(HTTP 429)！",
            )
        if ratio >= self.warn_ratio:
            return BudgetDecision(
                tenant_id=tenant_id,
                action="WARN_DEGRADE",
                spent_cny=spent,
                limit_cny=limit,
                usage_ratio=ratio,
                recommended_model=self.fallback_model,
                message=f"租户 {tenant_id} 预算已用 {ratio*100:.1f}%，自动降级至低成本模型 {self.fallback_model}。",
            )
        return BudgetDecision(
            tenant_id=tenant_id,
            action="ALLOW",
            spent_cny=spent,
            limit_cny=limit,
            usage_ratio=ratio,
            recommended_model=requested_model,
            message="预算充足，正常放行。",
        )


if __name__ == "__main__":
    guard = TokenBudgetGuard()
    guard.set_daily_limit("dept_sales", 10.0)
    guard.record_usage("dept_sales", "qwen-max", 100_000, 110_000)  # 约 8.6 元
    print("85%水位:", guard.check_before_call("dept_sales", "qwen-max"))
    guard.record_usage("dept_sales", "qwen-max", 50_000, 50_000)    # 累计超 12 元
    print("超额熔断:", guard.check_before_call("dept_sales", "qwen-max"))

