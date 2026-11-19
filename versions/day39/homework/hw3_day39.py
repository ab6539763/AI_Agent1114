"""
Day 39 课后作业 3（架构进阶）：实现“连续重复动作”提前熔断器
工单：STARMIND-039
"""

"""Day 39 作业 3 参考答案：ReAct 重复动作熔断器。"""

from typing import List, Tuple


class LoopGuard:
    """检测并拦截 Agent 连续重复调用同一工具与参数的死循环。"""

    def __init__(self, max_consecutive_repeats: int = 2) -> None:
        self.max_consecutive_repeats = max_consecutive_repeats
        self._history: List[Tuple[str, str]] = []

    def check_and_record(self, action: str, action_input: str) -> tuple[bool, str]:
        sig = (action.strip(), action_input.strip())
        self._history.append(sig)
        if len(self._history) >= self.max_consecutive_repeats:
            recent = self._history[-self.max_consecutive_repeats :]
            if all(item == sig for item in recent):
                return (
                    False,
                    f"熔断拦截：检测到连续 {self.max_consecutive_repeats} 次重复调用 "
                    f"{sig[0]}({sig[1]})，请更换策略或直接总结已有信息输出 Final Answer。",
                )
        return True, "OK"


if __name__ == "__main__":
    guard = LoopGuard(max_consecutive_repeats=2)
    assert guard.check_and_record("internal_search", "上海")[0] is True
    ok, msg = guard.check_and_record("internal_search", "上海")
    print("第二次相同调用:", ok, msg)
    assert ok is False and "熔断拦截" in msg

