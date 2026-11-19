"""
Day 22 课后作业 3（架构进阶）：SSE 跨网络包粘包/拆包解析器（Python 模拟前端缓冲逻辑）
工单：STARMIND-022
"""

import json
from typing import Any, Dict, Iterable, List


def parse_chunked_sse(raw_chunks: Iterable[str]) -> List[Dict[str, Any]]:
    """模拟前端 ReadableStream 缓冲机制，正确处理任意切分的 SSE 文本流。"""
    results: List[Dict[str, Any]] = []
    buffer = ""
    for chunk in raw_chunks:
        buffer += chunk
        lines = buffer.split("\n")
        buffer = lines.pop()
        for line in lines:
            if line.startswith("data: "):
                payload = line[6:].strip()
                if payload and payload != "[DONE]":
                    results.append(json.loads(payload))
    return results


if __name__ == "__main__":
    messy_chunks = ['data: {"del', 'ta":"你"}\n\ndata: {"del', 'ta":"好"}\n\n']
    print("解析结果:", parse_chunked_sse(messy_chunks))

