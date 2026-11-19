"""
统一业务异常体系模块。

工程规范：
1. 所有平台内部可预期异常均继承自 `StarMindError`，并携带标准错误码（`error_code`）、
   面向用户的中文提示（`message`）、HTTP 状态码（`http_status`）与可选扩展详情（`details`）。
2. FastAPI 全局异常处理器可据此统一返回结构化 JSON 响应，避免将内部堆栈直接暴露给前端。
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class StarMindError(Exception):
    """星辰智脑平台基础业务异常类。"""

    error_code: str = "STARMIND_INTERNAL_ERROR"
    http_status: int = 500

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        http_status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        if http_status is not None:
            self.http_status = http_status
        self.details: Dict[str, Any] = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """转换为标准 API 错误响应载荷。"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class LLMInvocationError(StarMindError):
    """大模型调用通用异常（如上游 5xx、鉴权失败、响应体解析异常）。"""

    error_code = "LLM_INVOCATION_ERROR"
    http_status = 502


class LLMTimeoutError(LLMInvocationError):
    """大模型推理请求超时异常。"""

    error_code = "LLM_TIMEOUT_ERROR"
    http_status = 504


class GuardrailBlockedError(StarMindError):
    """安全护栏拦截异常（提示词注入、违规敏感内容等触发熔断）。"""

    error_code = "GUARDRAIL_BLOCKED"
    http_status = 400


class RAGRetrievalError(StarMindError):
    """知识库入库或检索阶段异常（如不支持的文档格式、索引读写失败）。"""

    error_code = "RAG_RETRIEVAL_ERROR"
    http_status = 500


class ToolExecutionError(StarMindError):
    """Agent 工具调用执行失败异常（如参数校验不通过、外部工具报错）。"""

    error_code = "TOOL_EXECUTION_ERROR"
    http_status = 500


class SQLSafetyError(StarMindError):
    """Text-to-SQL 安全校验异常（检测到写操作、多语句或高危 SQL 注入）。"""

    error_code = "SQL_SAFETY_VIOLATION"
    http_status = 400


class WorkflowStateError(StarMindError):
    """状态图工作流执行或恢复异常（如 thread_id 不存在、节点未注册）。"""

    error_code = "WORKFLOW_STATE_ERROR"
    http_status = 400
