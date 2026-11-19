"""
Day 26 课后作业 1（基础巩固）：作业一：实现带条件分支的 RunnableBranch 路由链
工单：STARMIND-026
"""

"""Day 26 作业一参考答案：条件路由 RunnableBranch"""
import sys
from pathlib import Path
from typing import Any, Callable, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day26_lcel_core import Runnable, coerce_to_runnable


class RunnableBranch(Runnable[Any, Any]):
    def __init__(
        self,
        branches: Sequence[Tuple[Callable[[Any], bool], Any]],
        default: Any,
    ) -> None:
        self.branches = [(cond, coerce_to_runnable(r)) for cond, r in branches]
        self.default = coerce_to_runnable(default)

    def invoke(self, input_data: Any) -> Any:
        for cond, runnable in self.branches:
            if cond(input_data):
                return runnable.invoke(input_data)
        return self.default.invoke(input_data)


if __name__ == "__main__":
    router = RunnableBranch(
        branches=[
            (lambda q: "报销" in q, lambda q: f"[财务链] 正在处理报销咨询：{q}"),
            (lambda q: "GitLab" in q or "报错" in q, lambda q: f"[研发链] 正在排查技术问题：{q}"),
        ],
        default=lambda q: f"[通用链] 已转交前台客服：{q}",
    )
    print(router.invoke("差旅报销发票怎么贴？"))
    print(router.invoke("GitLab CI 报错了"))
    assert router.invoke("报销").startswith("[财务链]")

