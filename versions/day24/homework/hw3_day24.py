"""
Day 24 课后作业 3（架构进阶）：SSE 心跳保活（Heartbeat）流式生成器包装器
工单：STARMIND-024
"""

from typing import Generator, Iterable


def with_sse_heartbeat(data_frames: Iterable[str]) -> Generator[str, None, None]:
    """在 SSE 流开头注入标准注释心跳帧，防止长推理期间代理网关超时断连。"""
    yield ": keep-alive\n\n"
    for frame in data_frames:
        yield frame


if __name__ == "__main__":
    sample = ['data: {"delta": "你好"}\n\n', "data: [DONE]\n\n"]
    print(list(with_sse_heartbeat(sample)))

