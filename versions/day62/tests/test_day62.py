import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 62 单元测试：FastAPI 全量 REST/SSE 接口与前端解析联调"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day62_api_server import create_app
from src.day62_console_client import parse_sse_stream


def test_health_and_trace_header():
    client = TestClient(create_app())
    r1 = client.get("/healthz")
    r2 = client.get("/readyz", headers={"X-Trace-Id": "tr-custom-99"})
    assert r1.status_code == 200 and r1.headers["X-Trace-Id"].startswith("tr-")
    assert r2.status_code == 200 and r2.headers["X-Trace-Id"] == "tr-custom-99"
    assert r2.json()["docs_count"] == 2


def test_dynamic_doc_upsert_and_sse_stream():
    client = TestClient(create_app())
    up = client.post(
        "/api/v1/knowledge/docs",
        json={"doc_id": "DOC-09", "title": "年假政策", "content": "入职满一年享受10天带薪年假。"},
    )
    assert up.status_code == 200 and up.json()["total_docs"] == 3

    stream_resp = client.post("/api/v1/chat/stream", json={"session_id": "s9", "query": "年假有几天？"})
    assert stream_resp.status_code == 200
    assert "text/event-stream" in stream_resp.headers["content-type"]
    assert stream_resp.headers["X-Accel-Buffering"] == "no"

    parsed = parse_sse_stream(stream_resp.text)
    assert "[DOC-09]" in parsed.full_text
    assert len(parsed.chunks) >= 2
    assert parsed.done["status"] == "COMPLETED"


def test_approval_workflow_and_conflict_guard():
    client = TestClient(create_app())
    r = client.post("/api/v1/chat", json={"session_id": "s10", "query": "提交采购报销 6800 元"})
    body = r.json()
    assert body["status"] == "PENDING_APPROVAL"
    tid = body["ticket_id"]

    ok = client.post(f"/api/v1/approvals/{tid}", json={"approve": True, "approver": "王总", "note": "同意"})
    assert ok.status_code == 200 and ok.json()["status"] == "APPROVED_EXECUTED"

    dup = client.post(f"/api/v1/approvals/{tid}", json={"approve": True, "approver": "王总"})
    assert dup.status_code == 409

