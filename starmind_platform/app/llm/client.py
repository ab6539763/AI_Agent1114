"""
统一大模型适配层模块（Unified LLM Adapter）。

架构设计：
1. `BaseLLM`：统一抽象接口，定义同步/异步对话 `chat`、流式输出 `stream_chat` 与 Function Calling 协议。
2. `OpenAICompatibleLLM`：基于 `httpx` 实现的生产级客户端，兼容 DeepSeek、通义千问 Qwen、
   OpenAI、Ollama、vLLM 等所有遵循 OpenAI Chat Completions 规范的推理后端；
   内置指数退避重试、超时映射（`LLMTimeoutError`）、SSE 流式解析与链路可观测性埋点。
3. `SmartLocalMockLLM`：面向无外网 API Key / CI 自动化测试 / 本地离线演示的智能本地推理引擎。
   它并非简单返回固定字符串，而是内置了：
   - 意图识别与企业场景多轮上下文记忆
   - Function Calling / ReAct 工具调用自动决策（计算器、天气、知识库检索、邮件、日程、审批）
   - RAG 上下文证据提炼与 `[文档名#片段ID]` 精准引用标注
   - 多 Agent 角色化推理（Researcher / Analyst / Writer / Reviewer）
   - Text-to-SQL 自然语言转 `enterprise_sales` 只读 SQL 生成器
   - 流式打字机逐片输出
"""

from __future__ import annotations

import asyncio
import json
import re
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Dict, List, Optional

import httpx

from starmind_platform.app.config import Settings, get_settings
from starmind_platform.app.core.exceptions import LLMInvocationError, LLMTimeoutError
from starmind_platform.app.core.logging_utils import get_logger
from starmind_platform.app.core.observability import get_observability
from starmind_platform.app.core.retry import compute_backoff_delay
from starmind_platform.app.core.token_counter import TokenCounter

logger = get_logger("starmind.llm")


@dataclass
class ToolCallRequest:
    """大模型返回的单个工具调用请求（对齐 OpenAI Function Calling 规范）。"""

    id: str
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": "function",
            "function": {
                "name": self.name,
                "arguments": json.dumps(self.arguments, ensure_ascii=False),
            },
        }


@dataclass
class LLMResponse:
    """统一大模型调用返回结构。"""

    content: str
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_cny: float = 0.0
    latency_ms: float = 0.0
    tool_calls: List[ToolCallRequest] = field(default_factory=list)
    finish_reason: str = "stop"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_cny": self.cost_cny,
            "latency_ms": self.latency_ms,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls],
            "finish_reason": self.finish_reason,
        }


class BaseLLM(ABC):
    """统一大模型抽象基类。"""

    def __init__(self, model: str, provider: str, temperature: float = 0.2, max_tokens: int = 2048) -> None:
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """执行一次同步对话补全调用。"""

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """执行流式对话补全，异步逐片产出文本增量（Delta）。"""


