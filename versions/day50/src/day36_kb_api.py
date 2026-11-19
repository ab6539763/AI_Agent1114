"""
Day 36 - 步骤二：阶段项目二(上) StarMind-KB v2.0 FastAPI 后端服务
提供：健康检查、多格式文档入库(Upsert)、文档列表/删除、混合检索+Rerank 问答 API
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day36_kb_engine import EnterpriseKBEngine, build_seeded_kb_engine


class IngestRequest(BaseModel):
    doc_id: str = Field(..., min_length=2, max_length=64, description="文档唯一ID（同ID重复入库自动覆盖）")
    source: str = Field(..., min_length=1, description="文档文件名")
    format: str = Field(..., pattern="^(md|txt|json|csv)$", description="文档格式：md/txt/json/csv")
    content: str = Field(..., min_length=1, description="文档原始内容")
    department: str = Field(default="public", description="可见部门：public/rd/finance/hr")


class IngestResponse(BaseModel):
    doc_id: str
    chunks_created: int
    status: str = "ingested"


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)
    department: str = Field(default="public")
    use_rerank: bool = Field(default=True)


class CitationDTO(BaseModel):
    doc_id: str
    source: str
    section: str
    snippet: str
    score: float


class QueryResponse(BaseModel):
    question: str
    answer: str
    citations: List[CitationDTO]
    refused: bool
    latency_ms: float
    used_rerank: bool


def create_app(engine: Optional[EnterpriseKBEngine] = None) -> FastAPI:
    """FastAPI 应用工厂：支持生产默认预置知识库，也支持测试注入独立隔离引擎。"""
    kb = engine if engine is not None else build_seeded_kb_engine()
    app = FastAPI(
        title="StarMind-KB v2.0 企业级知识库问答系统",
        version="2.0.0",
        description="杭州星辰数科企业知识库：多格式入库 + ACL权限过滤 + BM25/向量混合检索 + Rerank",
    )

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {
            "status": "ok",
            "doc_count": len(kb.doc_registry),
            "chunk_count": len(kb.chunks),
        }

    @app.post("/api/v1/documents/ingest", response_model=IngestResponse)
    def ingest_document(req: IngestRequest) -> IngestResponse:
        try:
            count = kb.ingest_document(
                doc_id=req.doc_id,
                source=req.source,
                fmt=req.format,
                content=req.content,
                department=req.department,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"文档解析失败: {exc}") from exc
        return IngestResponse(doc_id=req.doc_id, chunks_created=count)

    @app.get("/api/v1/documents")
    def list_documents() -> Dict[str, Any]:
        docs = kb.list_documents()
        return {"total": len(docs), "items": docs}

    @app.delete("/api/v1/documents/{doc_id}")
    def delete_document(doc_id: str) -> Dict[str, Any]:
        deleted = kb.delete_document(doc_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"文档 {doc_id} 不存在")
        return {"deleted": True, "doc_id": doc_id}

    @app.post("/api/v1/qa/query", response_model=QueryResponse)
    def qa_query(req: QueryRequest) -> QueryResponse:
        res = kb.query(
            question=req.question,
            top_k=req.top_k,
            department=req.department,
            use_rerank=req.use_rerank,
        )
        return QueryResponse(
            question=res.question,
            answer=res.answer,
            citations=[
                CitationDTO(
                    doc_id=c.doc_id,
                    source=c.source,
                    section=c.section,
                    snippet=c.snippet,
                    score=c.score,
                )
                for c in res.citations
            ],
            refused=res.refused,
            latency_ms=res.latency_ms,
            used_rerank=res.used_rerank,
        )

    return app


app = create_app()

if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    print("GET /health ->", client.get("/health").json())
    resp = client.post("/api/v1/qa/query", json={"question": "北京出差住宿上限是多少？", "department": "public"})
    print("POST /api/v1/qa/query ->", resp.json()["answer"])

