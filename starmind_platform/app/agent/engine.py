"""
星辰智脑企业级 Agent 编排引擎模块。

本模块集成六大企业级核心编排范式：
1. `ToolRegistry` & `@register_tool`：标准化工具注册中心与安全执行器，自动导出 OpenAI Function Calling Schema。
   内置 6 个企业办公工具：计算器、天气查询、企业内部知识检索、邮件草拟、日程创建、审批单提交。
2. `ReActAgent`：标准 Thought -> Action -> Observation 推理执行闭环，内置 `max_steps` 防死循环熔断。
3. `StateGraph`（类 LangGraph 状态图引擎）：支持 State 合并、普通边/条件边路由、`MemoryCheckpointer` /
   `SQLiteCheckpointer` 状态持久化，以及 Human-in-the-loop 人工审批中断（`interrupt`）与断点恢复（`resume`）。
4. `MultiAgentSupervisor`：主管编排式多 Agent 协作流水线（Researcher 研究检索员 -> Analyst 数据分析师
   -> Writer 报告撰写员 -> Reviewer 质量审核员）。
5. `TextToSQLAgent`：对接真实 SQLite 销售业绩库，执行严格只读 SQL 安全校验（禁止 DROP/DELETE/UPDATE/
   INSERT/ALTER/PRAGMA 及多语句注入），返回结构化表格与业务解读。
6. `MCPServer` & `MCPClient`：基于标准 JSON-RPC 2.0 协议的 Model Context Protocol 服务端与客户端实现
   （完整支持 `initialize`、`tools/list`、`tools/call`、`resources/list`、`resources/read`）。
"""

from __future__ import annotations

import ast
import json
import operator
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from starmind_platform.app.core.exceptions import SQLSafetyError, ToolExecutionError, WorkflowStateError
from starmind_platform.app.core.logging_utils import get_logger
from starmind_platform.app.core.observability import get_observability
from starmind_platform.app.db.database import DatabaseManager, get_db_manager
from starmind_platform.app.llm.client import BaseLLM, create_llm_client
from starmind_platform.app.rag.engine import RAGPipeline

logger = get_logger("starmind.agent")

# 状态图终止节点哨兵常量
END = "__END__"


# ==============================================================================
# 1. 安全数学表达式求值与 ToolRegistry 工具注册中心
# ==============================================================================

_SAFE_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_SAFE_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval_math(expression: str) -> float:
    """基于 Python AST 的安全算术表达式求值，杜绝 `eval()` 任意代码执行漏洞。"""
    try:
        node = ast.parse(expression.strip(), mode="eval").body
    except SyntaxError as exc:
        raise ToolExecutionError(f"数学表达式语法不合法: {expression}") from exc

    def _eval(n: ast.AST) -> float:
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.UnaryOp) and type(n.op) in _SAFE_UNARY_OPS:
            return _SAFE_UNARY_OPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in _SAFE_BIN_OPS:
            right = _eval(n.right)
            if isinstance(n.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
                raise ToolExecutionError("数学计算异常：除数不能为 0")
            if isinstance(n.op, ast.Pow) and abs(right) > 100:
                raise ToolExecutionError("数学计算异常：指数过大，拒绝计算")
            return _SAFE_BIN_OPS[type(n.op)](_eval(n.left), right)
        raise ToolExecutionError(f"表达式包含不允许的语法节点: {type(n).__name__}")

    return round(_eval(node), 6)


@dataclass
class ToolDefinition:
    """单个企业工具的元数据与可执行函数封装。"""

    name: str
    description: str
    parameters: Dict[str, Any]
    func: Callable[..., Any]

    def to_openai_schema(self) -> Dict[str, Any]:
        """导出 OpenAI Function Calling 标准工具定义。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_mcp_schema(self) -> Dict[str, Any]:
        """导出 MCP `tools/list` 规范工具定义。"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters,
        }


