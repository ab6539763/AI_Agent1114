"""Day 40 - 步骤二：ToolCallingAgent、AgentExecutor 与 CallbackHandler 观测引擎。"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from src.day40_tool_schema import StructuredTool, build_enterprise_tools
except ImportError:
    from day40_tool_schema import StructuredTool, build_enterprise_tools


@dataclass
class ToolCallAction:
    """模型输出的结构化工具调用指令（对齐 OpenAI tool_calls）。"""

    tool_name: str
    tool_args: Dict[str, Any]
    thought: str = ""


@dataclass
class AgentFinish:
    """模型输出的最终完成信号。"""

    output: str


class CallbackHandler:
    """可插拔回调基类：用于监听 Agent 全生命周期事件。"""

    def on_agent_action(self, action: ToolCallAction) -> None:
        pass

    def on_tool_start(self, tool_name: str, tool_args: Dict[str, Any]) -> None:
        pass

    def on_tool_end(self, tool_name: str, observation: str, latency_ms: float) -> None:
        pass

    def on_agent_finish(self, finish: AgentFinish) -> None:
        pass


class TraceCallbackHandler(CallbackHandler):
    """实战观测回调器：收集结构化事件日志供排查与前端进度展示。"""

    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def on_agent_action(self, action: ToolCallAction) -> None:
        self.events.append({"event": "agent_action", "tool": action.tool_name, "args": action.tool_args})

    def on_tool_start(self, tool_name: str, tool_args: Dict[str, Any]) -> None:
        self.events.append({"event": "tool_start", "tool": tool_name})

    def on_tool_end(self, tool_name: str, observation: str, latency_ms: float) -> None:
        self.events.append(
            {"event": "tool_end", "tool": tool_name, "latency_ms": latency_ms, "preview": observation[:60]}
        )

    def on_agent_finish(self, finish: AgentFinish) -> None:
        self.events.append({"event": "agent_finish", "output_len": len(finish.output)})


class MockToolCallingAgent:
    """
    本地确定性 ToolCallingAgent（模拟原生 Function Calling 模型行为）。
    接收用户输入与历史中间步骤，决定返回 ToolCallAction 或 AgentFinish。
    """

    def plan(
        self,
        user_input: str,
        intermediate_steps: List[Tuple[ToolCallAction, str]],
        tool_schemas: List[Dict[str, Any]],
    ) -> ToolCallAction | AgentFinish:
        assert len(tool_schemas) > 0, "必须向模型提供工具 Schema 列表"

        # 场景：查 Q3 目标并写入周报文件
        if "Q3" in user_input and "写入" in user_input:
            if len(intermediate_steps) == 0:
                return ToolCallAction(
                    tool_name="knowledge_search",
                    tool_args={"keyword": "Q3", "top_k": 1},
                    thought="先检索星辰数科 Q3 研发目标文档",
                )
            if len(intermediate_steps) == 1:
                doc_obs = intermediate_steps[0][1]
                return ToolCallAction(
                    tool_name="safe_write_file",
                    tool_args={"filename": "q3_summary.md", "content": f"# Q3目标摘录\n{doc_obs}\n"},
                    thought="已获取目标内容，将其安全写入 q3_summary.md",
                )
            write_obs = intermediate_steps[-1][1]
            return AgentFinish(output=f"已完成检索并生成文件：{write_obs}")

        return AgentFinish(output="未匹配到需要调用工具的复合指令，直接回复完成。")


class AgentExecutor:
    """对齐 LangChain AgentExecutor：负责驱动循环、工具分发、熔断与回调通知。"""

    def __init__(
        self,
        agent: MockToolCallingAgent,
        tools: List[StructuredTool],
        callbacks: Optional[List[CallbackHandler]] = None,
        max_iterations: int = 5,
    ) -> None:
        self.agent = agent
        self.tool_map: Dict[str, StructuredTool] = {t.name: t for t in tools}
        self.tool_schemas: List[Dict[str, Any]] = [t.to_openai_schema() for t in tools]
        self.callbacks = callbacks or []
        self.max_iterations = max_iterations

    def invoke(self, user_input: str) -> Dict[str, Any]:
        intermediate_steps: List[Tuple[ToolCallAction, str]] = []

        for _ in range(self.max_iterations):
            decision = self.agent.plan(user_input, intermediate_steps, self.tool_schemas)
            if isinstance(decision, AgentFinish):
                for cb in self.callbacks:
                    cb.on_agent_finish(decision)
                return {
                    "input": user_input,
                    "output": decision.output,
                    "intermediate_steps": intermediate_steps,
                }

            for cb in self.callbacks:
                cb.on_agent_action(decision)

            tool_obj = self.tool_map.get(decision.tool_name)
            t0 = time.perf_counter()
            for cb in self.callbacks:
                cb.on_tool_start(decision.tool_name, decision.tool_args)

            if tool_obj is None:
                observation = f"错误：未注册工具 '{decision.tool_name}'"
            else:
                observation = tool_obj.invoke(decision.tool_args)

            latency_ms = round((time.perf_counter() - t0) * 1000, 3)
            for cb in self.callbacks:
                cb.on_tool_end(decision.tool_name, observation, latency_ms)

            intermediate_steps.append((decision, observation))

        return {
            "input": user_input,
            "output": f"已达到最大迭代次数 {self.max_iterations}，任务中止。",
            "intermediate_steps": intermediate_steps,
        }


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tools = build_enterprise_tools(Path(tmp))
        tracer = TraceCallbackHandler()
        executor = AgentExecutor(agent=MockToolCallingAgent(), tools=tools, callbacks=[tracer])
        res = executor.invoke("帮我查一下公司Q3研发目标，并写入周报文件")
        print("最终输出:", res["output"])
        print("中间步骤数:", len(res["intermediate_steps"]))
        print("回调事件流:", [e["event"] for e in tracer.events])

