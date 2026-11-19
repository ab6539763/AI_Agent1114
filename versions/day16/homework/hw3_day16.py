"""
Day 16 课后作业 3（架构进阶）：流式文本缓冲与按句推送适配器
工单：STARMIND-016
"""

from typing import Generator, Iterable
from src.day16_sampling_simulator import GenerationConfig
from src.day16_stream_client import StarMindStreamClient, StreamChunk

SENTENCE_ENDINGS = ("。", "！", "？")


def buffer_by_sentence(chunks: Iterable[StreamChunk]) -> Generator[str, None, None]:
    """将细粒度 Token 流聚合成完整句子流，适配实时 TTS/翻译下游。"""
    buf = ""
    for chunk in chunks:
        buf += chunk.delta_content
        while True:
            positions = [buf.find(p) for p in SENTENCE_ENDINGS if p in buf]
            if not positions:
                break
            cut = min(positions) + 1
            yield buf[:cut].strip()
            buf = buf[cut:]
    if buf.strip():
        yield buf.strip()


if __name__ == "__main__":
    client = StarMindStreamClient()
    stream = client.stream_chat(
        [{"role": "user", "content": "如何提升客服满意度？"}],
        GenerationConfig(temperature=0.4, max_tokens=200),
        chunk_size=3,
    )
    for sent in buffer_by_sentence(stream):
        print("整句推送 ->", sent)

