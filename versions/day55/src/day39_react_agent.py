"""Day 39 - 步骤二：零框架纯 Python 手写 ReAct Agent 引擎。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

try:
    from src.day39_tools import ToolRegistry, build_default_registry
except ImportError:
    from day39_tools import ToolRegistry, build_default_registry


REACT_SYSTEM_PROMPT = """你是杭州星辰数科的企业智能助手「星辰智脑」。
请严格使用以下 ReAct 格式逐步推理并调用工具回答问题：

可用工具列表：
{tool_docs}

输出格式规范：
Thought: 你的当前思考过程
Action: 要调用的工具名称（必须是 [{tool_names}] 之一）
Action Input: 传给工具的输入参数
Observation: （由系统自动填入工具执行结果，严禁你自行编造）
...（可重复多轮 Thought/Action/Action Input/Observation）
Thought: 我已经掌握足够信息，可以给出最终答复
Final Answer: 给用户的清晰、准确的最终答复

用户问题：{question}
{scratchpad}"""


@dataclass
class AgentStep:
    """记录 ReAct 单步执行轨迹，便于追踪与调试。"""

    step_index: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[str] = None
    observation: Optional[str] = None


@dataclass
class AgentResult:
    """Agent 执行总结果。"""

    final_answer: str
    steps: List[AgentStep] = field(default_factory=list)
    stopped_reason: str = "completed"  # completed | max_steps_reached


def parse_react_output(text: str) -> Tuple[str, Optional[str], Optional[str], Optional[str]]:
    """
    解析模型输出的 ReAct 文本。
    返回: (thought, action, action_input, final_answer)
    """
    thought_match = re.search(r"Thought:\s*(.*?)(?=\n(?:Action:|Final Answer:)|$)", text, re.S)
    thought = thought_match.group(1).strip() if thought_match else ""

    final_match = re.search(r"Final Answer:\s*(.*)", text, re.S)
    if final_match:
        return thought, None, None, final_match.group(1).strip()

    action_match = re.search(r"Action:\s*([^\n]+)", text)
    input_match = re.search(r"Action Input:\s*([^\n]+)", text)
    action = action_match.group(1).strip() if action_match else None
    action_input = input_match.group(1).strip() if input_match else None
    return thought, action, action_input, None


class DeterministicReActLLM:
    """
    本地确定性 ReAct LLM 模拟器（零外网依赖，用于教学演示与 CI 单元测试）。
    生产环境替换为：
        client.chat.completions.create(
            model="qwen-plus", messages=[{"role": "user", "content": prompt}],
            temperature=0, stop=["Observation:", "\\nObservation:"]
        ).choices[0].message.content
    """

    def __call__(self, prompt: str) -> str:
        # 场景 1：上海差旅 3 天报销核算
        if "上海" in prompt and "3" in prompt and "报销" in prompt:
            if "600 元/晚" not in prompt:
                return (
                    "Thought: 员工询问去上海出差 3 天的住宿和餐补报销总额，我需要先查询公司上海差旅标准。\n"
                    "Action: internal_search\n"
                    "Action Input: 上海 差旅 住宿 餐补"
                )
            if "2160" not in prompt:
                return (
                    "Thought: 已查到上海住宿上限 600 元/晚，餐补 120 元/天。为避免心算出错，调用安全计算器算 3 天总额。\n"
                    "Action: safe_calculator\n"
                    "Action Input: (600 + 120) * 3"
                )
            return (
                "Thought: 计算器返回 2160，信息已完整，可以给员工答复。\n"
                "Final Answer: 根据《杭州星辰数科2026差旅报销标准》，上海（一线城市）住宿上限 600 元/晚、餐补 120 元/天，"
                "出差 3 天住宿加餐补最高可报销 2160 元（市内交通另按实报实销上限 80 元/天计算）。"
            )

        # 场景 2：纯数学计算问题
        if "计算" in prompt and "Observation:" not in prompt:
            expr_match = re.search(r"计算[：:\s]*([0-9+\-*/().\s]+)", prompt)
            expr = expr_match.group(1).strip() if expr_match else "1+1"
            return (
                f"Thought: 这是一个纯数学计算请求，直接调用 safe_calculator 工具计算 {expr}。\n"
                f"Action: safe_calculator\n"
                f"Action Input: {expr}"
            )
        if "计算" in prompt and "Observation:" in prompt:
            obs_vals = re.findall(r"Observation:\s*(.+)", prompt)
            ans = obs_vals[-1].strip() if obs_vals else "未知"
            return (
                "Thought: 计算器已经返回精确结果。\n"
                f"Final Answer: 计算结果为 {ans}。"
            )

        return (
            "Thought: 当前问题无需调用外部工具，直接作答。\n"
            "Final Answer: 抱歉，我暂未在知识库中找到对应场景，请联系星辰数科行政部。"
        )


class ReActAgent:
    """零框架手写 ReAct 智能体主引擎。"""

    def __init__(
        self,
        llm: Callable[[str], str],
        registry: ToolRegistry,
        max_steps: int = 5,
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.max_steps = max_steps

    def run(self, question: str) -> AgentResult:
        scratchpad_parts: List[str] = []
        steps: List[AgentStep] = []

        for step_idx in range(1, self.max_steps + 1):
            prompt = REACT_SYSTEM_PROMPT.format(
                tool_docs=self.registry.render_prompt_docs(),
                tool_names=", ".join(self.registry.list_names()),
                question=question,
                scratchpad="\n".join(scratchpad_parts),
            )
            raw_output = self.llm(prompt)
            thought, action, action_input, final_answer = parse_react_output(raw_output)

            if final_answer is not None:
                steps.append(AgentStep(step_index=step_idx, thought=thought))
                return AgentResult(final_answer=final_answer, steps=steps, stopped_reason="completed")

            if not action:
                # 协议解析失败，不崩溃，将纠偏提示写回 Observation 引导下一轮修正
                obs = "格式错误：请严格输出 Action 与 Action Input，或直接输出 Final Answer。"
                steps.append(AgentStep(step_index=step_idx, thought=thought, observation=obs))
                scratchpad_parts.append(f"Thought: {thought}\nObservation: {obs}")
                continue

            observation = self.registry.execute(action, action_input or "")
            steps.append(
                AgentStep(
                    step_index=step_idx,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    observation=observation,
                )
            )
            scratchpad_parts.append(
                f"Thought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"
            )

        return AgentResult(
            final_answer=f"已达到最大推理步数上限（{self.max_steps}步），任务安全中止，请缩小问题范围后重试。",
            steps=steps,
            stopped_reason="max_steps_reached",
        )


if __name__ == "__main__":
    agent = ReActAgent(llm=DeterministicReActLLM(), registry=build_default_registry(), max_steps=5)
    result = agent.run("我下周去上海出差 3 天，按公司标准住宿加餐补最多能报销多少钱？")
    for s in result.steps:
        print(f"[Step {s.step_index}] Thought: {s.thought}")
        if s.action:
            print(f"         Action: {s.action}({s.action_input}) -> Obs: {s.observation}")
    print("\n>>> Final Answer:", result.final_answer)

