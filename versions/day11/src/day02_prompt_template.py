"""
STARMIND-002 模块二：f-string Prompt 模板引擎与 Token 粗估工具。
演示多行 f-string、转义花括号、算术运算符（整除 // 与向上取整技巧）。
"""

from day02_text_cleaner import clean_ticket_text, has_blocked_content


def estimate_tokens_rough(text: str) -> int:
    """
    粗略估算中英混合文本的 Token 数量（经验值：约每 2 个字符折算 1.5 个 Token）。
    使用整数运算避免浮点误差，并保证非空文本至少返回 1。
    """
    if not text:
        return 0
    # 向上取整技巧：(长度 * 3 + 3) // 4 等价于 ceil(len * 0.75)
    return max(1, (len(text) * 3 + 3) // 4)


def render_support_prompt(
    user_query: str,
    customer_tier: str = "VIP",
    max_reply_words: int = 120,
) -> str:
    """将清洗后的用户问题组装为星辰智脑标准客服 Prompt。"""
    cleaned_query = clean_ticket_text(user_query, max_length=300)

    # 若触发安全词拦截，直接返回拒答提示模板
    if has_blocked_content(cleaned_query):
        return "[BLOCKED] 检测到高风险违规内容，已拦截，不送入大模型。"

    # 使用多行 f-string 与 XML 标签清晰隔离用户输入，降低提示词注入风险
    # 注意：JSON 示例中的花括号必须双写 {{ }} 进行转义
    prompt = f"""你是「杭州星辰数科」官方智能客服助手，专业、克制且高效。
当前服务客户等级：{customer_tier.upper()}
回复字数要求：不超过 {max_reply_words} 字，必须输出如下 JSON 格式：
{{"intent": "物流查询|退款售后|其他", "reply": "你的回复内容"}}

请严格基于以下标签内的用户原始提问作答：
<user_query>
{cleaned_query}
</user_query>"""
    return prompt


if __name__ == "__main__":
    sample_q = "  \n 麻烦问下 ord-99812 啥时候能送到杭州滨江？\u3000急用！ "
    final_prompt = render_support_prompt(sample_q, customer_tier="svip", max_reply_words=80)
    est_tokens = estimate_tokens_rough(final_prompt)
    print(final_prompt)
    print(f"\n--- 预估输入 Token 数: 约 {est_tokens} Tokens ---")

