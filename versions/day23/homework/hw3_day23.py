"""
Day 23 课后作业 3（架构进阶）：全局请求耗时与 Request-ID 追踪中间件
工单：STARMIND-023
"""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()


@app.middleware("http")
async def add_observability_headers(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
    response.headers["X-Request-ID"] = uuid.uuid4().hex[:12]
    response.headers["X-Process-Time-Ms"] = str(elapsed_ms)
    return response


@app.get("/ping")
def ping():
    return {"pong": True}


if __name__ == "__main__":
    r = TestClient(app).get("/ping")
    print("Request-ID:", r.headers["X-Request-ID"], "| Time(ms):", r.headers["X-Process-Time-Ms"])

