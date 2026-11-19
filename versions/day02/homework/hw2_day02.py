"""
Day 02 课后作业 2（企业实战）：企业实战：对话日志快速摘要统计器
工单：STARMIND-002
"""

"""Day 2 课后题 2：对话日志摘要统计器。"""


def summarize_chat_log(log_text: str) -> str:
    """统计对话日志的基础指标并返回摘要。"""
    cleaned = log_text.strip()
    user_turns = cleaned.count("USER:")
    ai_turns = cleaned.count("AI:")
    has_refund = "退款" in cleaned
    return (
        f"日志总字数: {len(cleaned)} | 用户轮次: {user_turns} | "
        f"AI 轮次: {ai_turns} | 涉及退款: {'是' if has_refund else '否'}"
    )


if __name__ == "__main__":
    sample_log = "USER: 你好，我想申请退款\nAI: 请提供您的订单号\nUSER: ORD-1001"
    print(summarize_chat_log(sample_log))

