"""
Day 16 课后作业 2（企业实战）：流式输出中断续写器（Auto-Continue on Length）
工单：STARMIND-016
"""

from typing import Dict, List
from src.day16_sampling_simulator import GenerationConfig
from src.day16_stream_client import StarMindStreamClient


def chat_with_auto_continue(
    messages: List[Dict[str, str]],
    config: GenerationConfig,
    max_rounds: int = 2,
) -> str:
    """当输出因 max_tokens 被截断时自动续写。"""
    client = StarMindStreamClient()
    conv = list(messages)
    collected: List[str] = []

    for _ in range(max_rounds + 1):
        chunks = list(client.stream_chat(conv, config, chunk_size=5))
        part = "".join(c.delta_content for c in chunks)
        collected.append(part)
        if chunks[-1].finish_reason != "length":
            break
        conv.append({"role": "assistant", "content": part})
        conv.append({"role": "user", "content": "请接着上面的内容继续"})

    return "\n".join(collected)


if __name__ == "__main__":
    msgs = [{"role": "user", "content": "请详细介绍星辰智脑架构"}]
    print(chat_with_auto_continue(msgs, GenerationConfig(temperature=0.2, max_tokens=20), max_rounds=1))

