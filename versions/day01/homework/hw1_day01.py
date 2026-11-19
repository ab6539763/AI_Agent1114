"""
Day 01 课后作业 1（基础巩固）：基础巩固：API 费用人民币估算器
工单：STARMIND-001
"""

"""Day 1 课后题 1：大模型调用费用估算器。"""

INPUT_PRICE_PER_1K = 0.002   # 输入单价：元 / 1000 Tokens
OUTPUT_PRICE_PER_1K = 0.008  # 输出单价：元 / 1000 Tokens


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """计算单次大模型对话的人民币费用（元）。"""
    # 防止传入负数 Token
    safe_in = max(0, int(input_tokens))
    safe_out = max(0, int(output_tokens))
    # 按千 Token 单价分别计算并相加
    total = (safe_in / 1000.0) * INPUT_PRICE_PER_1K + (safe_out / 1000.0) * OUTPUT_PRICE_PER_1K
    return round(total, 6)


if __name__ == "__main__":
    cost = estimate_cost(1500, 800)
    print(f"本次调用输入 1500 Tokens，输出 800 Tokens，预计费用：¥{cost:.6f}")

