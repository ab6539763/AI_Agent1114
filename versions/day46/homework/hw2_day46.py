"""
Day 46 课后作业 2（企业实战）：实现单次会话 Token 预算熔断器
工单：STARMIND-046
"""

"""Day 46 作业 2 参考答案：单次会话 Token 费用预算熔断器。"""


class BudgetExceededError(RuntimeError):
    pass


class TokenBudgetGuard:
    def __init__(self, max_budget_cny: float = 0.10) -> None:
        self.max_budget_cny = max_budget_cny
        self.spent_cny = 0.0

    def consume(self, cost_cny: float) -> None:
        self.spent_cny = round(self.spent_cny + cost_cny, 6)
        if self.spent_cny > self.max_budget_cny:
            raise BudgetExceededError(f"单次请求费用 ¥{self.spent_cny} 超出上限 ¥{self.max_budget_cny}")


if __name__ == "__main__":
    g = TokenBudgetGuard(max_budget_cny=0.05)
    g.consume(0.03)
    try:
        g.consume(0.03)
    except BudgetExceededError as exc:
        print("成功熔断:", exc)

