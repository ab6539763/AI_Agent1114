"""
Day 65 - 模块二：防翻车现场 Demo 编排器（实时主链路 + 确定性降级快照）
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List


@dataclass
class DemoStep:
    scene_name: str
    live_fn: Callable[[], str]
    fallback_snapshot: str
    expected_keyword: str


@dataclass
class DemoStepOutcome:
    scene_name: str
    mode: str  # LIVE | FALLBACK
    output: str
    passed: bool


def run_demo_rehearsal(steps: List[DemoStep]) -> List[DemoStepOutcome]:
    outcomes: List[DemoStepOutcome] = []
    for st in steps:
        try:
            out = st.live_fn()
            mode = "LIVE"
        except Exception:
            out = st.fallback_snapshot
            mode = "FALLBACK"
        passed = st.expected_keyword in out
        outcomes.append(DemoStepOutcome(st.scene_name, mode, out, passed))
    return outcomes


if __name__ == "__main__":
    demo_steps = [
        DemoStep(
            scene_name="场景1：专有错误码混合检索+引用溯源",
            live_fn=lambda: "ERR_4291 表示部门日Token配额已触发硬熔断。[DOC-02]",
            fallback_snapshot="[快照] ERR_4291 表示部门日Token配额已触发硬熔断。[DOC-02]",
            expected_keyword="[DOC-02]",
        ),
        DemoStep(
            scene_name="场景2：高危报销 HITL 人工审批挂起",
            live_fn=lambda: "金额 4500 元超过上限，已进入 PENDING_APPROVAL（APR-8821）",
            fallback_snapshot="[快照] 金额 4500 元超过上限，已进入 PENDING_APPROVAL（APR-8821）",
            expected_keyword="PENDING_APPROVAL",
        ),
        DemoStep(
            scene_name="场景3：越狱攻击安全护栏拦截",
            live_fn=lambda: "BLOCKED: 检测到 Prompt 注入攻击，已拒绝执行",
            fallback_snapshot="[快照] BLOCKED: 检测到 Prompt 注入攻击，已拒绝执行",
            expected_keyword="BLOCKED",
        ),
    ]
    for r in run_demo_rehearsal(demo_steps):
        print(f"[{r.mode}] {r.scene_name} -> passed={r.passed}")

