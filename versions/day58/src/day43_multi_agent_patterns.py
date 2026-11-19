"""Day 43 - 步骤一：通用 Supervisor 多 Agent 路由状态机与上下文隔离底座。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol

FINISH = "FINISH"


class WorkerAgent(Protocol):
    """专家 Agent 统一协议：只读取裁剪后的上下文视图，返回结构化状态补丁。"""

    name: str
    role_desc: str
    allowed_tools: List[str]

    def run(self, state: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
        ...


@dataclass
class RouteDecision:
    next_agent: str
    reason: str
    feedback: str = ""


@dataclass
class MultiAgentResult:
    final_state: Dict[str, Any]
    routing_history: List[Dict[str, Any]] = field(default_factory=list)
    completed: bool = True
    truncated: bool = False
    rounds: int = 0


class SupervisorOrchestrator:
    """
    Supervisor 集中式多 Agent 编排器：
    - 维护共享黑板状态 (Blackboard State)
    - 每轮由 router_fn 决定派发给哪位专家或 FINISH
    - 内置路由白名单校验与 max_rounds 防踢皮球熔断
    """

    def __init__(
        self,
        router_fn: Callable[[Dict[str, Any], List[str]], RouteDecision],
        max_rounds: int = 8,
    ) -> None:
        self.router_fn = router_fn
        self.max_rounds = max_rounds
        self._workers: Dict[str, WorkerAgent] = {}

    def register_worker(self, worker: WorkerAgent) -> "SupervisorOrchestrator":
        if worker.name == FINISH:
            raise ValueError("专家名称不能与保留关键字 FINISH 冲突")
        self._workers[worker.name] = worker
        return self

    @property
    def worker_names(self) -> List[str]:
        return list(self._workers.keys())

    def invoke(self, initial_state: Dict[str, Any]) -> MultiAgentResult:
        state: Dict[str, Any] = dict(initial_state)
        history: List[Dict[str, Any]] = []

        for round_no in range(1, self.max_rounds + 1):
            decision = self.router_fn(state, self.worker_names)
            history.append(
                {
                    "round": round_no,
                    "next_agent": decision.next_agent,
                    "reason": decision.reason,
                    "feedback": decision.feedback,
                }
            )

            if decision.next_agent == FINISH:
                return MultiAgentResult(
                    final_state=state,
                    routing_history=history,
                    completed=True,
                    truncated=False,
                    rounds=round_no,
                )

            if decision.next_agent not in self._workers:
                raise ValueError(
                    f"Supervisor 路由目标非法: '{decision.next_agent}'，合法专家: {self.worker_names}"
                )

            worker = self._workers[decision.next_agent]
            patch = worker.run(state, feedback=decision.feedback)
            state.update(patch)

        # 超出最大轮次，触发防踢皮球安全熔断
        return MultiAgentResult(
            final_state=state,
            routing_history=history,
            completed=False,
            truncated=True,
            rounds=self.max_rounds,
        )


if __name__ == "__main__":
    class EchoWorker:
        def __init__(self, name: str, role_desc: str, allowed_tools: List[str]) -> None:
            self.name = name
            self.role_desc = role_desc
            self.allowed_tools = allowed_tools

        def run(self, state: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
            done = list(state.get("done", []))
            done.append(f"{self.name}:{feedback or 'ok'}")
            return {"done": done}

    def demo_router(state: Dict[str, Any], workers: List[str]) -> RouteDecision:
        done = state.get("done", [])
        if len(done) == 0:
            return RouteDecision(next_agent=workers[0], reason="先执行第一步采集")
        return RouteDecision(next_agent=FINISH, reason="采集已完成，结束流程")

    orch = SupervisorOrchestrator(router_fn=demo_router, max_rounds=4)
    orch.register_worker(EchoWorker("collector", "采集员", ["search"]))
    res = orch.invoke({"topic": "AI Agent 行业趋势"})
    print("完成状态:", res.completed, "| 轮次:", res.rounds, "| 轨迹:", res.routing_history)