class ToolRegistry:
    """企业级 Agent 工具注册中心。"""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        *,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        func: Callable[..., Any],
    ) -> ToolDefinition:
        tool_def = ToolDefinition(name=name, description=description, parameters=parameters, func=func)
        self._tools[name] = tool_def
        return tool_def

    def decorator(
        self,
        *,
        name: str,
        description: str,
        parameters: Dict[str, Any],
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """装饰器形式注册工具函数。"""

        def _wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.register(name=name, description=description, parameters=parameters, func=fn)
            return fn

        return _wrap

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolExecutionError(f"未找到名为 `{name}` 的已注册工具")
        start = time.perf_counter()
        try:
            result = tool.func(**arguments)
            get_observability().record_span(
                name=f"tool.{name}",
                category="tool",
                latency_ms=(time.perf_counter() - start) * 1000.0,
                metadata={"arguments": arguments},
            )
            return result
        except ToolExecutionError:
            raise
        except Exception as exc:
            get_observability().record_span(
                name=f"tool.{name}",
                category="tool",
                latency_ms=(time.perf_counter() - start) * 1000.0,
                status="error",
                metadata={"error": str(exc)},
            )
            raise ToolExecutionError(f"工具 `{name}` 执行失败: {exc}") from exc


# 全局默认注册表与快捷装饰器
GLOBAL_TOOL_REGISTRY = ToolRegistry()


def register_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
    registry: Optional[ToolRegistry] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    通用 `@register_tool` 装饰器。
    支持注册到指定 `ToolRegistry` 实例或默认 `GLOBAL_TOOL_REGISTRY`。
    """
    target = registry if registry is not None else GLOBAL_TOOL_REGISTRY
    return target.decorator(name=name, description=description, parameters=parameters)


def build_default_tool_registry(rag_pipeline: Optional[RAGPipeline] = None) -> ToolRegistry:
    """构建并注册星辰智脑内置的 6 大企业级办公与计算工具。"""
    registry = ToolRegistry()

    @register_tool(
        name="calculator",
        description="安全执行四则运算与幂运算（支持括号与小数），适用于财务核算与指标计算。",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "算术表达式，例如 '(1280 + 320) * 1.13'"}
            },
            "required": ["expression"],
        },
        registry=registry,
    )
    def calculator(expression: str) -> Dict[str, Any]:
        value = _safe_eval_math(expression)
        return {"expression": expression, "result": value}

    @register_tool(
        name="get_weather",
        description="查询国内主要城市实时天气与穿衣/出行建议。",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "城市名称，例如 杭州、北京、上海"}},
            "required": ["city"],
        },
        registry=registry,
    )
    def get_weather(city: str) -> Dict[str, Any]:
        weather_db = {
            "杭州": {"weather": "多云转晴", "temp_c": 19, "humidity": "58%", "advice": "体感舒适，适合外出洽谈"},
            "北京": {"weather": "晴间多云", "temp_c": 11, "humidity": "35%", "advice": "昼夜温差较大，建议备外套"},
            "上海": {"weather": "阴有微风", "temp_c": 18, "humidity": "65%", "advice": "微风凉爽，出行便利"},
            "深圳": {"weather": "晴", "temp_c": 26, "humidity": "62%", "advice": "温暖晴朗，注意防晒"},
            "成都": {"weather": "小雨", "temp_c": 16, "humidity": "78%", "advice": "建议携带雨具"},
        }
        info = weather_db.get(
            city,
            {"weather": "晴转多云", "temp_c": 20, "humidity": "55%", "advice": "气候适宜，祝您工作顺利"},
        )
        return {"city": city, **info}

    @register_tool(
        name="search_enterprise_kb",
        description="检索杭州星辰数科企业内部知识库（含差旅报销、年假制度、研发上线规范、数据安全规范等）。",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "检索关键词或问题"},
                "top_k": {"type": "integer", "description": "返回片段数量", "default": 3},
            },
            "required": ["query"],
        },
        registry=registry,
    )
    def search_enterprise_kb(query: str, top_k: int = 3) -> Dict[str, Any]:
        if rag_pipeline is None:
            return {"query": query, "hits": [], "summary": "知识库引擎暂未挂载。"}
        res = rag_pipeline.query(query, top_k=top_k)
        return {
            "query": query,
            "answer": res["answer"],
            "confidence": res["confidence"],
            "citations": res["citations"],
        }

    @register_tool(
        name="draft_email",
        description="根据收件人、主题与正文要点生成规范的企业商务邮件草稿。",
        parameters={
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "收件人邮箱"},
                "subject": {"type": "string", "description": "邮件主题"},
                "body": {"type": "string", "description": "正文核心内容"},
            },
            "required": ["recipient", "subject", "body"],
        },
        registry=registry,
    )
    def draft_email(recipient: str, subject: str, body: str) -> Dict[str, Any]:
        draft_id = f"MAIL-{uuid.uuid4().hex[:8].upper()}"
        return {
            "draft_id": draft_id,
            "status": "draft_saved",
            "to": recipient,
            "subject": subject,
            "preview": f"【邮件草稿 {draft_id}】收件人：{recipient} | 主题：{subject}\n正文：{body}",
        }

    @register_tool(
        name="create_calendar_event",
        description="在企业日历中创建会议日程并生成会议室编号。",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "会议主题"},
                "start_time": {"type": "string", "description": "开始时间，例如 2026-11-20 14:00"},
                "participants": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "参会人列表",
                },
            },
            "required": ["title", "start_time"],
        },
        registry=registry,
    )
    def create_calendar_event(
        title: str,
        start_time: str,
        participants: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        event_id = f"CAL-{uuid.uuid4().hex[:8].upper()}"
        return {
            "event_id": event_id,
            "title": title,
            "start_time": start_time,
            "participants": participants or ["项目组成员"],
            "meeting_room": "西湖园区 A座 802 会议室",
            "status": "scheduled",
        }

    @register_tool(
        name="submit_approval",
        description="向企业 OA 流程中心提交报销、采购或请假审批单。",
        parameters={
            "type": "object",
            "properties": {
                "approval_type": {"type": "string", "description": "审批类型，如 差旅报销/算力采购/年假申请"},
                "applicant": {"type": "string", "description": "申请人姓名"},
                "amount": {"type": "number", "description": "涉及金额（元）", "default": 0},
                "reason": {"type": "string", "description": "申请事由说明"},
            },
            "required": ["approval_type", "applicant", "reason"],
        },
        registry=registry,
    )
    def submit_approval(
        approval_type: str,
        applicant: str,
        reason: str,
        amount: float = 0.0,
    ) -> Dict[str, Any]:
        ticket_id = f"OA-{uuid.uuid4().hex[:8].upper()}"
        need_director = amount >= 5000.0
        return {
            "ticket_id": ticket_id,
            "approval_type": approval_type,
            "applicant": applicant,
            "amount_cny": amount,
            "reason": reason,
            "approver_chain": ["直属主管", "部门总监", "财务复核"] if need_director else ["直属主管"],
            "status": "pending_approval",
        }

    return registry


# ==============================================================================
# 2. ReActAgent（Thought -> Action -> Observation 闭环推理引擎）
# ==============================================================================


class ReActAgent:
    """
    企业级 ReAct（Reasoning + Acting）Agent 引擎。
    每轮循环记录完整的 Thought（推理）、Action（工具调用）与 Observation（工具返回），
    并通过 `max_steps` 严格防止大模型陷入工具调用死循环。
    """

    def __init__(
        self,
        *,
        llm: Optional[BaseLLM] = None,
        tool_registry: Optional[ToolRegistry] = None,
        max_steps: int = 6,
    ) -> None:
        self.llm = llm or create_llm_client()
        self.tool_registry = tool_registry or build_default_tool_registry()
        self.max_steps = max_steps

    def run(self, query: str) -> Dict[str, Any]:
        start = time.perf_counter()
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "你是杭州星辰数科企业级 ReAct 智能助手。请按需调用工具获取实时事实或执行办公操作，"
                    "在拿到工具观察结果后，给出清晰、简洁、可落地的中文回复。"
                ),
            },
            {"role": "user", "content": query},
        ]
        openai_tools = self.tool_registry.to_openai_tools()
        steps: List[Dict[str, Any]] = []
        final_answer = ""

        for step_idx in range(1, self.max_steps + 1):
            resp = self.llm.chat(messages, tools=openai_tools)
            if resp.tool_calls:
                # 记录助理的 Tool Call 请求
                messages.append(
                    {
                        "role": "assistant",
                        "content": resp.content or "",
                        "tool_calls": [tc.to_dict() for tc in resp.tool_calls],
                    }
                )
                for tc in resp.tool_calls:
                    thought = f"第 {step_idx} 步推理：识别到需要调用工具 `{tc.name}` 来推进任务。"
                    try:
                        obs = self.tool_registry.execute(tc.name, tc.arguments)
                        obs_str = json.dumps(obs, ensure_ascii=False)
                        status = "ok"
                    except ToolExecutionError as exc:
                        obs_str = json.dumps({"error": exc.message}, ensure_ascii=False)
                        status = "error"

                    steps.append(
                        {
                            "step": step_idx,
                            "thought": thought,
                            "action": tc.name,
                            "action_input": tc.arguments,
                            "observation": obs_str,
                            "status": status,
                        }
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": tc.name,
                            "content": obs_str,
                        }
                    )
            else:
                final_answer = resp.content
                steps.append(
                    {
                        "step": step_idx,
                        "thought": f"第 {step_idx} 步推理：已具备足够信息，汇总生成最终回答。",
                        "action": "final_answer",
                        "action_input": {},
                        "observation": final_answer,
                        "status": "ok",
                    }
                )
                break
        else:
            final_answer = f"已达到最大推理步数限制（max_steps={self.max_steps}），自动触发防死循环熔断，请缩小任务范围。"

        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
        get_observability().record_span(
            name="agent.react",
            category="agent",
            latency_ms=elapsed_ms,
            metadata={"steps": len(steps)},
        )
        return {
            "query": query,
            "answer": final_answer,
            "steps": steps,
            "step_count": len(steps),
            "latency_ms": elapsed_ms,
        }


# ==============================================================================
# 3. StateGraph（类 LangGraph 状态图引擎 + Checkpointer + Human-in-the-loop）
# ==============================================================================


class BaseCheckpointer:
    """工作流状态检查点抽象基类。"""

    def save(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        raise NotImplementedError

    def load(self, thread_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError


class MemoryCheckpointer(BaseCheckpointer):
    """内存版检查点存储器（适用于单元测试与高频无状态编排）。"""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def save(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        self._store[thread_id] = json.loads(json.dumps(checkpoint, ensure_ascii=False))

    def load(self, thread_id: str) -> Optional[Dict[str, Any]]:
        data = self._store.get(thread_id)
        return json.loads(json.dumps(data, ensure_ascii=False)) if data is not None else None


class SQLiteCheckpointer(BaseCheckpointer):
    """SQLite 持久化检查点存储器（支持服务重启后继续恢复中断的人工审批流）。"""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                    thread_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        payload = json.dumps(checkpoint, ensure_ascii=False)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO workflow_checkpoints(thread_id, payload, updated_at)
                VALUES(?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at
                """,
                (thread_id, payload, time.time()),
            )
            conn.commit()

    def load(self, thread_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT payload FROM workflow_checkpoints WHERE thread_id = ?",
                (thread_id,),
            ).fetchone()
            return json.loads(row[0]) if row else None


