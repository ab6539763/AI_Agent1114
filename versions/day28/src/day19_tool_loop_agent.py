"""
StarMind Day 19 - 步骤二：纯 API Function Calling 多步工具调用闭环引擎
完整实现 OpenAI tool_calls -> 本地执行 -> role="tool" 回填 -> 最终汇总的标准 Agent 闭环。
"""

import json
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.day19_tool_registry import ToolRegistry, build_default_registry


@dataclass
class LoopRunResult:
    """工具调用闭环运行结果与完整审计轨迹。"""
    final_answer: str
    rounds: int
    tool_invocations: List[Dict[str, Any]] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    stopped_by_limit: bool = False


class MockToolCallingModel:
    """
    离线仿真支持 Parallel Tool Calling 的大模型决策器。
    - 第一轮：解析用户自然语言中的多意图，生成标准 OpenAI `tool_calls` 列表。
    - 后续轮：读取 `role='tool'` 的全部观察结果，汇总生成最终企业级答复。
    """

    _MATH_EXPR_RE = re.compile(r"[\d\.\(\)\+\-\*/\s]{3,}")

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        # 检查是否已经拿到工具观察结果
        tool_msgs = [m for m in messages if m.get("role") == "tool"]
        if tool_msgs:
            summary_lines = ["星辰智脑已为您完成实时工具核验，汇总结果如下："]
            for tm in tool_msgs:
                data = json.loads(tm["content"])
                t_name = tm.get("name", "unknown")
                if t_name == "get_weather" and data.get("status") == "ok":
                    summary_lines.append(
                        f"- 【天气】{data['city']}：{data['weather']}，{data['temp_c']}°C（{data['advice']}）。"
                    )
                elif t_name == "safe_calculator" and data.get("status") == "ok":
                    summary_lines.append(
                        f"- 【计算结果】`{data['expression']}` = **{data['result']}**。"
                    )
                elif t_name == "search_internal_kb" and data.get("status") == "ok":
                    hits = data.get("hits", [])
                    if hits:
                        summary_lines.append(f"- 【内部制度】{hits[0]['title']}：{hits[0]['content']}")
                    else:
                        summary_lines.append(f"- 【内部制度】未检索到与「{data.get('keyword')}」匹配的制度。")
                else:
                    summary_lines.append(f"- 【工具异常({t_name})】{data.get('error', '执行失败')}")
            return {"role": "assistant", "content": "\n".join(summary_lines), "tool_calls": []}

        # 第一轮：根据最新 user 消息决定需要并行调用的工具集合
        user_text = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        tool_calls: List[Dict[str, Any]] = []

        # 1. 检测天气需求
        for city in ("杭州", "北京", "上海", "深圳"):
            if city in user_text and ("天气" in user_text or "下雨" in user_text or "温度" in user_text):
                tool_calls.append(self._make_call("get_weather", {"city": city}))

        # 2. 检测数学计算需求
        math_matches = [m.strip() for m in self._MATH_EXPR_RE.findall(user_text) if any(op in m for op in "+-*/")]
        if math_matches:
            tool_calls.append(self._make_call("safe_calculator", {"expression": math_matches[0]}))

        # 3. 检测企业内部知识库需求
        for kb_kw in ("差旅", "报销", "住宿", "VPN", "预算"):
            if kb_kw.lower() in user_text.lower():
                tool_calls.append(self._make_call("search_internal_kb", {"keyword": kb_kw}))
                break

        if tool_calls:
            return {"role": "assistant", "content": None, "tool_calls": tool_calls}

        return {
            "role": "assistant",
            "content": f"您好！您的问题「{user_text}」无需调用外部工具，星辰智脑直接为您解答：如需查询天气、计算报销或检索公司制度，随时告诉我。",
            "tool_calls": [],
        }

    @staticmethod
    def _make_call(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {
                "name": name,
                "arguments": json.dumps(args, ensure_ascii=False),
            },
        }


class FunctionCallingLoopEngine:
    """标准纯 API Function Calling 多步执行闭环引擎。"""

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        model: Any | None = None,
        max_rounds: int = 5,
    ) -> None:
        self.registry = registry or build_default_registry()
        self.model = model or MockToolCallingModel()
        self.max_rounds = max_rounds

    def run(self, user_query: str, system_prompt: str = "你是星辰智脑企业办公助手，请善用工具精准回答。") -> LoopRunResult:
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query},
        ]
        tools_schema = self.registry.export_openai_tools()
        invocations: List[Dict[str, Any]] = []

        for round_idx in range(1, self.max_rounds + 1):
            assistant_msg = self.model.create_completion(messages, tools_schema)
            messages.append(assistant_msg)
            tool_calls = assistant_msg.get("tool_calls") or []

            if not tool_calls:
                return LoopRunResult(
                    final_answer=str(assistant_msg.get("content") or ""),
                    rounds=round_idx,
                    tool_invocations=invocations,
                    messages=messages,
                    stopped_by_limit=False,
                )

            # 严格按照 OpenAI 协议：逐一执行每个 tool_call 并回填对应 tool_call_id
            for call in tool_calls:
                call_id = call["id"]
                fn_name = call["function"]["name"]
                fn_args = call["function"]["arguments"]
                tool_output = self.registry.execute(fn_name, fn_args)

                invocations.append({
                    "round": round_idx,
                    "tool_call_id": call_id,
                    "name": fn_name,
                    "arguments": fn_args,
                    "output": tool_output,
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": fn_name,
                    "content": tool_output,
                })

        return LoopRunResult(
            final_answer="⚠️ 工具调用轮次达到安全上限，已触发熔断机制，请简化问题后重试。",
            rounds=self.max_rounds,
            tool_invocations=invocations,
            messages=messages,
            stopped_by_limit=True,
        )


if __name__ == "__main__":
    engine = FunctionCallingLoopEngine()
    query = "我明天去杭州出差，帮我查下杭州天气、公司差旅住宿标准，顺便算一下 600 * 3 + 240 是多少钱？"
    res = engine.run(query)
    print(f"闭环轮次: {res.rounds} | 调用工具数: {len(res.tool_invocations)}")
    print(res.final_answer)

