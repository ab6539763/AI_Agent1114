import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 36 自动化集成测试：使用 FastAPI TestClient 验证多格式入库、ACL权限隔离、问答与删除。"""

from fastapi.testclient import TestClient

from src.day36_kb_api import create_app


def test_health_and_seeded_qa_with_acl():
    client = TestClient(create_app())

    h = client.get("/health")
    assert h.status_code == 200
    assert h.json()["status"] == "ok"
    assert h.json()["doc_count"] == 4

    # 1. 公共 CSV 表格问答
    r_pub = client.post(
        "/api/v1/qa/query",
        json={"question": "一线城市北京出差住宿上限是多少？", "department": "public"},
    )
    assert r_pub.status_code == 200
    body = r_pub.json()
    assert body["refused"] is False
    assert "600元" in body["answer"]
    assert len(body["citations"]) >= 1

    # 2. 部门 ACL 隔离：研发人员不可查财务机密，财务人员可查
    r_rd_denied = client.post(
        "/api/v1/qa/query",
        json={"question": "2026年高管年终奖金池基数是多少？", "department": "rd"},
    )
    assert r_rd_denied.json()["refused"] is True

    r_fin_ok = client.post(
        "/api/v1/qa/query",
        json={"question": "2026年高管年终奖金池基数是多少？", "department": "finance"},
    )
    assert r_fin_ok.json()["refused"] is False
    assert "8%" in r_fin_ok.json()["answer"]


def test_ingest_upsert_and_delete_lifecycle():
    client = TestClient(create_app())

    # 入库一篇新 Markdown 文档
    r1 = client.post(
        "/api/v1/documents/ingest",
        json={
            "doc_id": "it-wifi-01",
            "source": "办公网指南.md",
            "format": "md",
            "department": "public",
            "content": "## 访客WiFi\n访客WiFi名称为 StarMind-Guest，每日密码需在行政钉钉群获取。",
        },
    )
    assert r1.status_code == 200
    assert r1.json()["chunks_created"] == 1

    # 同 doc_id 幂等更新覆盖旧内容
    r2 = client.post(
        "/api/v1/documents/ingest",
        json={
            "doc_id": "it-wifi-01",
            "source": "办公网指南_v2.md",
            "format": "md",
            "department": "public",
            "content": "## 访客WiFi\n访客WiFi已升级为 StarMind-Guest-5G，支持扫码一键认证。",
        },
    )
    assert r2.status_code == 200

    q = client.post("/api/v1/qa/query", json={"question": "访客WiFi怎么连接？", "department": "public"})
    assert "StarMind-Guest-5G" in q.json()["answer"]
    assert "钉钉群" not in q.json()["answer"]

    # 删除文档后应无法再次删除（404）
    d1 = client.delete("/api/v1/documents/it-wifi-01")
    assert d1.status_code == 200
    d2 = client.delete("/api/v1/documents/it-wifi-01")
    assert d2.status_code == 404


def test_out_of_domain_query_triggers_refusal():
    client = TestClient(create_app())
    r = client.post(
        "/api/v1/qa/query",
        json={"question": "火星大气层主要成分是什么？", "department": "public"},
    )
    assert r.status_code == 200
    assert r.json()["refused"] is True
    assert r.json()["citations"] == []

