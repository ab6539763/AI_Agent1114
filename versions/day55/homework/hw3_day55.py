"""
Day 55 课后作业 3（架构进阶）：架构进阶：模拟 Prefix Caching 在多轮 RAG 对话中的显存与 Prefill 加速收益
工单：STARMIND-055
"""

def calc_prefix_cache_gain(shared_prompt_tokens: int, user_token_lens: list[int]) -> float:
    without_cache = sum(shared_prompt_tokens + u for u in user_token_lens)
    with_cache = shared_prompt_tokens + sum(user_token_lens)
    return round((without_cache - with_cache) / without_cache * 100, 2)


gain = calc_prefix_cache_gain(800, [220, 310, 450, 280, 390, 260, 500, 330, 290, 410])
print(f"开启 Prefix Caching 后 Prefill 计算量直降: {gain}%")