class OpenAICompatibleLLM(BaseLLM):
    """
    基于 httpx 的 OpenAI 协议兼容客户端。
    支持 DeepSeek / Qwen / OpenAI / Ollama / vLLM 等所有兼容 `/chat/completions` 的服务端。
    """

    def __init__(
        self,
        *,
        model: str,
        provider: str,
        api_key: str,
        base_url: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(model=model, provider=provider, temperature=temperature, max_tokens=max_tokens)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def _build_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        obs = get_observability()
        start = time.perf_counter()
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 2):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.post(url, headers=self._build_headers(), json=payload)

                if resp.status_code == 429 or resp.status_code >= 500:
                    raise LLMInvocationError(
                        f"上游大模型服务繁忙（HTTP {resp.status_code}）",
                        details={"status_code": resp.status_code, "body": resp.text[:300]},
                    )
                if resp.status_code >= 400:
                    raise LLMInvocationError(
                        f"大模型请求被拒绝（HTTP {resp.status_code}）: {resp.text[:200]}",
                        http_status=resp.status_code,
                    )

                data = resp.json()
                choice = data["choices"][0]
                message = choice.get("message", {})
                content = message.get("content") or ""
                finish_reason = choice.get("finish_reason") or "stop"

                parsed_tool_calls: List[ToolCallRequest] = []
                for tc in message.get("tool_calls") or []:
                    fn = tc.get("function", {})
                    raw_args = fn.get("arguments") or "{}"
                    try:
                        args_dict = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args)
                    except json.JSONDecodeError:
                        args_dict = {"raw": raw_args}
                    parsed_tool_calls.append(
                        ToolCallRequest(
                            id=tc.get("id") or f"call_{uuid.uuid4().hex[:8]}",
                            name=fn.get("name", ""),
                            arguments=args_dict,
                        )
                    )

                usage = data.get("usage") or {}
                prompt_tokens = int(usage.get("prompt_tokens") or TokenCounter.count_messages(messages))
                completion_tokens = int(usage.get("completion_tokens") or TokenCounter.count_text(content))
                cost = TokenCounter.estimate_cost(self.model, prompt_tokens, completion_tokens).total_cost_cny
                elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)

                obs.record_span(
                    name=f"llm.chat.{self.provider}",
                    category="llm",
                    latency_ms=elapsed_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    model=self.model,
                )
                return LLMResponse(
                    content=content,
                    model=self.model,
                    provider=self.provider,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    cost_cny=cost,
                    latency_ms=elapsed_ms,
                    tool_calls=parsed_tool_calls,
                    finish_reason=finish_reason,
                )
            except httpx.TimeoutException as exc:
                last_error = LLMTimeoutError(f"调用大模型 {self.provider}/{self.model} 超时（>{self.timeout_seconds}s）")
                if attempt > self.max_retries:
                    break
                time.sleep(compute_backoff_delay(attempt))
                logger.warning(f"大模型调用超时，准备第 {attempt} 次重试: {exc}")
            except LLMInvocationError as exc:
                last_error = exc
                if attempt > self.max_retries:
                    break
                time.sleep(compute_backoff_delay(attempt))
            except httpx.HTTPError as exc:
                last_error = LLMInvocationError(f"大模型网络通信异常: {exc}")
                if attempt > self.max_retries:
                    break
                time.sleep(compute_backoff_delay(attempt))

        obs.record_span(
            name=f"llm.chat.{self.provider}",
            category="llm",
            latency_ms=(time.perf_counter() - start) * 1000.0,
            status="error",
            model=self.model,
            metadata={"error": str(last_error)},
        )
        assert last_error is not None
        raise last_error

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if temperature is None else temperature,
            "max_tokens": self.max_tokens if max_tokens is None else max_tokens,
            "stream": True,
        }
        start = time.perf_counter()
        collected: List[str] = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                async with client.stream("POST", url, headers=self._build_headers(), json=payload) as resp:
                    if resp.status_code >= 400:
                        body = await resp.aread()
                        raise LLMInvocationError(
                            f"流式接口返回异常（HTTP {resp.status_code}）: {body.decode('utf-8', errors='ignore')[:200]}"
                        )
                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        raw = line[5:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw)
                            delta = chunk["choices"][0].get("delta", {}).get("content")
                            if delta:
                                collected.append(delta)
                                yield delta
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(f"流式调用大模型 {self.provider}/{self.model} 超时") from exc
        finally:
            full_text = "".join(collected)
            get_observability().record_span(
                name=f"llm.stream.{self.provider}",
                category="llm_stream",
                latency_ms=(time.perf_counter() - start) * 1000.0,
                prompt_tokens=TokenCounter.count_messages(messages),
                completion_tokens=TokenCounter.count_text(full_text),
                model=self.model,
            )


