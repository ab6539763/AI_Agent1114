import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 40 自动化单元测试：验证 @tool Schema 提取、安全工具防御与 AgentExecutor 回调链。"""

from pathlib import Path
import pytest
from src.day40_tool_schema import tool, build_enterprise_tools
from src.day40_agent_executor import (
    AgentExecutor,
    MockToolCallingAgent,
    TraceCallbackHandler,
)


def test_tool_decorator_schema_and_validation():
    @tool
    def multiply(a: int, b: int = 2) -> int:
        """计算两个整数的乘积。"""
        return a * b

    schema = multiply.to_openai_schema()
    assert schema["function"]["name"] == "multiply"
    assert "a" in schema["function"]["parameters"]["required"]
    assert "b" not in schema["function"]["parameters"]["required"]
    # 自动类型转换: '5' -> 5
    assert multiply.invoke({"a": "5", "b": 3}) == "15"
    # 非法类型拦截
    assert "参数校验失败" in multiply.invoke({"a": "not_an_int"})


def test_enterprise_tools_security(tmp_path: Path):
    tools = {t.name: t for t in build_enterprise_tools(tmp_path)}
    assert "5000" in tools["knowledge_search"].invoke({"keyword": "Q3"})
    assert tools["sandbox_python_calc"].invoke({"expression": "(10 + 5) * 4"}) == "60"
    assert "禁止执行" in tools["sandbox_python_calc"].invoke({"expression": "open('/etc/passwd')"})
    assert "安全拦截" in tools["safe_write_file"].invoke({"filename": "../escape.txt", "content": "x"})
    assert "安全拦截" in tools["safe_read_file"].invoke({"filename": "/etc/hosts"})


def test_agent_executor_full_workflow_and_callbacks(tmp_path: Path):
    tools = build_enterprise_tools(tmp_path)
    tracer = TraceCallbackHandler()
    executor = AgentExecutor(agent=MockToolCallingAgent(), tools=tools, callbacks=[tracer])

    res = executor.invoke("查询公司Q3研发目标并写入文件")
    assert "q3_summary.md" in res["output"]
    assert len(res["intermediate_steps"]) == 2
    assert (tmp_path / "q3_summary.md").exists()
    assert "5000" in (tmp_path / "q3_summary.md").read_text(encoding="utf-8")

    event_types = [e["event"] for e in tracer.events]
    assert event_types[0] == "agent_action"
    assert event_types[-1] == "agent_finish"
    assert event_types.count("tool_end") == 2

