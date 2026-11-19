import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 24 自动化单元测试：端到端验证 SSE 流式推送、CORS 跨域、SQLite 跨重启持久化与前端页面托管。"""

import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.day24_chatgpt_backend import create_chatgpt_app


def test_frontend_html_and_cors_headers():
    client = TestClient(create_chatgpt_app())

    # 1. 验证前端聊天首页托管
    r_home = client.get("/")
    assert r_home.status_code == 200
    assert "text/html" in r_home.headers["content-type"]
    assert "/api/v1/chat/stream" in r_home.text

    # 2. 验证 CORS 跨域响应头
    r_cors = client.options(
        "/api/v1/chat/stream",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert r_cors.status_code == 200
    assert r_cors.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_sse_stream_and_sqlite_persistence_across_restarts(tmp_path: Path):
    db_file = tmp_path / "starmind_day24.db"
    db_url = f"sqlite:///{db_file}"

    # 第一次启动应用并发送 SSE 流式对话
    client1 = TestClient(create_chatgpt_app(database_url=db_url))
    chunks = []
    saw_done = False
    with client1.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"session_id": "persist_01", "message": "杭州出差住宿报销标准是多少？", "chunk_size": 8},
    ) as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        for line in resp.iter_lines():
            if line.startswith("data: "):
                raw = line[6:].strip()
                if raw == "[DONE]":
                    saw_done = True
                else:
                    chunks.append(json.loads(raw)["delta"])

    assembled = "".join(chunks)
    assert saw_done is True
    assert len(chunks) >= 3
    assert "600 元/晚" in assembled

    # 模拟服务重启：使用同一个 SQLite 文件重建全新 FastAPI 实例
    client2 = TestClient(create_chatgpt_app(database_url=db_url))
    r_hist = client2.get("/api/v1/sessions/persist_01")
    assert r_hist.status_code == 200
    msgs = r_hist.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert msgs[1]["content"] == assembled

    # 验证多轮跨重启记忆
    with client2.stream(
        "POST",
        "/api/v1/chat/stream",
        json={"session_id": "persist_01", "message": "我上一句问了什么？"},
    ) as resp2:
        text2 = "".join(
            json.loads(line[6:])["delta"]
            for line in resp2.iter_lines()
            if line.startswith("data: ") and line[6:].strip() != "[DONE]"
        )
    assert "杭州出差住宿报销标准" in text2

    # 验证级联删除
    assert client2.delete("/api/v1/sessions/persist_01").status_code == 200
    assert client2.get("/api/v1/sessions/persist_01").status_code == 404

