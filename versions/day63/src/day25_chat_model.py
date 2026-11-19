"""
Day 25 - 步骤一：LangChain 风格消息协议与 BaseChatModel 统一接口实现
对应生产包：langchain_core.messages / langchain_core.language_models.chat_models
"""

from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Union


@dataclass
class BaseMessage:
    """统一对话消息基类，对应 langchain_core.messages.BaseMessage。"""

    content: str
    role: str
    additional_kwargs: Dict[str, Any] = field(default_factory=dict)

    def to_openai_dict(self) -> Dict[str, str]:
        """转换为国内主流模型网关（DeepSeek/通义千问/vLLM）通用的 OpenAI 消息字典。"""
        return {"role": self.role, "content": self.content}


@dataclass
class SystemMessage(BaseMessage):
    """系统指令消息：用于设定角色边界、输出格式与安全红线。"""

    role: str = field(default="system", init=False)


@dataclass
class HumanMessage(BaseMessage):
    """用户输入消息：承载终端用户的真实提问。"""

    role: str = field(default="user", init=False)


@dataclass
class AIMessage(BaseMessage):
    """模型回复消息：除正文外，额外携带 Token 统计与耗时等可观测元数据。"""

    role: str = field(default="assistant", init=False)
    response_metadata: Dict[str, Any] = field(default_factory=dict)
    usage_metadata: Dict[str, int] = field(default_factory=dict)


MessageInput = Union[str, Sequence[BaseMessage]]


class BaseChatModel(ABC):
    """
    对话模型统一抽象基类（模板方法模式）。
    子类只需实现 `_generate`，即可自动获得输入标准化、耗时统计与 Token 计量能力。
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
        base_url: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url or "local://starmind-offline"

    @staticmethod
    def _normalize_input(input_data: MessageInput) -> List[BaseMessage]:
        """兼容直接传 str 或传 List[BaseMessage]，与 LangChain invoke 行为对齐。"""
        if isinstance(input_data, str):
            return [HumanMessage(content=input_data)]
        if not input_data:
            raise ValueError("消息列表不能为空")
        return list(input_data)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        轻量级中英文 Token 估算器（离线环境免 tiktoken 依赖）：
        中文约 1 字 ~ 1.3 token，英文/数字约 4 字符 ~ 1 token。
        """
        zh_chars = sum(1 for ch in text if "\\u4e00" <= ch <= "\\u9fff")
        other_chars = len(text) - zh_chars
        return max(1, int(zh_chars * 1.3 + other_chars / 4))

    @abstractmethod
    def _generate(self, messages: List[BaseMessage]) -> str:
        """子类实现具体的模型推理或 HTTP 调用逻辑。"""

    def invoke(self, input_data: MessageInput) -> AIMessage:
        """统一同步调用入口，自动封装 AIMessage 与可观测元数据。"""
        messages = self._normalize_input(input_data)
        start = time.perf_counter()
        reply_text = self._generate(messages)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        prompt_tokens = sum(self._estimate_tokens(m.content) for m in messages)
        completion_tokens = self._estimate_tokens(reply_text)

        return AIMessage(
            content=reply_text,
            response_metadata={
                "request_id": f"req_{uuid.uuid4().hex[:8]}",
                "model_name": self.model_name,
                "base_url": self.base_url,
                "temperature": self.temperature,
                "latency_ms": latency_ms,
            },
            usage_metadata={
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        )


class StarMindChatModel(BaseChatModel):
    """
    星辰智脑本地可运行 ChatModel 实现：
    - 默认使用确定性规则引擎模拟企业大模型回复，保障离线教学与 CI 单测 100% 稳定。
    - 支持传入自定义 `handler` 回调，方便按需对接 DeepSeek / Qwen / vLLM 真实 HTTP 接口。
    """

    def __init__(
        self,
        model_name: str = "starmind-qwen2.5-72b",
        temperature: float = 0.1,
        max_tokens: int = 1024,
        base_url: Optional[str] = None,
        handler: Optional[Callable[[List[BaseMessage]], str]] = None,
    ) -> None:
        super().__init__(model_name, temperature, max_tokens, base_url)
        self._handler = handler

    def _generate(self, messages: List[BaseMessage]) -> str:
        if self._handler is not None:
            return self._handler(messages)

        system_text = " ".join(m.content for m in messages if m.role == "system")
        user_text = messages[-1].content

        # 场景 1：IT 工单分类路由
        if "分类" in system_text or "工单" in system_text:
            if any(k in user_text for k in ("VPN", "内网", "WiFi", "断网", "GitLab")):
                return "【工单分类】网络与权限类 | 【优先级】P1 | 【建议】请先检查零信任客户端证书是否过期，并重置星辰VPN令牌。"
            if any(k in user_text for k in ("蓝屏", "屏幕", "键盘", "笔记本", "显卡")):
                return "【工单分类】硬件设备类 | 【优先级】P2 | 【建议】请携带资产编号前往B座3楼IT运维台检测。"
            if any(k in user_text for k in ("密码", "登录", "账号", "SSO", "权限")):
                return "【工单分类】账号安全类 | 【优先级】P1 | 【建议】请通过企业微信「星辰SSO自助重置」找回密码。"
            return "【工单分类】软件与综合支持 | 【优先级】P3 | 【建议】已转交桌面支持工程师跟进。"

        # 场景 2：通用企业助手兜底响应
        return f"[{self.model_name}] 已收到您的请求：「{user_text[:60]}」。我们将严格按照星辰数科规范为您处理。"


if __name__ == "__main__":
    llm = StarMindChatModel(model_name="deepseek-chat-compat", temperature=0.1)
    msgs = [
        SystemMessage(content="你是杭州星辰数科的IT服务台专家，负责对员工工单进行分类并给出首响建议。"),
        HumanMessage(content="老陈，我今天早上VPN死活连不上内网GitLab，急着提MR！"),
    ]
    response = llm.invoke(msgs)
    print("模型回复:", response.content)
    print("Token 统计:", response.usage_metadata)
    print("元数据:", response.response_metadata)

