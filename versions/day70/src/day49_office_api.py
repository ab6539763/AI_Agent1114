"""Day 49 - 步骤二：多 Agent 智能办公助手 FastAPI 生产级 REST 服务。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.day49_office_orchestrator import (
    OfficeAssistantOrchestrator,
    TaskConflictError,
    TaskNotFoundError,
)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="员工自然语言办公指令")
    user_id: str = Field(default="emp_01", description="当前登录员工工号")
    params: Dict[str, Any] = Field(default_factory=dict, description="可选结构化表单补充参数")
    thread_id: Optional[str] = Field(default=None, description="可选会话线程号")


class ConfirmRequest(BaseModel):
    approved: bool = Field(..., description="人工是否同意执行该高危动作")
    reviewer: str = Field(default="部门负责人", min_length=1)
    comment: str = Field(default="")


def create_office_app(db_path: Union[str, Path] = ":memory:") -> FastAPI:
    """工厂模式创建 FastAPI 应用实例，隔离测试与生产环境状态。"""
    app = FastAPI(title="星辰智脑多 Agent 智能办公助手 API", version="1.0.0")
    orchestrator = OfficeAssistantOrchestrator(db_path=db_path)
    app.state.orchestrator = orchestrator

    @app.get("/api/v1/health")
    def health_check() -> Dict[str, str]:
        return {"status": "ok", "service": "starmind-office-assistant"}

    @app.post("/api/v1/office/chat")
    def office_chat(req: ChatRequest) -> Dict[str, Any]:
        return orchestrator.chat(
            query=req.query,
            user_id=req.user_id,
            params=req.params,
            thread_id=req.thread_id,
        )

    @app.post("/api/v1/office/tasks/{thread_id}/confirm")
    def confirm_task(thread_id: str, req: ConfirmRequest) -> Dict[str, Any]:
        try:
            return orchestrator.confirm(
                thread_id=thread_id,
                approved=req.approved,
                reviewer=req.reviewer,
                comment=req.comment,
            )
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except TaskConflictError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.get("/api/v1/office/tasks/{thread_id}")
    def query_task(thread_id: str) -> Dict[str, Any]:
        try:
            return orchestrator.get_task(thread_id)
        except TaskNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(create_office_app(":memory:"))
    print("健康检查:", client.get("/api/v1/health").json())
    chat_res = client.post("/api/v1/office/chat", json={"query": "查询差旅报销制度"}).json()
    print("制度问答:", chat_res["status"], "|", chat_res["reply"])