class SmartLocalMockLLM(BaseLLM):
    """
    智能本地模拟推理引擎（无外网 API Key 亦可 100% 流畅驱动所有企业级能力）。
    通过解析 System Prompt 任务指令、工具定义、RAG 检索片段与历史消息，生成贴近真实大模型的结构化回复。
    """

    def __init__(self, model: str = "deepseek-chat", temperature: float = 0.2, max_tokens: int = 2048) -> None:
        super().__init__(model=model, provider="local_mock", temperature=temperature, max_tokens=max_tokens)

    @staticmethod
    def _extract_system_and_user(messages: List[Dict[str, Any]]) -> tuple[str, str, List[Dict[str, Any]]]:
        system_parts: List[str] = []
        last_user = ""
        for msg in messages:
            role = msg.get("role", "")
            content = str(msg.get("content") or "")
            if role == "system":
                system_parts.append(content)
            elif role == "user":
                last_user = content
        return "\n".join(system_parts), last_user, messages

    def _decide_tool_calls(
        self,
        user_text: str,
        tools: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
    ) -> List[ToolCallRequest]:
        """根据用户意图与可用工具列表决定是否触发 Function Calling。"""
        # 如果刚刚已经执行过工具并返回了 tool 结果，则不再重复触发工具调用，转而总结回答
        if messages and messages[-1].get("role") == "tool":
            return []

        tool_names = {t.get("function", {}).get("name") for t in tools}
        calls: List[ToolCallRequest] = []

        # 1. 数学表达式计算
        expr_match = re.search(r"([0-9]+(?:\.[0-9]+)?\s*[\+\-\*/]\s*[0-9]+(?:\.[0-9]+)?(?:\s*[\+\-\*/]\s*[0-9]+(?:\.[0-9]+)?)*)", user_text)
        if "calculator" in tool_names and (expr_match or "计算" in user_text or "等于多少" in user_text):
            expr = expr_match.group(1) if expr_match else "128 * 36 + 512"
            calls.append(
                ToolCallRequest(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name="calculator",
                    arguments={"expression": expr.strip()},
                )
            )

        # 2. 天气查询
        if "get_weather" in tool_names and ("天气" in user_text or "气温" in user_text or "下雨" in user_text):
            city = "杭州"
            for candidate in ["杭州", "北京", "上海", "深圳", "广州", "成都", "苏州", "南京"]:
                if candidate in user_text:
                    city = candidate
                    break
            calls.append(
                ToolCallRequest(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name="get_weather",
                    arguments={"city": city},
                )
            )

        # 3. 邮件草拟
        if "draft_email" in tool_names and ("邮件" in user_text or "发信" in user_text):
            calls.append(
                ToolCallRequest(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name="draft_email",
                    arguments={
                        "recipient": "team@starmind.cn",
                        "subject": "项目进度与协同同步",
                        "body": f"您好，关于“{user_text[:40]}”的事项已整理完毕，请查收并确认后续排期。",
                    },
                )
            )

        # 4. 日程创建
        if "create_calendar_event" in tool_names and ("日程" in user_text or "会议" in user_text or "预约" in user_text):
            calls.append(
                ToolCallRequest(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name="create_calendar_event",
                    arguments={
                        "title": "星辰智脑项目评审会",
                        "start_time": "2026-11-20 14:00",
                        "participants": ["架构师", "产品经理", "研发负责人"],
                    },
                )
            )

        # 5. 审批单提交
        if "submit_approval" in tool_names and ("审批" in user_text or "报销" in user_text or "请假" in user_text or "采购" in user_text):
            amount_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:元|万|块)", user_text)
            amount = float(amount_match.group(1)) if amount_match else 3500.0
            if "万" in user_text and amount < 1000:
                amount *= 10000
            calls.append(
                ToolCallRequest(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name="submit_approval",
                    arguments={
                        "approval_type": "报销/采购审批" if ("报销" in user_text or "采购" in user_text) else "常规流程审批",
                        "applicant": "张工",
                        "amount": amount,
                        "reason": user_text[:80],
                    },
                )
            )

        # 6. 企业内部知识检索
        if not calls and "search_enterprise_kb" in tool_names and any(
            kw in user_text for kw in ["制度", "报销", "年假", "差旅", "星辰", "规范", "手册", "知识库", "政策", "上线"]
        ):
            calls.append(
                ToolCallRequest(
                    id=f"call_{uuid.uuid4().hex[:8]}",
                    name="search_enterprise_kb",
                    arguments={"query": user_text},
                )
            )

        return calls

    def _generate_sql(self, user_text: str) -> str:
        """针对 `enterprise_sales` 销售业绩表生成安全只读 SQL。"""
        q = user_text.lower()
        if "区域" in user_text or "地区" in user_text or "华东" in user_text or "华北" in user_text:
            return (
                "SELECT region AS 销售大区, COUNT(*) AS 订单数, "
                "ROUND(SUM(amount_cny), 2) AS 销售额_元, ROUND(AVG(amount_cny), 2) AS 客单价_元 "
                "FROM enterprise_sales GROUP BY region ORDER BY 销售额_元 DESC"
            )
        if "季度" in user_text or "quarter" in q or "趋势" in user_text:
            return (
                "SELECT quarter AS 季度, COUNT(*) AS 订单数, "
                "ROUND(SUM(amount_cny), 2) AS 销售额_元 "
                "FROM enterprise_sales GROUP BY quarter ORDER BY quarter ASC"
            )
        if "产品" in user_text or "套件" in user_text or "排行" in user_text or "top" in q:
            return (
                "SELECT product_name AS 产品名称, SUM(quantity) AS 销量, "
                "ROUND(SUM(amount_cny), 2) AS 销售额_元 "
                "FROM enterprise_sales GROUP BY product_name ORDER BY 销售额_元 DESC LIMIT 5"
            )
        if "客户" in user_text or "大客户" in user_text:
            return (
                "SELECT customer_name AS 客户名称, region AS 区域, product_name AS 采购产品, "
                "amount_cny AS 合同金额_元, quarter AS 签约季度 "
                "FROM enterprise_sales ORDER BY amount_cny DESC LIMIT 5"
            )
        return (
            "SELECT region AS 销售大区, product_name AS 产品名称, quarter AS 季度, "
            "ROUND(SUM(amount_cny), 2) AS 销售额_元 "
            "FROM enterprise_sales GROUP BY region, product_name, quarter "
            "ORDER BY 销售额_元 DESC LIMIT 10"
        )

    def _generate_rag_answer(self, user_text: str) -> str:
        """从 RAG Prompt 拼接的证据片段中提炼高置信度回答并保留 `[文档名#片段ID]` 溯源标注。"""
        citations = re.findall(r"\[([^\[\]]+#[^\[\]]+)\]", user_text)
        # 提取“参考资料”段落中的核心句子
        context_block = ""
        if "参考资料" in user_text:
            context_block = user_text.split("参考资料", 1)[1]
            if "用户问题" in context_block:
                context_block = context_block.split("用户问题", 1)[0]

        lines = [ln.strip() for ln in context_block.splitlines() if ln.strip() and not ln.strip().startswith("---")]
        # 挑选最具信息量的前 2~3 条参考证据
        evidence_lines = lines[:3] if lines else ["已检索到相关企业制度与技术规范片段。"]
        cite_str = "、".join(f"[{c}]" for c in dict.fromkeys(citations[:3])) if citations else "[企业知识库#0]"

        summary_bullets = "\n".join(f"- {ln[:160]}" for ln in evidence_lines)
        return (
            f"根据星辰智脑企业知识库检索结果，核心结论如下：\n\n"
            f"{summary_bullets}\n\n"
            f"以上结论均严格依据知识库原文整理，引用来源：{cite_str}。"
        )

    def _generate_multi_agent_reply(self, system_text: str, user_text: str) -> str:
        """针对多 Agent 协作中的 4 类专家角色生成专业结构化产出。"""
        if "ROLE:RESEARCHER" in system_text:
            return (
                f"【研究检索员调研摘要】\n"
                f"1. 调研主题：{user_text[:80]}\n"
                f"2. 行业与内部依据：结合杭州星辰数科企业知识库及国内大模型落地实践，"
                f"建议采用“混合检索 RAG + 安全护栏 + 可观测性监控”三位一体架构。\n"
                f"3. 关键事实点：私有化部署与 DeepSeek/Qwen 多模型路由可降低 45% 以上推理成本。"
            )
        if "ROLE:ANALYST" in system_text:
            return (
                f"【数据分析师量化洞察】\n"
                f"1. 投入产出评估：基于平台 Token 成本核算，常规问答单次成本控制在 0.002~0.015 元区间。\n"
                f"2. 性能与风险指标：P95 延迟目标 < 1800ms，RAG 忠实度 >= 0.85，高危审批操作需引入人工复核节点。\n"
                f"3. 优化建议：高频问答开启语义缓存，复杂任务拆分为多步工作流并做好持久化检查点。"
            )
        if "ROLE:WRITER" in system_text:
            return (
                f"【企业级执行方案报告】\n"
                f"一、背景与目标\n针对“{user_text[:60]}”业务诉求，本方案融合调研依据与量化分析结果。\n\n"
                f"二、核心落地路径\n"
                f"1. 知识底座：统一接入企业制度与业务文档，采用 BM25 + 向量 + RRF 混合检索确保可溯源。\n"
                f"2. 智能编排：通过 ReAct 工具链与状态图审批流打通办公协同与数据库只读查询。\n"
                f"3. 安全治理：全链路开启提示词注入拦截、PII 敏感信息脱敏与 Trace/Cost 监控。\n\n"
                f"三、预期收益\n预计提升内部知识检索与报表分析效率 3 倍以上，同时满足政企合规审计要求。"
            )
        if "ROLE:REVIEWER" in system_text:
            return (
                "【质量审核员评审意见】\n"
                "- 审核结论：通过（PASS）\n"
                "- 完整性评分：95/100（覆盖调研证据、量化指标、落地路径与合规要点）\n"
                "- 风险复核：未发现敏感信息明文泄露或越权操作建议，可直接交付业务团队执行。"
            )
        return ""

    def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        start = time.perf_counter()
        system_text, user_text, _ = self._extract_system_and_user(messages)

        tool_calls: List[ToolCallRequest] = []
        content = ""
        finish_reason = "stop"

        # 1. Text-to-SQL 专用模式
        if "TEXT_TO_SQL_MODE" in system_text:
            content = self._generate_sql(user_text)
        # 2. 多 Agent 协作角色模式
        elif "ROLE:" in system_text:
            content = self._generate_multi_agent_reply(system_text, user_text)
        # 3. RAG 溯源问答模式
        elif "RAG_ANSWER_MODE" in system_text:
            content = self._generate_rag_answer(user_text)
        # 4. 工具调用决策模式
        elif tools:
            tool_calls = self._decide_tool_calls(user_text, tools, messages)
            if tool_calls:
                finish_reason = "tool_calls"
                content = ""
            else:
                # 若刚刚拿到工具执行结果，则综合工具结果输出最终中文回答
                tool_outputs = [
                    str(m.get("content", "")) for m in messages if m.get("role") == "tool"
                ]
                if tool_outputs:
                    joined = "；".join(tool_outputs[-3:])
                    content = f"已为您调用企业工具完成处理，核心结果如下：{joined}。如需进一步操作请随时告知。"
                else:
                    content = f"已收到您的请求“{user_text[:80]}”，无需调用外部工具，已直接为您整理建议方案。"
        # 5. 常规企业多轮对话模式
        else:
            history_turns = sum(1 for m in messages if m.get("role") == "user")
            if "我是" in user_text or "记住" in user_text:
                content = f"好的，我已记住您提供的信息（当前第 {history_turns} 轮对话）。在本次会话中我会持续结合上下文为您提供精准服务。"
            elif "我叫什么" in user_text or "刚才" in user_text or "上一轮" in user_text:
                prev_users = [str(m.get("content", "")) for m in messages[:-1] if m.get("role") == "user"]
                prev_hint = prev_users[-1] if prev_users else "暂无更早历史"
                content = f"结合本会话历史上下文，您之前提到过：“{prev_hint}”。如需我基于该背景继续推进，请直接说明目标。"
            else:
                content = (
                    f"【星辰智脑 StarMind】已收到您的问题（第 {history_turns} 轮）：“{user_text[:100]}”。\n"
                    f"建议结合平台内置的企业知识库 RAG 检索、ReAct 工具协同或 Text-to-SQL 数据分析模块联动处理，"
                    f"当前运行于 `local_mock` 零门槛本地智能引擎，切换 DeepSeek/Qwen API Key 即可无缝升级云端大模型。"
                )

        prompt_tokens = TokenCounter.count_messages(messages)
        completion_tokens = TokenCounter.count_text(content) if content else 16
        cost = TokenCounter.estimate_cost(self.model, prompt_tokens, completion_tokens).total_cost_cny
        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)

        get_observability().record_span(
            name="llm.chat.local_mock",
            category="llm",
            latency_ms=elapsed_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=self.model,
        )

        return LLMResponse(
            content=content,
            model=self.model,
            provider=self.provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_cny=cost,
            latency_ms=elapsed_ms,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
        )

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """将本地智能引擎响应按 4~8 字符切分为流式打字机片段异步产出。"""
        resp = self.chat(messages, temperature=temperature, max_tokens=max_tokens)
        text = resp.content
        chunk_size = 6
        for idx in range(0, len(text), chunk_size):
            yield text[idx : idx + chunk_size]
            await asyncio.sleep(0.005)


