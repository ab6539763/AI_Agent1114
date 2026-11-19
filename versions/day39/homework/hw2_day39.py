"""
Day 39 课后作业 2（企业实战）：为 ReAct 引擎增加单步耗时监控与轨迹 JSON 导出
工单：STARMIND-039
"""

"""Day 39 作业 2 参考答案：带耗时统计的轨迹追踪器。"""

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, List


@dataclass
class TimedStep:
    step: int
    action: str
    observation: str
    latency_ms: float


@dataclass
class TimedTrace:
    question: str
    steps: List[TimedStep] = field(default_factory=list)

    def to_trace_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)


def run_timed_tool(func: Callable[[str], str], arg: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    res = func(arg)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
    return res, elapsed_ms


if __name__ == "__main__":
    obs, ms = run_timed_tool(lambda x: f"echo:{x}", "星辰数科")
    trace = TimedTrace(question="测试耗时", steps=[TimedStep(1, "echo", obs, ms)])
    payload = trace.to_trace_json()
    print(payload)
    assert "latency_ms" in payload

