import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 43 自动化单元测试：验证 Supervisor 路由状态机、研究团队质检打回与防死循环熔断。"""

import pytest
from src.day43_multi_agent_patterns import (
    FINISH,
    RouteDecision,
    SupervisorOrchestrator,
)
from src.day43_research_team import build_research_team


def test_research_team_full_collaboration_with_revision():
    team = build_research_team(max_rounds=8)
    res = team.invoke({"topic": "企业级Agent"})
    assert res.completed is True
    assert res.truncated is False
    assert res.rounds == 5
    routed_order = [item["next_agent"] for item in res.routing_history]
    assert routed_order == ["researcher", "analyst", "writer", "writer", FINISH]
    assert res.final_state["writer_revisions"] == 2
    assert "风险提示" in res.final_state["draft"]
    assert res.final_state["analysis"]["verdict"] == "高速扩张期"


def test_supervisor_truncates_on_ping_pong_loop():
    class DummyWorker:
        name = "loop_worker"
        role_desc = "测试死循环"
        allowed_tools = []

        def run(self, state, feedback=""):
            return {"count": state.get("count", 0) + 1}

    orch = SupervisorOrchestrator(
        router_fn=lambda _s, _w: RouteDecision(next_agent="loop_worker", reason="永远打回"),
        max_rounds=3,
    )
    orch.register_worker(DummyWorker())
    res = orch.invoke({})
    assert res.completed is False
    assert res.truncated is True
    assert res.rounds == 3
    assert res.final_state["count"] == 3


def test_supervisor_rejects_unknown_worker_route():
    orch = SupervisorOrchestrator(
        router_fn=lambda _s, _w: RouteDecision(next_agent="ghost_agent", reason="幻觉角色"),
        max_rounds=3,
    )
    with pytest.raises(ValueError, match="路由目标非法"):
        orch.invoke({})

