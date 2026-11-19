import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 37 全链路端到端集成测试：验证多会话隔离、多轮指代改写、安全高亮与 SSE 流式解析。"""

import json
from typing import Any, List, Tuple

from fastapi.testclient import TestClient

from src.day37_session_highlight import CitationHighlighter
from src.day37_sse_api import create_chat_app


def _parse_sse_frames(raw_text: str) -> List[Tuple[str, Any]]:
    frames: List[Tuple[str, Any]] = []
    for block in raw_text.strip().split("\n\n"):
        event_type = "message"
        data_str = ""
        for line in block.splitlines():
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data_str = line.split(":", 1)[1].strip()
        if data_str:
            frames.append((event_type, json.loads(data_str)))
    return frames


def test_citation_highlighter_prevents_xss_and_marks_keywords():
    raw = "年假需提前3天OA申请，<script>alert(1)</script>严禁绕过审批。"
    out = CitationHighlighter.highlight("年假提前OA申请", raw)
    assert "<script>" not in out
    assert "&lt;script&gt;" in out
    assert "<mark>年假</mark>" in out
    assert "<mark>OA</mark>" in out


def test_multi_session_isolation_and_multiturn_rewrite():
    client = TestClient(create_chat_app())

    sid_a = client.post("/api/v1/sessions", json={"title": "HR休假"}).json()["session_id"]
    sid_b = client.post("/api/v1/sessions", json={"title": "运维排障", "department": "rd"}).json()["session_id"]

    # Session A 第一轮聊年假
    r_a1 = client.post("/api/v1/chat/ask", json={"session_id": sid_a, "question": "入职满一年年假有几天？"})
    assert r_a1.status_code == 200
    assert "5天" in r_a1.json()["answer"]

    # Session B 第一轮聊 ERR-5042
    r_b1 = client.post(
        "/api/v1/chat/ask",
        json={"session_id": sid_b, "question": "ERR-5042 报错原因是什么？", "department": "rd"},
    )
    assert "超时" in r_b1.json()["answer"]

    # Session A 第二轮追问使用指代词「它」，应准确锚定到「年假」而非 Session B 的 ERR-5042
    r_a2 = client.post("/api/v1/chat/ask", json={"session_id": sid_a, "question": "它需要提前几天OA申请？"})
    body_a2 = r_a2.json()
    assert "年假" in body_a2["rewritten_query"]
    assert "ERR-5042" not in body_a2["rewritten_query"]
    assert "<mark>" in body_a2["citations"][0]["highlighted_snippet"]

    # 验证历史隔离：A 与 B 各自只有自己的记录
    hist_a = client.get(f"/api/v1/sessions/{sid_a}/history").json()["history"]
    hist_b = client.get(f"/api/v1/sessions/{sid_b}/history").json()["history"]
    assert len(hist_a) == 4  # 2 turns * 2 messages
    assert len(hist_b) == 2  # 1 turn * 2 messages


def test_sse_streaming_endpoint_full_protocol():
    client = TestClient(create_chat_app())
    sid = client.post("/api/v1/sessions", json={"title": "差旅SSE测试"}).json()["session_id"]

    # 第一轮同步建立上下文
    client.post("/api/v1/chat/ask", json={"session_id": sid, "question": "北京出差住酒店上限是多少？"})

    # 第二轮走 SSE 流式接口追问
    resp = client.post("/api/v1/chat/stream", json={"session_id": sid, "question": "那餐饮补助是多少？"})
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers["content-type"]
    assert resp.headers.get("x-accel-buffering") == "no"

    frames = _parse_sse_frames(resp.text)
    event_types = [ev for ev, _ in frames]
    assert event_types[0] == "meta"
    assert "citation" in event_types
    assert "token" in event_types
    assert event_types[-1] == "done"

    meta = frames[0][1]
    assert "出差" in meta["rewritten_query"]

    reconstructed = "".join(payload["delta"] for ev, payload in frames if ev == "token")
    assert "100元" in reconstructed

    # 确认流式回答已持久化进入历史
    hist = client.get(f"/api/v1/sessions/{sid}/history").json()["history"]
    assert len(hist) == 4
    assert hist[-1]["content"] == reconstructed

