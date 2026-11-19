"""
Day 62 课后作业 1（基础巩固）：基础巩固：为 FastAPI 服务增加请求参数校验失败测试用例
工单：STARMIND-062
"""

from fastapi.testclient import TestClient
from src.day62_api_server import create_app

client = TestClient(create_app())
resp = client.post("/api/v1/chat", json={"session_id": "s1", "query": ""})
assert resp.status_code == 422
print("空提问 422 校验拦截通过")

