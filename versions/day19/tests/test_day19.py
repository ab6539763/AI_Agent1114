import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 19 自动化单元测试：验证 Tool Schema、AST 安全防注入与多步 Function Calling 闭环。"""

import json
import pytest
from src.day19_tool_registry import build_default_registry, safe_eval_math
from src.day19_tool_loop_agent import FunctionCallingLoopEngine


def test_openai_tool_schema_and_safe_calculator():
    reg = build_default_registry()
    schemas = reg.export_openai_tools()
    assert len(schemas) == 3
    for s in schemas:
        assert s["type"] == "function"
        assert "name" in s["function"]
        assert "parameters" in s["function"]

    assert safe_eval_math("(600 * 3 + 240) / 2") == pytest.approx(1020.0)
    # 验证安全拦截代码注入与超大幂 DoS
    with pytest.raises(ValueError):
        safe_eval_math("__import__('os').system('echo hacked')")
    with pytest.raises(ValueError):
        safe_eval_math("9 ** 999")


def test_tool_registry_error_isolation():
    reg = build_default_registry()
    err_json = reg.execute("safe_calculator", '{"expression": "10 / 0"}')
    data = json.loads(err_json)
    assert data["status"] == "error"
    assert "0" in data["error"]

    unknown_json = reg.execute("drop_database", "{}")
    assert json.loads(unknown_json)["status"] == "error"


def test_parallel_function_calling_loop():
    engine = FunctionCallingLoopEngine()
    res = engine.run("查一下杭州天气和公司差旅报销标准，并算下 600 * 3 + 150")
    assert res.rounds == 2
    assert res.stopped_by_limit is False
    assert len(res.tool_invocations) == 3
    called_names = {inv["name"] for inv in res.tool_invocations}
    assert called_names == {"get_weather", "safe_calculator", "search_internal_kb"}
    assert "1950.0" in res.final_answer
    assert "杭州" in res.final_answer
    assert "600 元/晚" in res.final_answer


def test_loop_circuit_breaker_max_rounds():
    class InfiniteLoopModel:
        def create_completion(self, messages, tools):
            return {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {"id": "call_loop", "type": "function", "function": {"name": "get_weather", "arguments": '{"city":"杭州"}'}}
                ],
            }

    engine = FunctionCallingLoopEngine(model=InfiniteLoopModel(), max_rounds=3)
    res = engine.run("测试熔断")
    assert res.stopped_by_limit is True
    assert res.rounds == 3