class StateGraph:
    """
    轻量级类 LangGraph 状态图编排引擎。
    核心特性：
    - 节点注册（`add_node`）
    - 确定边（`add_edge`）与条件分支边（`add_conditional_edges`）
    - 检查点持久化（`MemoryCheckpointer` / `SQLiteCheckpointer`）
    - Human-in-the-loop 人工审批中断与恢复（`interrupt_before` + `resume`）
    """

    def __init__(
        self,
        checkpointer: Optional[BaseCheckpointer] = None,
        interrupt_before: Optional[List[str]] = None,
    ) -> None:
        self.nodes: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self.edges: Dict[str, str] = {}
        self.conditional_edges: Dict[str, Tuple[Callable[[Dict[str, Any]], str], Dict[str, str]]] = {}
        self.entry_point: Optional[str] = None
        self.checkpointer: BaseCheckpointer = checkpointer or MemoryCheckpointer()
        self.interrupt_before: set[str] = set(interrupt_before or [])

    def add_node(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> "StateGraph":
        self.nodes[name] = func
        return self

    def set_entry_point(self, name: str) -> "StateGraph":
        if name not in self.nodes:
            raise WorkflowStateError(f"入口节点 `{name}` 尚未注册")
        self.entry_point = name
        return self

    def add_edge(self, source: str, target: str) -> "StateGraph":
        self.edges[source] = target
        return self

    def add_conditional_edges(
        self,
        source: str,
        router: Callable[[Dict[str, Any]], str],
        path_map: Dict[str, str],
    ) -> "StateGraph":
        self.conditional_edges[source] = (router, path_map)
        return self

    def _next_node(self, current: str, state: Dict[str, Any]) -> str:
        if current in self.conditional_edges:
            router, path_map = self.conditional_edges[current]
            branch = router(state)
            if branch not in path_map:
                raise WorkflowStateError(f"条件路由 `{current}` 返回未知分支: {branch}")
            return path_map[branch]
        return self.edges.get(current, END)

    def _run_from(
        self,
        *,
        thread_id: str,
        current_node: str,
        state: Dict[str, Any],
        history: List[str],
        skip_interrupt_once: bool = False,
        max_hops: int = 30,
    ) -> Dict[str, Any]:
        hops = 0
        node = current_node

        while node != END:
            hops += 1
            if hops > max_hops:
                raise WorkflowStateError(f"工作流执行超过最大跳转步数 {max_hops}，疑似存在环路")

            # Human-in-the-loop 中断点拦截：保存检查点并暂停等待人工介入
            if node in self.interrupt_before and not skip_interrupt_once:
                checkpoint = {
                    "thread_id": thread_id,
                    "status": "interrupted",
                    "next_node": node,
                    "state": state,
                    "history": history,
                }
                self.checkpointer.save(thread_id, checkpoint)
                return checkpoint

            skip_interrupt_once = False
            if node not in self.nodes:
                raise WorkflowStateError(f"状态图节点 `{node}` 未定义")

            updates = self.nodes[node](dict(state))
            if isinstance(updates, dict):
                state.update(updates)
            history.append(node)

            next_node = self._next_node(node, state)
            self.checkpointer.save(
                thread_id,
                {
                    "thread_id": thread_id,
                    "status": "running" if next_node != END else "completed",
                    "next_node": next_node,
                    "state": state,
                    "history": history,
                },
            )
            node = next_node

        final_cp = {
            "thread_id": thread_id,
            "status": "completed",
            "next_node": END,
            "state": state,
            "history": history,
        }
        self.checkpointer.save(thread_id, final_cp)
        return final_cp

    def invoke(self, initial_state: Dict[str, Any], *, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """启动工作流执行；若命中 `interrupt_before` 节点则暂停并返回 `status='interrupted'`。"""
        if not self.entry_point:
            raise WorkflowStateError("状态图尚未设置入口节点（set_entry_point）")
        tid = thread_id or f"wf-{uuid.uuid4().hex[:10]}"
        return self._run_from(
            thread_id=tid,
            current_node=self.entry_point,
            state=dict(initial_state),
            history=[],
            skip_interrupt_once=False,
        )

    def resume(self, thread_id: str, human_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """从已保存的检查点恢复中断工作流，并注入人工审批决策数据。"""
        cp = self.checkpointer.load(thread_id)
        if cp is None:
            raise WorkflowStateError(f"未找到 thread_id=`{thread_id}` 的工作流检查点")
        if cp.get("status") != "interrupted":
            return cp

        state = dict(cp.get("state") or {})
        if human_input:
            state.update(human_input)

        return self._run_from(
            thread_id=thread_id,
            current_node=str(cp["next_node"]),
            state=state,
            history=list(cp.get("history") or []),
            skip_interrupt_once=True,
        )


def build_enterprise_approval_workflow(checkpointer: Optional[BaseCheckpointer] = None) -> StateGraph:
    """
    构建星辰智脑标准“企业费用/采购智能审批状态图”：
    1. `risk_assess`：自动风控评估（金额 >= 5000 元判定为高风险，走人工审批；< 5000 元自动通过）。
    2. `human_review`：人工审批节点（配置 `interrupt_before=['human_review']`，触发 Human-in-the-loop 中断）。
    3. `auto_approve`：低风险自动放行节点。
    4. `finalize_order`：生成最终审批回执与归档编号。
    """

    def risk_assess(state: Dict[str, Any]) -> Dict[str, Any]:
        amount = float(state.get("amount", 0.0))
        risk_level = "high" if amount >= 5000.0 else "low"
        return {
            "risk_level": risk_level,
            "assessment_note": (
                f"申请金额 {amount:.2f} 元达到复核阈值（>=5000元），需转入人工审批中断节点。"
                if risk_level == "high"
                else f"申请金额 {amount:.2f} 元属于低风险小额范围，可自动审批通过。"
            ),
        }

    def human_review(state: Dict[str, Any]) -> Dict[str, Any]:
        approved = bool(state.get("approved", True))
        reviewer = str(state.get("reviewer", "财务总监"))
        comment = str(state.get("comment", "同意执行" if approved else "预算超标驳回"))
        return {
            "approved": approved,
            "reviewer": reviewer,
            "review_comment": comment,
        }

    def auto_approve(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "approved": True,
            "reviewer": "星辰智脑风控规则引擎",
            "review_comment": "小额常规申请自动核准通过",
        }

    def finalize_order(state: Dict[str, Any]) -> Dict[str, Any]:
        approved = bool(state.get("approved", False))
        return {
            "decision": "APPROVED" if approved else "REJECTED",
            "receipt_no": f"RCPT-{uuid.uuid4().hex[:8].upper()}",
            "final_message": (
                f"审批单已通过（审批人：{state.get('reviewer')}，意见：{state.get('review_comment')}）"
                if approved
                else f"审批单已驳回（审批人：{state.get('reviewer')}，原因：{state.get('review_comment')}）"
            ),
        }

    graph = StateGraph(
        checkpointer=checkpointer or MemoryCheckpointer(),
        interrupt_before=["human_review"],
    )
    graph.add_node("risk_assess", risk_assess)
    graph.add_node("human_review", human_review)
    graph.add_node("auto_approve", auto_approve)
    graph.add_node("finalize_order", finalize_order)
    graph.set_entry_point("risk_assess")
    graph.add_conditional_edges(
        "risk_assess",
        lambda s: "high" if s.get("risk_level") == "high" else "low",
        {"high": "human_review", "low": "auto_approve"},
    )
    graph.add_edge("human_review", "finalize_order")
    graph.add_edge("auto_approve", "finalize_order")
    graph.add_edge("finalize_order", END)
    return graph


# ==============================================================================
# 4. MultiAgentSupervisor（多 Agent 协作编排：研究 + 分析 + 撰写 + 审核）
# ==============================================================================


class MultiAgentSupervisor:
    """
    主管模式多 Agent 协作系统（Supervisor Orchestration）。
    由 4 位各司其职的专家 Agent 顺序接力并交由主管汇总：
    1. Researcher（研究检索员）：负责知识库检索与事实依据收集；
    2. Analyst（数据分析师）：负责量化指标、成本收益与风险测算；
    3. Writer（报告撰写员）：整合调研与分析产出结构化中文方案报告；
    4. Reviewer（质量审核员）：执行合规性、完整性与可执行性终审。
    """

    def __init__(
        self,
        *,
        llm: Optional[BaseLLM] = None,
        rag_pipeline: Optional[RAGPipeline] = None,
    ) -> None:
        self.llm = llm or create_llm_client()
        self.rag_pipeline = rag_pipeline

    def run(self, task: str) -> Dict[str, Any]:
        start = time.perf_counter()
        kb_context = ""
        if self.rag_pipeline is not None:
            kb_res = self.rag_pipeline.query(task, top_k=2)
            if not kb_res.get("fallback_triggered"):
                kb_context = f"\n【企业知识库参考】\n{kb_res['answer']}"

        agent_outputs: List[Dict[str, str]] = []

        # 1. 研究检索员
        r1 = self.llm.chat(
            [
                {"role": "system", "content": "ROLE:RESEARCHER 你是资深研究检索员，负责整理背景事实与内部依据。"},
                {"role": "user", "content": f"请调研以下企业任务：{task}{kb_context}"},
            ]
        ).content
        agent_outputs.append({"agent": "Researcher(研究检索员)", "output": r1})

        # 2. 数据分析师
        r2 = self.llm.chat(
            [
                {"role": "system", "content": "ROLE:ANALYST 你是资深数据分析师，负责量化评估收益、成本与风险。"},
                {"role": "user", "content": f"任务：{task}\n调研摘要：\n{r1}"},
            ]
        ).content
        agent_outputs.append({"agent": "Analyst(数据分析师)", "output": r2})

        # 3. 报告撰写员
        r3 = self.llm.chat(
            [
                {"role": "system", "content": "ROLE:WRITER 你是企业战略报告撰写员，请输出结构化可执行方案。"},
                {"role": "user", "content": f"任务：{task}\n调研：\n{r1}\n分析：\n{r2}"},
            ]
        ).content
        agent_outputs.append({"agent": "Writer(报告撰写员)", "output": r3})

        # 4. 质量审核员
        r4 = self.llm.chat(
            [
                {"role": "system", "content": "ROLE:REVIEWER 你是质量审核员，请检查方案完整性与合规风险并给出结论。"},
                {"role": "user", "content": f"请审核以下报告：\n{r3}"},
            ]
        ).content
        agent_outputs.append({"agent": "Reviewer(质量审核员)", "output": r4})

        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
        get_observability().record_span(
            name="agent.multi_supervisor",
            category="multi_agent",
            latency_ms=elapsed_ms,
            metadata={"agents": 4},
        )
        return {
            "task": task,
            "agents": agent_outputs,
            "final_report": r3,
            "review_result": r4,
            "latency_ms": elapsed_ms,
        }


# ==============================================================================
# 5. TextToSQLAgent（安全只读自然语言转 SQL 数据分析引擎）
# ==============================================================================


class TextToSQLAgent:
    """
    企业级 Text-to-SQL Agent。
    安全机制：
    - 强制白名单校验：仅允许单条 `SELECT`（或 `WITH ... SELECT`）查询语句；
    - 严禁出现 `DROP / DELETE / UPDATE / INSERT / ALTER / CREATE / REPLACE / TRUNCATE / ATTACH / PRAGMA`；
    - 严禁多语句分号 `;` 拼接或 `--` / `/*` SQL 注入注释。
    """

    FORBIDDEN_SQL_RE = re.compile(
        r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|PRAGMA|EXEC|EXECUTE)\b",
        re.IGNORECASE,
    )

    SCHEMA_PROMPT = (
        "数据库表 `enterprise_sales` 字段定义：\n"
        "- id (INTEGER): 主键\n"
        "- order_no (TEXT): 订单号\n"
        "- customer_name (TEXT): 客户名称\n"
        "- region (TEXT): 销售大区（华东/华北/华南/西南）\n"
        "- product_name (TEXT): 产品名称\n"
        "- quarter (TEXT): 季度（2026Q1~2026Q4）\n"
        "- quantity (INTEGER): 采购数量\n"
        "- amount_cny (REAL): 合同金额（人民币元）\n"
        "- sales_owner (TEXT): 负责销售\n"
    )

    def __init__(
        self,
        *,
        llm: Optional[BaseLLM] = None,
        db_manager: Optional[DatabaseManager] = None,
    ) -> None:
        self.llm = llm or create_llm_client()
        self.db = db_manager or get_db_manager()

    @classmethod
    def validate_readonly_sql(cls, sql: str) -> str:
        """校验 SQL 必须为安全只读 SELECT 单语句，发现高危操作立即抛出 `SQLSafetyError`。"""
        cleaned = sql.strip()
        # 去除大模型可能包裹的 Markdown 代码块
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned).strip()

        # 允许末尾单个分号，但禁止语句中间分号（防堆叠注入）
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()
        if ";" in cleaned:
            raise SQLSafetyError("检测到多语句分号拼接，已触发 SQL 注入拦截！")

        if "--" in cleaned or "/*" in cleaned:
            raise SQLSafetyError("检测到 SQL 注释符注入风险，已拦截执行！")

        upper_sql = cleaned.upper()
        if not (upper_sql.startswith("SELECT ") or upper_sql.startswith("WITH ")):
            raise SQLSafetyError("安全策略仅允许只读 SELECT 查询，已拒绝非查询语句！")

        match = cls.FORBIDDEN_SQL_RE.search(cleaned)
        if match:
            raise SQLSafetyError(f"检测到禁止的写操作/高危关键字 `{match.group(1).upper()}`，已拦截！")

        return cleaned

    def query(self, question: str, *, override_sql: Optional[str] = None) -> Dict[str, Any]:
        """将自然语言问题转为 SQL，执行安全只读查询并输出结构化表格与中文解读。"""
        start = time.perf_counter()

        # 若用户在自然语言里直接尝试 SQL 破坏性指令，优先拦截
        if self.FORBIDDEN_SQL_RE.search(question):
            raise SQLSafetyError("检测到高危数据库写操作/删除意图，Text-to-SQL 安全护栏已拦截！")

        if override_sql is not None:
            raw_sql = override_sql
        else:
            llm_resp = self.llm.chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "TEXT_TO_SQL_MODE: 你是精通 SQLite 的数据分析师，请根据表结构仅输出一条合法的 SELECT SQL，"
                            "禁止输出任何写操作或解释文字。\n" + self.SCHEMA_PROMPT
                        ),
                    },
                    {"role": "user", "content": question},
                ]
            )
            raw_sql = llm_resp.content

        safe_sql = self.validate_readonly_sql(raw_sql)
        query_result = self.db.execute_readonly_query(safe_sql)
        rows = query_result["rows"]

        # 自动生成简明业务数据解读
        if not rows:
            interpretation = "未查询到符合条件的销售记录。"
        else:
            top_row = rows[0]
            top_summary = "，".join(f"{k}={v}" for k, v in top_row.items())
            interpretation = (
                f"共查询到 {len(rows)} 条汇总/明细记录。排名首位数据为：{top_summary}。"
                f"所有数据均实时读取自企业 SQLite 销售业绩库 `enterprise_sales`。"
            )

        elapsed_ms = round((time.perf_counter() - start) * 1000.0, 2)
        get_observability().record_span(
            name="agent.text_to_sql",
            category="sql",
            latency_ms=elapsed_ms,
            metadata={"row_count": len(rows)},
        )
        return {
            "question": question,
            "sql": safe_sql,
            "columns": query_result["columns"],
            "rows": rows,
            "row_count": len(rows),
            "interpretation": interpretation,
            "latency_ms": elapsed_ms,
        }


