"""
STARMIND-012 模块一：OpenAI 兼容协议 HTTP 大模型客户端（支持本地 Mock 降级）。
兼容 DeepSeek / 通义千问 DashScope / 智谱等 /v1/chat/completions 接口。
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


class LLMAPIError(RuntimeError):
    """大模型 HTTP 接口调用异常基类，携带 HTTP 状态码便于上层区分处理。"""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class LLMRequestConfig:
    """大模型 API 连接配置。"""

    base_url: str = "https://api.deepseek.com/v1"
    api_key: str = ""
    model: str = "deepseek-chat"
    timeout: float = 15.0
    temperature: float = 0.7


@dataclass
class LLMResponse:
    """标准化大模型响应对象。"""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    source: str  # "remote" 或 "mock"


def build_chat_payload(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """构造标准 OpenAI 兼容 /chat/completions 请求体。"""
    if not messages:
        raise ValueError("messages 不能为空")
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }


def parse_chat_response(
    raw_data: Dict[str, Any],
    latency_ms: float,
    source: str = "remote",
) -> LLMResponse:
    """解析 OpenAI 兼容响应 JSON 为强类型 LLMResponse。"""
    choices = raw_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("接口返回格式异常：缺少有效的 choices 字段")

    first_message = choices[0].get("message", {})
    content = first_message.get("content")
    if not isinstance(content, str):
        raise ValueError("接口返回格式异常：缺少 message.content 文本")

    usage = raw_data.get("usage", {})
    prompt_tokens = int(usage.get("prompt_tokens", 0))
    completion_tokens = int(usage.get("completion_tokens", 0))
    total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens))

    return LLMResponse(
        content=content.strip(),
        model=str(raw_data.get("model", "unknown")),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=round(latency_ms, 2),
        source=source,
    )


class StarMindHTTPClient:
    """星辰智脑 OpenAI 兼容 HTTP 客户端（支持无 Key 本地 Mock 降级）。"""

    def __init__(
        self,
        config: Optional[LLMRequestConfig] = None,
        mock_mode: bool = False,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.config = config or LLMRequestConfig()
        # 如果显式开启 mock_mode 或者未配置 api_key，自动启用本地 Mock 模式
        self.mock_mode = mock_mode or (not self.config.api_key.strip())
        self._transport = transport

    def _mock_chat_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """离线本地 Mock 引擎：返回与真实 OpenAI 协议 100% 同构的 JSON 报文。"""
        messages = payload["messages"]
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )

        # 针对星辰数科常见演示问题给出贴近业务的回答
        if "报销" in last_user:
            reply = "【本地Mock】星辰数科差旅报销请在钉钉发起「费用报销单」，500元以上需直属主管+财务双审批。"
        elif "DeepSeek" in last_user or "兼容" in last_user or "通义" in last_user:
            reply = "【本地Mock】DeepSeek 与通义千问均兼容 OpenAI /v1/chat/completions 协议，切换厂商只需修改 base_url 与 model。"
        elif "年假" in last_user:
            reply = "【本地Mock】入职满 1 年享 5 天带薪年假，系统按自然年每年 1 月 1 日自动发放。"
        else:
            reply = f"【本地Mock】已收到你的提问：「{last_user}」。当前未配置线上 API Key，已自动降级为离线模拟回复。"

        prompt_tokens = sum(len(m.get("content", "")) for m in messages)
        completion_tokens = len(reply)
        return {
            "id": "chatcmpl-starmind-mock-001",
            "object": "chat.completion",
            "model": f"{payload['model']}-mock",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": reply},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }

    def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """发送对话请求并返回标准化 LLMResponse。"""
        payload = build_chat_payload(
            messages=messages,
            model=self.config.model,
            temperature=self.config.temperature,
        )
        start = time.perf_counter()

        if self.mock_mode:
            raw_data = self._mock_chat_completion(payload)
            elapsed_ms = (time.perf_counter() - start) * 1000
            return parse_chat_response(raw_data, latency_ms=elapsed_ms, source="mock")

        endpoint = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(
                timeout=self.config.timeout,
                transport=self._transport,
            ) as client:
                resp = client.post(endpoint, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise LLMAPIError(f"请求大模型超时（>{self.config.timeout}s）") from exc
        except httpx.HTTPError as exc:
            raise LLMAPIError(f"网络请求失败：{exc}") from exc

        if resp.status_code == 401:
            raise LLMAPIError("API Key 无效或已过期（HTTP 401）", status_code=401)
        if resp.status_code == 429:
            raise LLMAPIError("触发接口频率限制或余额不足（HTTP 429）", status_code=429)
        if resp.status_code >= 500:
            raise LLMAPIError(
                f"大模型服务端暂时不可用（HTTP {resp.status_code}）",
                status_code=resp.status_code,
            )
        if resp.status_code != 200:
            raise LLMAPIError(
                f"接口返回异常状态码 HTTP {resp.status_code}: {resp.text[:120]}",
                status_code=resp.status_code,
            )

        elapsed_ms = (time.perf_counter() - start) * 1000
        return parse_chat_response(resp.json(), latency_ms=elapsed_ms, source="remote")


if __name__ == "__main__":
    # 默认不传 api_key，自动触发本地 Mock 降级模式
    client = StarMindHTTPClient(LLMRequestConfig(model="deepseek-chat"))
    result = client.chat([
        {"role": "system", "content": "你是杭州星辰数科企业知识助手。"},
        {"role": "user", "content": "星辰数科差旅报销怎么走流程？"},
    ])
    print(f"[{result.source}] 模型: {result.model} | 耗时: {result.latency_ms}ms | Tokens: {result.total_tokens}")
    print(f"回复: {result.content}")

