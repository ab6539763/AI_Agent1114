"""
Day 62 - 模块二：前端控制台 SSE 事件解析器与端到端联调客户端
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ParsedSSEMessage:
    meta: Dict[str, Any] = field(default_factory=dict)
    chunks: List[str] = field(default_factory=list)
    done: Dict[str, Any] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return "".join(self.chunks)


def parse_sse_stream(raw_sse: str) -> ParsedSSEMessage:
    """解析标准 SSE 文本流（按双换行分帧，提取 event 与 JSON data）"""
    parsed = ParsedSSEMessage()
    frames = [f.strip() for f in raw_sse.strip().split("\n\n") if f.strip()]
    for frame in frames:
        event_name = "message"
        data_lines: List[str] = []
        for line in frame.splitlines():
            if line.startswith("event:"):
                event_name = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data_lines.append(line.split(":", 1)[1].strip())
        if not data_lines:
            continue
        payload = json.loads("\n".join(data_lines))
        if event_name == "meta":
            parsed.meta = payload
        elif event_name == "delta":
            parsed.chunks.append(payload.get("delta", ""))
        elif event_name == "done":
            parsed.done = payload
    return parsed


if __name__ == "__main__":
    from fastapi.testclient import TestClient
    from src.day62_api_server import create_app

    client = TestClient(create_app())
    resp = client.post("/api/v1/chat/stream", json={"session_id": "fe-1", "query": "报错 ERR_4291 怎么办"})
    msg = parse_sse_stream(resp.text)
    print("SSE 元信息:", msg.meta)
    print("分片数量:", len(msg.chunks))
    print("完整回复:", msg.full_text)

