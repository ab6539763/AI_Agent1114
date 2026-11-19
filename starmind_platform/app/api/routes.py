"""
星辰智脑 StarMind FastAPI 全量 REST + SSE 路由模块。

提供 16 个企业级生产接口：
- 健康检查与可观测性：`GET /api/v1/health`、`GET /api/v1/metrics`
- 多轮对话与流式输出：`POST /api/v1/chat`、`POST /api/v1/chat/stream`、`GET /api/v1/sessions/{session_id}`
- 企业混合检索 RAG：`POST /api/v1/rag/ingest`、`POST /api/v1/rag/query`、`POST /api/v1/rag/eval`
- Agent 编排引擎：`POST /api/v1/agent/react`、`POST /api/v1/agent/workflow`、
  `POST /api/v1/agent/workflow/{thread_id}/resume`、`POST /api/v1/agent/multi`、`POST /api/v1/agent/sql`
- MCP 协议网关：`GET /api/v1/mcp/tools`、`POST /api/v1/mcp/rpc`
- 微调工程流水线：`POST /api/v1/finetune/prepare`
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Literal, Optional

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from starmind_platform.app.agent.engine import (
    MCPServer,
    MultiAgentSupervisor,
    ReActAgent,
    SQLiteCheckpointer,
    StateGraph,
    TextToSQLAgent,
    ToolRegistry,
    build_default_tool_registry,
    build_enterprise_approval_workflow,
)
from starmind_platform.app.config import Settings, get_settings
from starmind_platform.app.core.guardrails import EnterpriseGuardrails
from starmind_platform.app.core.logging_utils import get_trace_id
from starmind_platform.app.core.observability import get_observability
from starmind_platform.app.db.database import DatabaseManager
from starmind_platform.app.finetune.pipeline import FinetunePipeline
from starmind_platform.app.llm.client import BaseLLM, create_llm_client
from starmind_platform.app.rag.engine import RAGPipeline

router = APIRouter(prefix="/api/v1", tags=["StarMind Enterprise API"])


# ==============================================================================
# 平台运行时依赖容器（统一管理各业务子引擎实例）
# ==============================================================================


class PlatformContainer:
    """集中持有星辰智脑平台各子系统实例，便于生命周期管理与测试替换。"""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.settings.ensure_data_dir()

        self.db = DatabaseManager(self.settings.database_url)
        self.db.init_db()

        self.llm: BaseLLM = create_llm_client(self.settings)
        self.guardrails = EnterpriseGuardrails(enable_pii_masking=self.settings.enable_pii_masking)
        self.rag = RAGPipeline(
            llm=self.llm,
            persist_path=self.settings.vector_store_path,
            chunk_size=self.settings.rag_chunk_size,
            chunk_overlap=self.settings.rag_chunk_overlap,
            min_confidence=self.settings.rag_min_confidence,
        )
        self.tool_registry: ToolRegistry = build_default_tool_registry(self.rag)
        self.react_agent = ReActAgent(
            llm=self.llm,
            tool_registry=self.tool_registry,
            max_steps=self.settings.agent_max_steps,
        )

        cp_path = Path(self.settings.data_dir) / "workflow_checkpoints.db"
        self.workflow: StateGraph = build_enterprise_approval_workflow(
            checkpointer=SQLiteCheckpointer(cp_path)
        )
        self.multi_agent = MultiAgentSupervisor(llm=self.llm, rag_pipeline=self.rag)
        self.sql_agent = TextToSQLAgent(llm=self.llm, db_manager=self.db)
        self.mcp_server = MCPServer(self.tool_registry)
        self.finetune = FinetunePipeline()


def _get_container(request: Request) -> PlatformContainer:
    return request.app.state.container


# ==============================================================================
# Pydantic 请求数据模型
# ==============================================================================


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="会话 ID，为空时自动生成")
    message: str = Field(..., min_length=1, description="用户输入消息")
    system_prompt: Optional[str] = Field(default=None, description="可选自定义系统提示词")


class RAGIngestRequest(BaseModel):
    doc_name: str = Field(..., min_length=1, description="文档名称（将作为溯源引用标签）")
    content: str = Field(..., min_length=1, description="文档原始内容")
    doc_format: str = Field(default="md", description="文档格式：txt / md / csv / json")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="自定义元数据标签，如部门/密级")


class RAGQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="知识库检索问题")
    top_k: int = Field(default=4, ge=1, le=10, description="返回参考片段数")
    metadata_filter: Optional[Dict[str, Any]] = Field(default=None, description="可选元数据过滤条件")
    use_query_rewrite: bool = Field(default=True, description="是否开启查询改写")


class RAGEvalRequest(BaseModel):
    question: str = Field(..., min_length=1, description="待评估问题")
    ground_truth: Optional[str] = Field(default=None, description="可选标准参考答案")
    top_k: int = Field(default=4, ge=1, le=10)


class ReActRequest(BaseModel):
    query: str = Field(..., min_length=1, description="需要 Agent 推理与调用工具解决的任务")


class WorkflowStartRequest(BaseModel):
    applicant: str = Field(default="张工", description="申请人姓名")
    item: str = Field(..., min_length=1, description="申请事项名称")
    amount: float = Field(..., ge=0.0, description="申请金额（元）；>=5000 元自动触发人工审批中断")
    thread_id: Optional[str] = Field(default=None, description="可选工作流线程 ID")


class WorkflowResumeRequest(BaseModel):
    approved: bool = Field(default=True, description="人工审批是否同意")
    reviewer: str = Field(default="王总监", description="审批人姓名")
    comment: str = Field(default="核对无误，同意放行", description="审批意见")


class MultiAgentRequest(BaseModel):
    task: str = Field(..., min_length=1, description="复杂企业分析/方案撰写任务")


class TextToSQLRequest(BaseModel):
    question: str = Field(..., min_length=1, description="自然语言销售数据查询问题")
    override_sql: Optional[str] = Field(default=None, description="可选显式指定只读 SQL（用于安全审计测试）")


class MCPRPCRequest(BaseModel):
    jsonrpc: str = Field(default="2.0")
    id: Any = Field(default=1)
    method: str = Field(..., min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)


class FinetunePrepareRequest(BaseModel):
    samples: List[Dict[str, Any]] = Field(..., min_length=1, description="原始问答/指令样本列表")
    dataset_format: Literal["alpaca", "sharegpt"] = Field(default="alpaca")
    base_model: str = Field(default="Qwen/Qwen2.5-7B-Instruct")
    dataset_name: str = Field(default="starmind_enterprise_sft")
    lora_rank: int = Field(default=16, ge=4, le=128)
    use_qlora_4bit: bool = Field(default=False)


# ==============================================================================
# 1. 健康检查与可观测性接口
# ==============================================================================


@router.get("/health", summary="系统健康检查")
def health_check(request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    return {
        "status": "healthy",
        "app_name": container.settings.app_name,
        "version": container.settings.app_version,
        "llm_provider": container.llm.provider,
        "llm_model": container.llm.model,
        "kb_chunks": len(container.rag.vector_store.chunks),
        "tools_count": len(container.tool_registry.list_tools()),
        "trace_id": get_trace_id(),
    }


@router.get("/metrics", summary="平台可观测性指标与链路大盘")
def get_metrics(request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    summary = get_observability().get_summary(recent_limit=25)
    summary["llm_provider"] = container.llm.provider
    summary["llm_model"] = container.llm.model
    summary["kb_chunks"] = len(container.rag.vector_store.chunks)
    return summary


# ==============================================================================
# 2. 多轮对话、SSE 流式接口与会话历史查询
# ==============================================================================


@router.post("/chat", summary="企业级多轮对话（持久化 + 安全护栏 + PII 脱敏）")
def chat_endpoint(payload: ChatRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    session_id = payload.session_id or f"sess-{uuid.uuid4().hex[:10]}"

    # 输入安全护栏校验与 PII 脱敏
    guard_res = container.guardrails.check_input(payload.message, raise_on_block=True)
    sanitized_input = guard_res.sanitized_text

    # 拉取历史多轮消息并组装上下文
    history = container.db.get_session_messages(session_id, limit=20)
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": payload.system_prompt
            or "你是杭州星辰数科企业级智能助手「星辰智脑 StarMind」，请专业、简洁地回答用户问题。",
        }
    ]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": sanitized_input})

    llm_resp = container.llm.chat(messages)
    safe_reply = container.guardrails.sanitize_output(llm_resp.content)

    # 持久化本轮用户与助手消息（仅存储脱敏后的文本）
    container.db.append_message(session_id=session_id, role="user", content=sanitized_input)
    container.db.append_message(
        session_id=session_id,
        role="assistant",
        content=safe_reply,
        model=llm_resp.model,
        tokens=llm_resp.total_tokens,
        cost_cny=llm_resp.cost_cny,
    )
    container.db.record_audit(
        action="chat",
        status="ok",
        detail=f"session={session_id}, pii_masked={guard_res.masked_entities}",
    )

    return {
        "session_id": session_id,
        "reply": safe_reply,
        "sanitized_input": sanitized_input,
        "masked_entities": guard_res.masked_entities,
        "usage": {
            "model": llm_resp.model,
            "provider": llm_resp.provider,
            "prompt_tokens": llm_resp.prompt_tokens,
            "completion_tokens": llm_resp.completion_tokens,
            "total_tokens": llm_resp.total_tokens,
            "cost_cny": llm_resp.cost_cny,
            "latency_ms": llm_resp.latency_ms,
        },
        "trace_id": get_trace_id(),
    }


@router.post("/chat/stream", summary="SSE 流式打字机对话接口")
async def chat_stream_endpoint(payload: ChatRequest, request: Request) -> StreamingResponse:
    container = _get_container(request)
    session_id = payload.session_id or f"sess-{uuid.uuid4().hex[:10]}"

    guard_res = container.guardrails.check_input(payload.message, raise_on_block=True)
    sanitized_input = guard_res.sanitized_text

    history = container.db.get_session_messages(session_id, limit=20)
    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": payload.system_prompt
            or "你是杭州星辰数科企业级智能助手「星辰智脑 StarMind」。",
        }
    ]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": sanitized_input})
    container.db.append_message(session_id=session_id, role="user", content=sanitized_input)

    async def event_generator() -> AsyncIterator[str]:
        chunks: List[str] = []
        meta_evt = {"type": "meta", "session_id": session_id, "masked_entities": guard_res.masked_entities}
        yield f"data: {json.dumps(meta_evt, ensure_ascii=False)}\n\n"

        async for delta in container.llm.stream_chat(messages):
            chunks.append(delta)
            yield f"data: {json.dumps({'type': 'delta', 'content': delta}, ensure_ascii=False)}\n\n"

        full_reply = container.guardrails.sanitize_output("".join(chunks))
        container.db.append_message(
            session_id=session_id,
            role="assistant",
            content=full_reply,
            model=container.llm.model,
        )
        yield f"data: {json.dumps({'type': 'done', 'session_id': session_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/sessions/{session_id}", summary="查询指定会话的历史对话记录")
def get_session_history(session_id: str, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    messages = container.db.get_session_messages(session_id, limit=100)
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages,
    }


# ==============================================================================
# 3. 企业混合检索 RAG 接口
# ==============================================================================


@router.post("/rag/ingest", summary="知识库文档解析切分与向量入库")
def rag_ingest_endpoint(payload: RAGIngestRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    return container.rag.ingest_document(
        doc_name=payload.doc_name,
        content=payload.content,
        doc_format=payload.doc_format,
        metadata=payload.metadata,
    )


@router.post("/rag/query", summary="混合检索 + 重排序 + 溯源标注问答")
def rag_query_endpoint(payload: RAGQueryRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    guard_res = container.guardrails.check_input(payload.question, raise_on_block=True)
    return container.rag.query(
        guard_res.sanitized_text,
        top_k=payload.top_k,
        metadata_filter=payload.metadata_filter,
        use_query_rewrite=payload.use_query_rewrite,
    )


@router.post("/rag/eval", summary="Ragas 风格 RAG 自动化质量评估")
def rag_eval_endpoint(payload: RAGEvalRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    return container.rag.evaluate_query(
        question=payload.question,
        ground_truth=payload.ground_truth,
        top_k=payload.top_k,
    )


# ==============================================================================
# 4. Agent 编排引擎接口（ReAct / StateGraph 审批流 / Multi-Agent / Text-to-SQL）
# ==============================================================================


@router.post("/agent/react", summary="ReAct 推理与企业工具调用 Agent")
def agent_react_endpoint(payload: ReActRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    guard_res = container.guardrails.check_input(payload.query, raise_on_block=True)
    return container.react_agent.run(guard_res.sanitized_text)


@router.post("/agent/workflow", summary="启动企业审批状态图工作流（支持 Human-in-the-loop 中断）")
def agent_workflow_start(payload: WorkflowStartRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    result = container.workflow.invoke(
        {"applicant": payload.applicant, "item": payload.item, "amount": payload.amount},
        thread_id=payload.thread_id,
    )
    container.db.record_audit(
        action="workflow.start",
        status=result["status"],
        detail=f"thread_id={result['thread_id']}, item={payload.item}, amount={payload.amount}",
    )
    return result


@router.post("/agent/workflow/{thread_id}/resume", summary="恢复人工审批中断的状态图工作流")
def agent_workflow_resume(
    thread_id: str,
    payload: WorkflowResumeRequest,
    request: Request,
) -> Dict[str, Any]:
    container = _get_container(request)
    result = container.workflow.resume(
        thread_id,
        {
            "approved": payload.approved,
            "reviewer": payload.reviewer,
            "comment": payload.comment,
        },
    )
    container.db.record_audit(
        action="workflow.resume",
        status=result["status"],
        detail=f"thread_id={thread_id}, approved={payload.approved}, reviewer={payload.reviewer}",
    )
    return result


@router.post("/agent/multi", summary="多 Agent 协作主管模式（研究/分析/撰写/审核）")
def agent_multi_endpoint(payload: MultiAgentRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    guard_res = container.guardrails.check_input(payload.task, raise_on_block=True)
    return container.multi_agent.run(guard_res.sanitized_text)


@router.post("/agent/sql", summary="Text-to-SQL 企业销售库安全只读分析")
def agent_sql_endpoint(payload: TextToSQLRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    result = container.sql_agent.query(payload.question, override_sql=payload.override_sql)
    container.db.record_audit(
        action="agent.sql",
        status="ok",
        detail=f"sql={result['sql']}, rows={result['row_count']}",
    )
    return result


# ==============================================================================
# 5. MCP 协议接口与微调准备接口
# ==============================================================================


@router.get("/mcp/tools", summary="获取 MCP 服务端已注册工具列表")
def mcp_list_tools(request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    return {
        "protocol_version": container.mcp_server.PROTOCOL_VERSION,
        "tools": container.mcp_server.list_tools(),
        "resources": container.mcp_server.list_resources(),
    }


@router.post("/mcp/rpc", summary="标准 JSON-RPC 2.0 MCP 协议调用入口")
def mcp_rpc_endpoint(payload: MCPRPCRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    return container.mcp_server.handle_rpc(payload.model_dump())


@router.post("/finetune/prepare", summary="微调数据集清洗、格式转换与 LLaMA-Factory 配置生成")
def finetune_prepare_endpoint(payload: FinetunePrepareRequest, request: Request) -> Dict[str, Any]:
    container = _get_container(request)
    return container.finetune.prepare(
        raw_samples=payload.samples,
        dataset_format=payload.dataset_format,
        base_model=payload.base_model,
        dataset_name=payload.dataset_name,
        lora_rank=payload.lora_rank,
        use_qlora_4bit=payload.use_qlora_4bit,
    )
