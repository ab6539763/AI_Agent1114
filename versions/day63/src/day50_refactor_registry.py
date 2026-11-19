"""Day 50 - 步骤二：代码评审重构实战——插件化专家注册表与责任链中间件中台内核。"""

from __future__ import annotations

import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Set

PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)")
INJECTION_RE = re.compile(r"(忽略.{0,6}(指令|规则)|system\s*prompt)", re.IGNORECASE)


@dataclass
class AgentRequestContext:
    query: str
    user_id: str
    role: str
    trace_id: str = field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:8]}")
    matched_specialist: str = ""
    status: str = "PENDING"
    reply: str = ""
    execution_order: List[str] = field(default_factory=list)
    latency_ms: float = 0.0


@dataclass
class SpecialistPlugin:
    name: str
    allowed_roles: Set[str]
    matcher: Callable[[str], bool]
    handler: Callable[[AgentRequestContext], str]


MiddlewareFunc = Callable[[AgentRequestContext, Callable[[AgentRequestContext], AgentRequestContext]], AgentRequestContext]


class SpecialistRegistry:
    """插件化专家注册表：支持按开闭原则（OCP）动态注册新领域专家。"""

    def __init__(self) -> None:
        self._plugins: List[SpecialistPlugin] = []

    def register(self, plugin: SpecialistPlugin) -> "SpecialistRegistry":
        self._plugins.append(plugin)
        return self

    def resolve(self, query: str) -> SpecialistPlugin:
        for plugin in self._plugins:
            if plugin.matcher(query):
                return plugin
        raise LookupError(f"未匹配到可处理该请求的专家插件: {query}")


class AgentMiddlewarePipeline:
    """洋葱模型责任链管道：依次串联中间件并最终分发到 SpecialistRegistry。"""

    def __init__(self, registry: SpecialistRegistry, middlewares: List[MiddlewareFunc]) -> None:
        self.registry = registry
        self.middlewares = middlewares

    def execute(self, ctx: AgentRequestContext) -> AgentRequestContext:
        def core_dispatch(c: AgentRequestContext) -> AgentRequestContext:
            c.execution_order.append("dispatch")
            plugin = self.registry.resolve(c.query)
            c.matched_specialist = plugin.name
            c.reply = plugin.handler(c)
            c.status = "COMPLETED"
            return c

        chain: Callable[[AgentRequestContext], AgentRequestContext] = core_dispatch
        for mw in reversed(self.middlewares):
            prev_next = chain

            def _wrap(
                current_mw: MiddlewareFunc = mw,
                next_fn: Callable[[AgentRequestContext], AgentRequestContext] = prev_next,
            ) -> Callable[[AgentRequestContext], AgentRequestContext]:
                return lambda c: current_mw(c, next_fn)

            chain = _wrap()

        return chain(ctx)


def trace_middleware(ctx: AgentRequestContext, nxt: Callable[[AgentRequestContext], AgentRequestContext]) -> AgentRequestContext:
    t0 = time.perf_counter()
    ctx.execution_order.append("trace:enter")
    out = nxt(ctx)
    out.latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
    out.execution_order.append("trace:exit")
    return out


def guardrail_middleware(ctx: AgentRequestContext, nxt: Callable[[AgentRequestContext], AgentRequestContext]) -> AgentRequestContext:
    ctx.execution_order.append("guardrail:in")
    if INJECTION_RE.search(ctx.query):
        ctx.status = "BLOCKED"
        ctx.reply = "安全护栏拦截：疑似 Prompt 注入指令。"
        return ctx
    out = nxt(ctx)
    out.execution_order.append("guardrail:out")
    out.reply = PHONE_RE.sub(r"\1****\2", out.reply)
    return out


def make_rbac_middleware(registry: SpecialistRegistry) -> MiddlewareFunc:
    def rbac_middleware(ctx: AgentRequestContext, nxt: Callable[[AgentRequestContext], AgentRequestContext]) -> AgentRequestContext:
        ctx.execution_order.append("rbac")
        plugin = registry.resolve(ctx.query)
        if ctx.role not in plugin.allowed_roles:
            ctx.matched_specialist = plugin.name
            ctx.status = "FORBIDDEN"
            ctx.reply = f"权限不足：角色 '{ctx.role}' 无权访问专家 '{plugin.name}'。"
            return ctx
        return nxt(ctx)

    return rbac_middleware


def build_refactored_office_platform() -> AgentMiddlewarePipeline:
    registry = SpecialistRegistry()
    # 热插拔注册 3 个专家（包含新扩展的 text2sql 财务数据专家，无需改动主干代码！）
    registry.register(
        SpecialistPlugin(
            name="text2sql_finance_agent",
            allowed_roles={"director", "analyst"},
            matcher=lambda q: "销售额" in q or "SQL" in q.upper(),
            handler=lambda _c: "华东区 Q3 有效销售额 270000 元，负责人电话 13911112222。",
        )
    )
    registry.register(
        SpecialistPlugin(
            name="knowledge_agent",
            allowed_roles={"intern", "employee", "analyst", "director"},
            matcher=lambda _q: True,
            handler=lambda _c: "一线城市住宿标准 600 元/晚。",
        )
    )
    return AgentMiddlewarePipeline(
        registry=registry,
        middlewares=[trace_middleware, guardrail_middleware, make_rbac_middleware(registry)],
    )


if __name__ == "__main__":
    platform = build_refactored_office_platform()
    r_ok = platform.execute(AgentRequestContext(query="查一下华东区销售额", user_id="u1", role="analyst"))
    print("合法分析师查询:", r_ok.status, "| 回复:", r_ok.reply, "| 链路:", r_ok.execution_order)
    r_deny = platform.execute(AgentRequestContext(query="查一下华东区销售额", user_id="u2", role="intern"))
    print("实习生越权查询:", r_deny.status, "| 回复:", r_deny.reply)

