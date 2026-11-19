"""
Day 26 课后作业 2（企业实战）：作业二：实现高可用降级链 RunnableWithFallbacks
工单：STARMIND-026
"""

"""Day 26 作业二参考答案：生产级故障自动降级链"""
import sys
from pathlib import Path
from typing import Any, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day26_lcel_core import Runnable, coerce_to_runnable


class RunnableWithFallbacks(Runnable[Any, Any]):
    def __init__(self, primary: Any, fallbacks: Sequence[Any]) -> None:
        self.primary = coerce_to_runnable(primary)
        self.fallbacks: List[Runnable[Any, Any]] = [coerce_to_runnable(f) for f in fallbacks]

    def invoke(self, input_data: Any) -> Any:
        last_exc: Exception | None = None
        for idx, candidate in enumerate([self.primary, *self.fallbacks]):
            try:
                return candidate.invoke(input_data)
            except Exception as exc:
                last_exc = exc
                print(f"[Fallback] 候选链 #{idx} 失败: {exc}，自动切换下一候选...")
        assert last_exc is not None
        raise last_exc


if __name__ == "__main__":
    def broken_deepseek(_: str) -> str:
        raise TimeoutError("DeepSeek API 504 Gateway Timeout")

    chain = RunnableWithFallbacks(
        primary=broken_deepseek,
        fallbacks=[lambda q: f"[备用通义千问兜底回答] {q}"],
    )
    ans = chain.invoke("星辰数科年假规则")
    print("最终结果:", ans)
    assert "兜底回答" in ans

