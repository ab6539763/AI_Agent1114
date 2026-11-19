"""
Day 23 课后作业 2（企业实战）：批量对话评测接口（Batch Chat Endpoint）
工单：STARMIND-023
"""

from typing import List
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from src.day23_schemas import ChatRequest


class BatchChatRequest(BaseModel):
    items: List[ChatRequest] = Field(..., min_length=1, max_length=10)


app = FastAPI()


@app.post("/api/v1/chat/batch")
def batch_chat(payload: BatchChatRequest):
    return {
        "count": len(payload.items),
        "replies": [{"session_id": item.session_id, "echo": item.message} for item in payload.items],
    }


if __name__ == "__main__":
    c = TestClient(app)
    ok = c.post("/api/v1/chat/batch", json={"items": [{"session_id": "s1", "message": "hello"}]})
    print("批量结果:", ok.status_code, ok.json())

