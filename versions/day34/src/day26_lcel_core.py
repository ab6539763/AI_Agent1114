"""
Day 26 - 步骤一：LCEL 核心 Runnable 协议深度实现
对应生产包：langchain_core.runnables
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Generic, Iterator, List, Mapping, Sequence, TypeVar, Union

Input = TypeVar("Input")
Output = TypeVar("Output")


def coerce_to_runnable(thing: Any) -> "Runnable[Any, Any]":
    """将普通函数或字典自动转换为 Runnable，支撑 LCEL 优雅语法糖。"""
    if isinstance(thing, Runnable):
        return thing
    if isinstance(thing, Mapping):
        return RunnableParallel(dict(thing))
    if callable(thing):
        return RunnableLambda(thing)
    raise TypeError(f"无法将类型 {type(thing).__name__} 转换为 Runnable")


class Runnable(ABC, Generic[Input, Output]):
    """LCEL 统一协议抽象基类，支持 | 管道串联与 invoke/batch/stream。"""

    @abstractmethod
    def invoke(self, input_data: Input) -> Output:
        """同步执行单条输入。"""

    def batch(self, inputs: Sequence[Input], max_workers: int = 4) -> List[Output]:
        """并发批处理，默认使用线程池保持返回顺序一致。"""
        if not inputs:
            return []
        with ThreadPoolExecutor(max_workers=min(max_workers, len(inputs))) as pool:
            return list(pool.map(self.invoke, inputs))

    def stream(self, input_data: Input) -> Iterator[Any]:
        """默认流式实现：若结果是字符串则按块吐出，否则产出完整结果。"""
        result = self.invoke(input_data)
        if isinstance(result, str):
            chunk_size = 8
            for i in range(0, len(result), chunk_size):
                yield result[i : i + chunk_size]
        else:
            yield result

    def __or__(self, other: Any) -> "RunnableSequence":
        """支持 self | other，自动扁平化嵌套 Sequence。"""
        right = coerce_to_runnable(other)
        left_steps = self.steps if isinstance(self, RunnableSequence) else [self]
        right_steps = right.steps if isinstance(right, RunnableSequence) else [right]
        return RunnableSequence(left_steps + right_steps)

    def __ror__(self, other: Any) -> "RunnableSequence":
        """支持 func | self 或 {'k': ...} | self。"""
        left = coerce_to_runnable(other)
        return left | self


class RunnableSequence(Runnable[Any, Any]):
    """顺序执行管道：将前一步的输出作为后一步的输入。"""

    def __init__(self, steps: Sequence[Runnable[Any, Any]]) -> None:
        if len(steps) < 2:
            raise ValueError("RunnableSequence 至少需要 2 个步骤")
        self.steps: List[Runnable[Any, Any]] = list(steps)

    def invoke(self, input_data: Any) -> Any:
        current = input_data
        for step in self.steps:
            current = step.invoke(current)
        return current

    def stream(self, input_data: Any) -> Iterator[Any]:
        """前面步骤依次 invoke，最后一个步骤走 stream 实现真流式输出。"""
        current = input_data
        for step in self.steps[:-1]:
            current = step.invoke(current)
        yield from self.steps[-1].stream(current)


class RunnableLambda(Runnable[Input, Output]):
    """将任意 Python 函数包装为 Runnable 节点。"""

    def __init__(self, func: Callable[[Input], Output]) -> None:
        self.func = func

    def invoke(self, input_data: Input) -> Output:
        return self.func(input_data)


class RunnablePassthrough(Runnable[Input, Input]):
    """原样透传输入；其 assign() 工厂可在保留原字典的同时追加新计算字段。"""

    def invoke(self, input_data: Input) -> Input:
        return input_data

    @staticmethod
    def assign(**kwargs: Any) -> "RunnableAssign":
        return RunnableAssign(RunnableParallel(kwargs))


class RunnableParallel(Runnable[Any, Dict[str, Any]]):
    """并行分支节点：使用线程池同时运行多个子链，合并为字典返回。"""

    def __init__(self, steps: Dict[str, Any]) -> None:
        self.steps: Dict[str, Runnable[Any, Any]] = {
            k: coerce_to_runnable(v) for k, v in steps.items()
        }

    def invoke(self, input_data: Any) -> Dict[str, Any]:
        if not self.steps:
            return {}
        results: Dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=len(self.steps)) as pool:
            future_map = {
                key: pool.submit(runnable.invoke, input_data)
                for key, runnable in self.steps.items()
            }
            for key, fut in future_map.items():
                results[key] = fut.result()
        return results


class RunnableAssign(Runnable[Dict[str, Any], Dict[str, Any]]):
    """在原字典基础上合并新字段（不修改原字典，保证无副作用）。"""

    def __init__(self, mapper: RunnableParallel) -> None:
        self.mapper = mapper

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(input_data, dict):
            raise TypeError("RunnablePassthrough.assign 要求上游输入必须为 dict")
        added = self.mapper.invoke(input_data)
        return {**input_data, **added}


if __name__ == "__main__":
    # 演示：普通函数 + 字典并行 + 管道符组合
    clean = RunnableLambda(lambda s: s.strip())
    pipeline = (
        clean
        | {
            "upper": lambda s: s.upper(),
            "length": lambda s: len(s),
            "raw": RunnablePassthrough(),
        }
        | RunnablePassthrough.assign(tag=lambda d: "LONG" if d["length"] > 10 else "SHORT")
    )
    print("单条 invoke:", pipeline.invoke("  StarMind LCEL Engine  "))
    print("批量 batch:", pipeline.batch(["  hi ", "  LangChain LCEL  "]))

