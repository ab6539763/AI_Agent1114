"""
Day 15 课后作业 1（基础巩固）：上下文窗口安全守门员（Context Window Guard）
工单：STARMIND-015
"""

from typing import Dict, List
from src.day15_tokenizer import StarMindTokenizer


def check_context_fit(
    system_prompt: str,
    history: List[str],
    user_query: str,
    max_reply_tokens: int,
    context_window: int = 32_000,
) -> Dict[str, object]:
    """检查当前完整对话加上预留回复长度是否超出模型上下文窗口。"""
    tok = StarMindTokenizer("cn_optimized")
    used_input = (
        tok.count_tokens(system_prompt)
        + sum(tok.count_tokens(msg) for msg in history)
        + tok.count_tokens(user_query)
    )
    total_required = used_input + max_reply_tokens
    remaining = context_window - total_required
    return {
        "fits": remaining >= 0,
        "used_input_tokens": used_input,
        "total_required_tokens": total_required,
        "remaining_tokens": remaining,
    }


if __name__ == "__main__":
    res = check_context_fit(
        system_prompt="你是星辰数科智能助手。",
        history=["你好", "请问有什么可以帮您？"],
        user_query="请帮我写一份季度复盘大纲。",
        max_reply_tokens=1024,
        context_window=4096,
    )
    print(res)

