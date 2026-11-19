"""Day 41 - 步骤一：轻量级 LangGraph 语义 StateGraph 引擎与 Mermaid/ASCII 可视化。"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

START = "__start__"
END = "__end__"

NodeFunc = Callable[[Dict[str, Any]], Dict[str, Any]]
RouterFunc = Callable[[Dict[str, Any]], str]
ReducerFunc = Callable[[Any, Any], Any]


@dataclass
class CompiledGraph:
    """编译后的可执行状态图对象。"""

    nodes: Dict[str, NodeFunc]
    edges: Dict[str, str]
    conditional_edges: Dict[str, Tuple[RouterFunc, Dict[str, str]]]
    reducers: Dict[str, ReducerFunc]

    def _merge_state(self, state: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
        """按字段 Reducer 合并节点返回的局部更新补丁。"""
        merged = copy.deepcopy(state)
        for key, value in update.items():
            if key in self.reducers and key in merged:
                merged[key] = self.reducers[key](merged[key], value)
            else:
                merged[key] = value
        return merged

    def invoke(self, initial_state: Dict[str, Any], max_steps: int = 15) -> Dict[str, Any]:
        """从 START 节点启动图执行，直至抵达 END 或触发最大步数保护。"""
        state = copy.deepcopy(initial_state)
        state.setdefault("_visited_nodes", [])
        current = self._next_node(START, state)
        steps = 0

        while current != END:
            steps += 1
            if steps > max_steps:
                raise RuntimeError(f"状态图超过最大步数上限 ({max_steps})，疑似陷入循环")

            node_fn = self.nodes[current]
            update = node_fn(copy.deepcopy(state))
            if not isinstance(update, dict):
                raise TypeError(f"节点 '{current}' 必须返回 dict 状态补丁，实际返回 {type(update).__name__}")
            state = self._merge_state(state, update)
            state["_visited_nodes"].append(current)
            current = self._next_node(current, state)

        return state

    def _next_node(self, current: str, state: Dict[str, Any]) -> str:
        if current in self.conditional_edges:
            router_fn, path_map = self.conditional_edges[current]
            route_key = router_fn(state)
            if route_key not in path_map:
                raise ValueError(f"节点 '{current}' 路由返回未知分支 '{route_key}'，合法值: {list(path_map.keys())}")
            return path_map[route_key]
        if current in self.edges:
            return self.edges[current]
        raise ValueError(f"节点 '{current}' 未配置任何出边，无法继续流转")

    def draw_mermaid(self) -> str:
        """导出标准 Mermaid flowchart TD 文本，可直接贴入文档或前端渲染。"""
        lines = ["graph TD"]
        for src, dst in self.edges.items():
            lines.append(f"    {src} --> {dst}")
        for src, (_, path_map) in self.conditional_edges.items():
            for cond_label, dst in path_map.items():
                lines.append(f"    {src} -. {cond_label} .-> {dst}")
        return "\n".join(lines)

    def draw_ascii(self) -> str:
        """导出简洁的 ASCII 拓扑结构图，便于终端调试与日志查看。"""
        lines = ["+--- StateGraph Topology ---+"]
        for src, dst in self.edges.items():
            lines.append(f"| [{src}] ===> [{dst}]")
        for src, (_, path_map) in self.conditional_edges.items():
            for cond_label, dst in path_map.items():
                lines.append(f"| [{src}] --({cond_label})--> [{dst}]")
        lines.append("+---------------------------+")
        return "\n".join(lines)


class StateGraph:
    """对齐 LangGraph StateGraph 的构建器 API。"""

    def __init__(self, reducers: Optional[Dict[str, ReducerFunc]] = None) -> None:
        self._nodes: Dict[str, NodeFunc] = {}
        self._edges: Dict[str, str] = {}
        self._conditional_edges: Dict[str, Tuple[RouterFunc, Dict[str, str]]] = {}
        self._reducers: Dict[str, ReducerFunc] = reducers or {}

    def add_node(self, name: str, func: NodeFunc) -> "StateGraph":
        if name in (START, END):
            raise ValueError(f"禁止使用保留节点名: {name}")
        self._nodes[name] = func
        return self

    def add_edge(self, src: str, dst: str) -> "StateGraph":
        self._edges[src] = dst
        return self

    def add_conditional_edges(
        self,
        src: str,
        router_fn: RouterFunc,
        path_map: Dict[str, str],
    ) -> "StateGraph":
        self._conditional_edges[src] = (router_fn, path_map)
        return self

    def compile(self) -> CompiledGraph:
        """编译期拓扑完整性校验。"""
        valid_targets: Set[str] = set(self._nodes.keys()) | {END}
        valid_sources: Set[str] = set(self._nodes.keys()) | {START}

        if START not in self._edges and START not in self._conditional_edges:
            raise ValueError("状态图必须配置从 START 出发的入口边")

        for src, dst in self._edges.items():
            if src not in valid_sources or dst not in valid_targets:
                raise ValueError(f"非法普通边: {src} -> {dst}")

        for src, (_, path_map) in self._conditional_edges.items():
            if src not in valid_sources:
                raise ValueError(f"非法条件边起点: {src}")
            for dst in path_map.values():
                if dst not in valid_targets:
                    raise ValueError(f"非法条件边终点: {src} -> {dst}")

        return CompiledGraph(
            nodes=dict(self._nodes),
            edges=dict(self._edges),
            conditional_edges=dict(self._conditional_edges),
            reducers=dict(self._reducers),
        )


if __name__ == "__main__":
    g = StateGraph(reducers={"logs": lambda old, new: old + new})
    g.add_node("step_a", lambda s: {"logs": ["A完成"], "val": s["val"] + 1})
    g.add_node("step_b", lambda s: {"logs": ["B完成"], "val": s["val"] * 10})
    g.add_edge(START, "step_a")
    g.add_edge("step_a", "step_b")
    g.add_edge("step_b", END)
    app = g.compile()
    print(app.draw_ascii())
    print("运行结果:", app.invoke({"val": 2, "logs": []}))

