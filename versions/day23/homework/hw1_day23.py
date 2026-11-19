"""
Day 23 课后作业 1（基础巩固）：为 FastAPI 添加 API Key 请求头鉴权依赖（Depends）
工单：STARMIND-023
"""

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient


def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "starmind-secret-2026":
        raise HTTPException(status_code=401, detail="无效的 API Key")
    return x_api_key


app = FastAPI()


@app.get("/api/v1/secret")
def secret_endpoint(api_key: str = Depends(verify_api_key)):
    return {"status": "authorized", "key_prefix": api_key[:8]}


if __name__ == "__main__":
    c = TestClient(app)
    print("错误 Key:", c.get("/api/v1/secret", headers={"X-API-Key": "bad"}).status_code)
    print("正确 Key:", c.get("/api/v1/secret", headers={"X-API-Key": "starmind-secret-2026"}).json())

