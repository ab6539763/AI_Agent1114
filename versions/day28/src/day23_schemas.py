"""
StarMind Day 23 - 步骤一：基于 Pydantic v2 的企业级 API 请求与响应数据模型
采用 ConfigDict、Field 与 @field_validator 现代规范。
"""

from typing import List, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_MODELS = ("deepseek-chat", "qwen-max", "glm-4-plus")


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str = "starmind-api"
    version: str = "0.23.0"


class ModelInfo(BaseModel):
    model_id: str
    provider: str
    context_window: int
    supports_tools: bool = True


class ChatRequest(BaseModel):
    """AI 对话请求体（严格强类型与业务规则校验）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str = Field(..., min_length=2, max_length=64, description="会话唯一标识")
    message: str = Field(..., min_length=1, max_length=4000, description="用户输入文本")
    model: str = Field(default="deepseek-chat", description="目标大模型 ID")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="采样温度 [0.0, 2.0]")
    max_tokens: int = Field(default=512, ge=16, le=8192, description="最大生成长度")

    @field_validator("model")
    @classmethod
    def validate_model_id(cls, value: str) -> str:
        if value not in SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型 '{value}'，可选列表: {list(SUPPORTED_MODELS)}")
        return value


class MessageRecord(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatResponse(BaseModel):
    """AI 对话标准响应体。"""

    session_id: str
    model: str
    reply: str
    turn_count: int
    estimated_tokens: int


class SessionDetailResponse(BaseModel):
    """会话详情与历史记录响应体。"""

    session_id: str
    message_count: int
    messages: List[MessageRecord]


if __name__ == "__main__":
    req = ChatRequest(session_id="s_001", message="  杭州出差住宿报销上限是多少？  ")
    print("校验通过的请求模型:", req.model_dump())