def create_llm_client(settings: Optional[Settings] = None) -> BaseLLM:
    """
    大模型客户端工厂方法。
    - 当 `llm_provider == "local_mock"` 或外部云厂商未配置 API Key 时，安全回退至 `SmartLocalMockLLM`；
    - 当配置了 `ollama` / `vllm` 或带 API Key 的 `deepseek` / `qwen` / `openai` 时，返回 `OpenAICompatibleLLM`。
    """
    cfg = settings or get_settings()
    provider = cfg.llm_provider

    if provider == "local_mock":
        return SmartLocalMockLLM(
            model=cfg.llm_model,
            temperature=cfg.llm_temperature,
            max_tokens=cfg.llm_max_tokens,
        )

    # 云端模型若未配置 Key，自动降级为 local_mock 并打印清晰告警，保证开箱即用
    if provider in {"deepseek", "qwen", "openai"} and not cfg.llm_api_key.strip():
        logger.warning(
            f"检测到 provider={provider} 但未配置 STARMIND_LLM_API_KEY，自动降级为 SmartLocalMockLLM 保障可用性。"
        )
        return SmartLocalMockLLM(
            model=cfg.llm_model,
            temperature=cfg.llm_temperature,
            max_tokens=cfg.llm_max_tokens,
        )

    return OpenAICompatibleLLM(
        model=cfg.llm_model,
        provider=provider,
        api_key=cfg.llm_api_key,
        base_url=cfg.resolve_base_url(),
        temperature=cfg.llm_temperature,
        max_tokens=cfg.llm_max_tokens,
        timeout_seconds=cfg.llm_timeout_seconds,
        max_retries=cfg.llm_max_retries,
    )
