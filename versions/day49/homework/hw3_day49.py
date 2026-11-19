"""
Day 49 课后作业 3（架构进阶）：为 FastAPI 接入轻量请求耗时响应头中间件
工单：STARMIND-049
"""

"""Day 49 作业 3 参考答案：FastAPI 请求耗时与 Request-ID 响应头中间件。"""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()


@app.middleware("http")
async def add_observability_headers(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-Id"] = request.headers.get("X-Request-Id", f"req_{uuid.uuid4().hex[:8]}")
    response.headers["X-Process-Time-Ms"] = f"{(time.perf_counter() - t0) * 1000:.2f}"
    return response


@app.get("/ping")
def ping():
    return {"pong": True}


if __name__ == "__main__":
    client = TestClient(app)
    resp = client.get("/ping")
    print("响应头:", resp.headers["X-Request-Id"], "| 耗时(ms):", resp.headers["X-Process-Time-Ms"])
    assert "X-Request-Id" in resp.headers and "X-Process-Time-Ms" in resp.headers

