import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 23 自动化单元测试：使用 FastAPI TestClient 全面验证路由、Pydantic v2 校验与会话状态。"""

from fastapi.testclient import TestClient
from src.day23_fastapi_app import create_app


def test_health_and_models_query_params():
    client = TestClient(create_app())

    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "ok"

    r_all = client.get("/api/v1/models")
    assert r_all.status_code == 200
    assert len(r_all.json()) == 3

    r_filtered = client.get("/api/v1/models", params={"provider": "DeepSeek", "min_context": 50000})
    assert r_filtered.status_code == 200
    assert [m["model_id"] for m in r_filtered.json()] == ["deepseek-chat"]


def test_chat_multi_turn_and_session_lifecycle():
    client = TestClient(create_app())

    r1 = client.post("/api/v1/chat", json={"session_id": "s_100", "message": "杭州出差住宿怎么报销？"})
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["turn_count"] == 1
    assert "600 元/晚" in body1["reply"]

    r2 = client.post("/api/v1/chat", json={"session_id": "s_100", "message": "我刚才上一句问了什么？"})
    assert r2.status_code == 200
    assert "杭州出差住宿怎么报销" in r2.json()["reply"]
    assert r2.json()["turn_count"] == 2

    # 路径参数查询会话
    r_sess = client.get("/api/v1/sessions/s_100")
    assert r_sess.status_code == 200
    assert r_sess.json()["message_count"] == 4

    # 删除会话后再查询应返回 404
    r_del = client.delete("/api/v1/sessions/s_100")
    assert r_del.status_code == 200
    assert client.get("/api/v1/sessions/s_100").status_code == 404


def test_pydantic_v2_validation_errors_return_422():
    client = TestClient(create_app())

    # 空白消息触发 422
    assert client.post("/api/v1/chat", json={"session_id": "s_err", "message": "   "}).status_code == 422
    # 非法模型名触发 422
    assert client.post("/api/v1/chat", json={"session_id": "s_err", "message": "hi", "model": "unknown-llm"}).status_code == 422
    # 超界温度触发 422
    assert client.post("/api/v1/chat", json={"session_id": "s_err", "message": "hi", "temperature": 3.5}).status_code == 422