# ==============================================================================
# 6. MCPServer & MCPClient（JSON-RPC 2.0 Model Context Protocol 实现）
# ==============================================================================


class MCPServer:
    """
    遵循 Model Context Protocol (MCP) JSON-RPC 2.0 规范的企业工具与资源服务端。
    支持方法：
    - `initialize`：协议版本与服务端能力协商
    - `tools/list`：列举已注册企业工具及 JSON Schema
    - `tools/call`：按名称与参数执行企业工具并返回 MCP 标准 `content` 结构
    - `resources/list`：列举可供 Agent 挂载的企业只读资源（如销售表结构、知识库统计）
    - `resources/read`：按 URI 读取资源文本内容
    """

    PROTOCOL_VERSION = "2024-11-05"

    def __init__(
        self,
        tool_registry: ToolRegistry,
        *,
        server_name: str = "starmind-mcp-server",
        server_version: str = "1.0.0",
    ) -> None:
        self.tool_registry = tool_registry
        self.server_name = server_name
        self.server_version = server_version
        self._resources: Dict[str, Dict[str, str]] = {
            "starmind://schema/enterprise_sales": {
                "uri": "starmind://schema/enterprise_sales",
                "name": "企业销售业绩表 Schema",
                "mimeType": "text/plain",
                "content": TextToSQLAgent.SCHEMA_PROMPT,
            },
            "starmind://policy/security": {
                "uri": "starmind://policy/security",
                "name": "星辰智脑数据安全与脱敏规范",
                "mimeType": "text/plain",
                "content": "所有进入大模型的手机号、身份证号、银行卡号与邮箱均需脱敏，禁止对业务库执行任何写操作。",
            },
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return [t.to_mcp_schema() for t in self.tool_registry.list_tools()]

    def list_resources(self) -> List[Dict[str, str]]:
        return [
            {"uri": r["uri"], "name": r["name"], "mimeType": r["mimeType"]}
            for r in self._resources.values()
        ]

    def handle_rpc(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理单条标准 JSON-RPC 2.0 请求并返回合规响应体。"""
        req_id = request.get("id")
        if request.get("jsonrpc") != "2.0" or not request.get("method"):
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "无效的 JSON-RPC 2.0 请求格式"},
            }

        method = str(request["method"])
        params = request.get("params") or {}

        try:
            if method == "initialize":
                result: Any = {
                    "protocolVersion": self.PROTOCOL_VERSION,
                    "serverInfo": {"name": self.server_name, "version": self.server_version},
                    "capabilities": {"tools": {}, "resources": {}},
                }
            elif method == "tools/list":
                result = {"tools": self.list_tools()}
            elif method == "tools/call":
                tool_name = str(params.get("name") or "")
                arguments = dict(params.get("arguments") or {})
                tool_output = self.tool_registry.execute(tool_name, arguments)
                result = {
                    "content": [
                        {"type": "text", "text": json.dumps(tool_output, ensure_ascii=False)}
                    ],
                    "isError": False,
                }
            elif method == "resources/list":
                result = {"resources": self.list_resources()}
            elif method == "resources/read":
                uri = str(params.get("uri") or "")
                res = self._resources.get(uri)
                if res is None:
                    return {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32002, "message": f"未找到指定资源 URI: {uri}"},
                    }
                result = {
                    "contents": [
                        {"uri": res["uri"], "mimeType": res["mimeType"], "text": res["content"]}
                    ]
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"不支持的 MCP 方法: {method}"},
                }

            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except ToolExecutionError as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": exc.message},
            }


class MCPClient:
    """进程内直连 MCPClient（亦可扩展为 HTTP/stdio 传输层）。"""

    def __init__(self, server: MCPServer) -> None:
        self.server = server
        self._seq = 0

    def _call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._seq += 1
        payload = {"jsonrpc": "2.0", "id": self._seq, "method": method, "params": params or {}}
        return self.server.handle_rpc(payload)

    def initialize(self) -> Dict[str, Any]:
        return self._call("initialize")

    def list_tools(self) -> List[Dict[str, Any]]:
        resp = self._call("tools/list")
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._call("tools/call", {"name": name, "arguments": arguments or {}})

    def list_resources(self) -> List[Dict[str, str]]:
        resp = self._call("resources/list")
        return resp.get("result", {}).get("resources", [])
