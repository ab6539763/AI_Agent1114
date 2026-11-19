"""
Day 62 - 模块一：星辰智脑 FastAPI 全量 REST + SSE 后端服务
"""
from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, Iterator, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field


class DocCreateRequest(BaseModel):
    doc_id: str = Field(..., min_length=2, max_length=32)
    title: str = Field(..., min_length=2, max_length=100)
    content: str = Field(..., min_length=4, max_length=2000)


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    query: str = Field(..., min_length=1, max_length=1000)
    employee: str = Field(default="张明", max_length=32)


class ApprovalDecisionRequest(BaseModel):
    approve: bool
    approver: str = Field(..., min_length=1, max_length=32)
    note: str = Field(default="", max_length=200)


class StarMindServiceState:
    """轻量可测试的服务内存状态（生产可无缝替换为 SQLAlchemy + Redis）"""

    def __init__(self) -> None:
        self.docs: Dict[str, Dict[str, str]] = {
            "DOC-01": {
                "doc_id": "DOC-01",
                "title": "差旅住宿报销标准",
                "content": "一线城市出差住宿上限650元/晚，需在费用中心上传电子专票核销。",
            },
            "DOC-02": {
                "doc_id": "DOC-02",
                "title": "网关错误码ERR_4291手册",
                "content": "错误码ERR_4291表示部门日Token配额已触发硬熔断，请联系管理员提额。",
            },
        }
        self.tickets: Dict[str, Dict[str, Any]] = {}

    def search_doc(self, query: str) -> Optional[Dict[str, str]]:
        q_low = query.lower()
        best_doc, best_hits = None, 0
        for doc in self.docs.values():
            hay = f"{doc['title']} {doc['content']}".lower()
            hits = sum(1 for ch in set(q_low) if ch.strip() and ch in hay)
            if hits > best_hits:
                best_hits, best_doc = hits, doc
        return best_doc if best_hits >= 2 else None

    def handle_chat(self, req: ChatRequest) -> Dict[str, Any]:
        if any(k in req.query for k in ("报销", "提交")) and re.search(r"\d+", req.query):
            amount = float(re.search(r"(\d+(?:\.\d+)?)", req.query).group(1))
            if amount > 2000:
                tid = f"APR-{uuid.uuid4().hex[:6].upper()}"
                self.tickets[tid] = {
                    "ticket_id": tid,
                    "session_id": req.session_id,
                    "employee": req.employee,
                    "amount": amount,
                    "status": "PENDING",
                }
                return {
                    "session_id": req.session_id,
                    "routed_agent": "action_agent",
                    "status": "PENDING_APPROVAL",
                    "ticket_id": tid,
                    "answer": f"报销金额 {amount:.2f} 元超过2000元上限，已转主管审批（单号 {tid}）。",
                }
            return {
                "session_id": req.session_id,
                "routed_agent": "action_agent",
                "status": "COMPLETED",
                "ticket_id": None,
                "answer": f"报销单已自动提交成功，金额 {amount:.2f} 元。",
            }

        hit = self.search_doc(req.query)
        if hit:
            return {
                "session_id": req.session_id,
                "routed_agent": "knowledge_agent",
                "status": "COMPLETED",
                "ticket_id": None,
                "answer": f"{hit['content']} [{hit['doc_id']}]",
            }
        return {
            "session_id": req.session_id,
            "routed_agent": "knowledge_agent",
            "status": "COMPLETED",
            "ticket_id": None,
            "answer": "知识库未检索到相关条款，为防幻觉暂不作答。",
        }


def create_app() -> FastAPI:
    app = FastAPI(title="StarMind Enterprise AI API", version="1.0.0")
    state = StarMindServiceState()
    app.state.starmind = state

    @app.middleware("http")
    async def trace_id_middleware(request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or f"tr-{uuid.uuid4().hex[:8]}"
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response

    @app.get("/healthz")
    def healthz() -> Dict[str, str]:
        return {"status": "alive"}

    @app.get("/readyz")
    def readyz() -> Dict[str, Any]:
        return {"status": "ready", "docs_count": len(state.docs)}

    @app.post("/api/v1/knowledge/docs")
    def upsert_doc(req: DocCreateRequest) -> Dict[str, Any]:
        state.docs[req.doc_id] = req.model_dump()
        return {"ok": True, "doc_id": req.doc_id, "total_docs": len(state.docs)}

    @app.post("/api/v1/chat")
    def chat(req: ChatRequest, request: Request) -> Dict[str, Any]:
        res = state.handle_chat(req)
        res["trace_id"] = request.state.trace_id
        return res

    @app.post("/api/v1/chat/stream")
    def chat_stream(req: ChatRequest, request: Request) -> StreamingResponse:
        res = state.handle_chat(req)
        trace_id = request.state.trace_id

        def event_generator() -> Iterator[str]:
            meta = {"trace_id": trace_id, "routed_agent": res["routed_agent"], "status": res["status"]}
            yield f"event: meta\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"
            text = res["answer"]
            step = 10
            for i in range(0, len(text), step):
                chunk = {"delta": text[i : i + step]}
                yield f"event: delta\ndata: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            done = {"status": res["status"], "ticket_id": res["ticket_id"]}
            yield f"event: done\ndata: {json.dumps(done, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/api/v1/approvals/{ticket_id}")
    def decide_approval(ticket_id: str, req: ApprovalDecisionRequest) -> Dict[str, Any]:
        if ticket_id not in state.tickets:
            raise HTTPException(status_code=404, detail="审批单不存在")
        ticket = state.tickets[ticket_id]
        if ticket["status"] != "PENDING":
            raise HTTPException(status_code=409, detail="审批单已处理，禁止重复操作")
        ticket["status"] = "APPROVED_EXECUTED" if req.approve else "REJECTED"
        ticket["approver"] = req.approver
        ticket["note"] = req.note
        return ticket

    return app


app = create_app()

if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(app)
    print("健康探针:", client.get("/healthz").json())
    r = client.post("/api/v1/chat", json={"session_id": "s1", "query": "差旅住宿标准"})
    print("同步对话:", r.status_code, r.headers["X-Trace-Id"], r.json()["answer"])

