"""
StarMind Day 23 - 步骤二：FastAPI 企业级 RESTful AI 对话服务
演示路径参数、查询参数、Pydantic v2 校验、HTTPException 规范错误与工厂模式隔离。
"""

from typing import Dict, List
from fastapi import FastAPI, HTTPException, Query

from src.day23_schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MessageRecord,
    ModelInfo,
    SessionDetailResponse,
)


BUILTIN_MODELS: List[ModelInfo] = [
    ModelInfo(model_id="deepseek-chat", provider="DeepSeek", context_window=64000, supports_tools=True),
    ModelInfo(model_id="qwen-max", provider="Alibaba", context_window=32000, supports_tools=True),
    ModelInfo(model_id="glm-4-plus", provider="Zhipu", context_window=128000, supports_tools=True),
]


def _generate_enterprise_reply(message: str, history: List[MessageRecord], model: str) -> str:
    """离线确定性企业问答回复生成器（无外网依赖，便于联调与自动化测试）。"""
    if "差旅" in message or "住宿" in message:
        return f"[{model}] 根据星辰数科 HR-001 制度，北京/上海/深圳/杭州出差住宿上限为 600 元/晚，需提供电子专票。"
    if "vpn" in message.lower():
        return f"[{model}] 请在 OA 系统发起『IT权限申请』，主管审批后 30 分钟内自动开通 WireGuard VPN。"
    if "上一句" in message or "刚才" in message:
        prev_users = [m.content for m in history if m.role == "user"]
        if prev_users:
            return f"[{model}] 您上一轮提到的问题是：「{prev_users[-1]}」。"
    return f"[{model}] 星辰智脑已收到您的咨询「{message}」，当前已为您记录至企业会话上下文。"


def create_app() -> FastAPI:
    """应用工厂函数：每次调用返回状态完全隔离的 FastAPI 实例。"""
    app = FastAPI(
        title="星辰智脑 StarMind REST API",
        description="杭州星辰数科企业级 AI 对话后端服务（Day 23 版本）",
        version="0.23.0",
    )

    # 实例级内存会话存储（Day 24 将升级为 SQLite + SQLAlchemy 持久化）
    sessions: Dict[str, List[MessageRecord]] = {}

    @app.get("/health", response_model=HealthResponse, tags=["System"])
    def health_check() -> HealthResponse:
        return HealthResponse()

    @app.get("/api/v1/models", response_model=List[ModelInfo], tags=["Models"])
    def list_models(
        provider: str | None = Query(default=None, description="按厂商名称过滤（不区分大小写）"),
        min_context: int = Query(default=0, ge=0, description="按最小上下文窗口过滤"),
    ) -> List[ModelInfo]:
        results = BUILTIN_MODELS
        if provider:
            results = [m for m in results if m.provider.lower() == provider.lower()]
        if min_context > 0:
            results = [m for m in results if m.context_window >= min_context]
        return results

    @app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
    def chat_endpoint(req: ChatRequest) -> ChatResponse:
        history = sessions.setdefault(req.session_id, [])
        reply_text = _generate_enterprise_reply(req.message, history, req.model)
        # 按 max_tokens 做安全输出截断保护
        reply_text = reply_text[: req.max_tokens]

        history.append(MessageRecord(role="user", content=req.message))
        history.append(MessageRecord(role="assistant", content=reply_text))

        est_tokens = max(1, (len(req.message) + len(reply_text)) // 2)
        return ChatResponse(
            session_id=req.session_id,
            model=req.model,
            reply=reply_text,
            turn_count=len(history) // 2,
            estimated_tokens=est_tokens,
        )

    @app.get("/api/v1/sessions/{session_id}", response_model=SessionDetailResponse, tags=["Sessions"])
    def get_session(session_id: str) -> SessionDetailResponse:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail=f"会话 '{session_id}' 不存在")
        msgs = sessions[session_id]
        return SessionDetailResponse(session_id=session_id, message_count=len(msgs), messages=msgs)

    @app.delete("/api/v1/sessions/{session_id}", tags=["Sessions"])
    def delete_session(session_id: str) -> Dict[str, str]:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail=f"会话 '{session_id}' 不存在")
        del sessions[session_id]
        return {"status": "deleted", "session_id": session_id}

    return app


app = create_app()


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(create_app())
    print("健康检查:", client.get("/health").json())
    print("模型过滤:", client.get("/api/v1/models?provider=DeepSeek").json())
    resp = client.post("/api/v1/chat", json={"session_id": "demo_01", "message": "杭州出差住宿报销标准？"})
    print("对话响应:", resp.json())

