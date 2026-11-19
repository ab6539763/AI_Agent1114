import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 39 自动化单元测试：验证 AST 安全计算器、工具注册表与 ReAct 引擎全链路。"""

import pytest
from src.day39_tools import build_default_registry, safe_calculator, internal_search
from src.day39_react_agent import ReActAgent, DeterministicReActLLM, parse_react_output


def test_safe_calculator_normal_and_security():
    assert safe_calculator("(600 + 120) * 3") == "2160"
    assert safe_calculator("10 / 4") == "2.50"
    assert "计算失败" in safe_calculator("__import__('os').system('echo pwned')")
    assert "指数绝对值不能超过" in safe_calculator("9 ** 999")
    assert "除数不能为 0" in safe_calculator("100 / 0")


def test_internal_search_hit_and_miss():
    res = internal_search("上海 差旅")
    assert "600" in res and "120" in res
    miss = internal_search("外星人福利")
    assert "未在内网知识库中找到" in miss


def test_react_agent_multi_step_travel_reimbursement():
    agent = ReActAgent(llm=DeterministicReActLLM(), registry=build_default_registry(), max_steps=5)
    result = agent.run("我下周去上海出差 3 天，住宿和餐补最多报销多少？")
    assert result.stopped_reason == "completed"
    assert "2160" in result.final_answer
    assert len(result.steps) == 3
    assert result.steps[0].action == "internal_search"
    assert result.steps[1].action == "safe_calculator"


def test_react_agent_max_steps_circuit_breaker():
    # 模拟一个陷入死循环的模型
    def looping_llm(_prompt: str) -> str:
        return "Thought: 继续查\nAction: internal_search\nAction Input: 上海"

    agent = ReActAgent(llm=looping_llm, registry=build_default_registry(), max_steps=3)
    result = agent.run("测试死循环")
    assert result.stopped_reason == "max_steps_reached"
    assert len(result.steps) == 3


def test_react_agent_unknown_tool_recovery():
    calls = {"n": 0}

    def recovering_llm(prompt: str) -> str:
        calls["n"] += 1
        if calls["n"] == 1:
            return "Thought: 试试不存在的工具\nAction: magic_tool\nAction Input: test"
        assert "未知工具 'magic_tool'" in prompt
        return "Thought: 工具名错了，改用直接回复\nFinal Answer: 已修正错误并安全返回"

    agent = ReActAgent(llm=recovering_llm, registry=build_default_registry(), max_steps=4)
    result = agent.run("测试未知工具恢复")
    assert result.stopped_reason == "completed"
    assert "已修正" in result.final_answer

