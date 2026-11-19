"""
Day 08 课后作业 1（基础巩固）：基础巩固：API Token 账单计数器类
工单：STARMIND-008
"""

"""Day 8 课后题 1：Token 账单追踪器类。"""


class TokenTracker:
    """累计单个会话或用户的 Token 消耗并估算人民币费用。"""

    def __init__(self) -> None:
        self.input_total: int = 0
        self.output_total: int = 0
        self.call_count: int = 0

    def record(self, in_tokens: int, out_tokens: int) -> None:
        """记录单次调用消耗。"""
        self.input_total += max(0, int(in_tokens))
        self.output_total += max(0, int(out_tokens))
        self.call_count += 1

    def total_tokens(self) -> int:
        return self.input_total + self.output_total

    def estimated_rmb(self, in_price_per_1k: float = 0.002, out_price_per_1k: float = 0.008) -> float:
        cost = (self.input_total / 1000.0) * in_price_per_1k + (self.output_total / 1000.0) * out_price_per_1k
        return round(cost, 6)


if __name__ == "__main__":
    tracker = TokenTracker()
    tracker.record(500, 200)
    tracker.record(800, 400)
    print(f"调用 {tracker.call_count} 次，总 Token: {tracker.total_tokens()}，费用: ¥{tracker.estimated_rmb()}")

