"""
Day 21 课后作业 3（架构进阶）：流式事件转标准 SSE 文本帧格式化器
工单：STARMIND-021
"""

import json
from src.day21_integrated_engine import StreamEvent


def format_sse_frame(event: StreamEvent) -> str:
    """将 StreamEvent 转换为标准 HTTP Server-Sent Events 文本帧。"""
    payload = json.dumps(event.data, ensure_ascii=False)
    return f"event: {event.event_type}\ndata: {payload}\n\n"


if __name__ == "__main__":
    print(repr(format_sse_frame(StreamEvent("delta", {"text": "你好，星辰智脑"}))))

