"""
Day 37 - 步骤二：阶段项目二(下) 多会话管理与 SSE 流式问答 FastAPI 后端服务
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day37_session_highlight import StreamingKBService


class CreateSessionRequest(BaseModel):
    title: str = Field(default="新对话", max_length=64)
    department: str = Field(default="public")


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    question: str = Field(..., min_length=2, max_length=500)
    department: str = Field(default="public")


def create_chat_app(service: Optional[StreamingKBService] = None) -> FastAPI:
    svc = service if service is not None else StreamingKBService()
    app = FastAPI(
        title="StarMind-KB v2.0 多轮流式问答服务",
        version="2.1.0",
    )

    @app.post("/api/v1/sessions")
    def create_session(req: CreateSessionRequest) -> Dict[str, str]:
        sid = svc.sessions.create_session(title=req.title, department=req.department)
        return {"session_id": sid, "title": req.title, "department": req.department}

    @app.get("/api/v1/sessions")
    def list_sessions() -> Dict[str, Any]:
        items = svc.sessions.list_sessions()
        return {"total": len(items), "items": items}

    @app.get("/api/v1/sessions/{session_id}/history")
    def get_session_history(session_id: str) -> Dict[str, Any]:
        try:
            turns = svc.sessions.get_history(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {
            "session_id": session_id,
            "history": [
                {"role": t.role, "content": t.content, "rewritten_query": t.rewritten_query}
                for t in turns
            ],
        }

    @app.delete("/api/v1/sessions/{session_id}")
    def delete_session(session_id: str) -> Dict[str, Any]:
        if not svc.sessions.delete_session(session_id):
            raise HTTPException(status_code=404, detail="Session not found")
        return {"deleted": True, "session_id": session_id}

    @app.post("/api/v1/chat/ask")
    def chat_ask(req: ChatRequest) -> Dict[str, Any]:
        res = svc.prepare_answer(
            session_id=req.session_id,
            question=req.question,
            department=req.department,
        )
        return {
            "session_id": res["session_id"],
            "rewritten_query": res["rewritten_query"],
            "answer": res["answer"],
            "latency_ms": res["latency_ms"],
            "citations": [
                {
                    "index": c.index,
                    "doc_id": c.doc_id,
                    "source": c.source,
                    "section": c.section,
                    "highlighted_snippet": c.highlighted_snippet,
                    "score": c.score,
                }
                for c in res["citations"]
            ],
        }

    @app.post("/api/v1/chat/stream")
    def chat_stream(req: ChatRequest) -> StreamingResponse:
        # 生产级 SSE 必配响应头：禁止代理缓存与 Nginx 缓冲
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        return StreamingResponse(
            svc.stream_sse_events(
                session_id=req.session_id,
                question=req.question,
                department=req.department,
            ),
            media_type="text/event-stream",
            headers=headers,
        )

    return app


app = create_chat_app()

if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(create_chat_app())
    sid = client.post("/api/v1/sessions", json={"title": "差旅咨询"}).json()["session_id"]
    client.post("/api/v1/chat/ask", json={"session_id": sid, "question": "北京出差住酒店上限是多少？"})
    with client.stream("POST", "/api/v1/chat/stream", json={"session_id": sid, "question": "那餐饮补助呢？"}) as r:
        print("SSE Content-Type:", r.headers["content-type"])
        for line in r.iter_lines():
            if line:
                print(" ", line)

