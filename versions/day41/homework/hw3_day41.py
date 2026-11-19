"""
Day 41 课后作业 3（架构进阶）：为 StateGraph 增加图可达性静态检测（发现孤岛节点）
工单：STARMIND-041
"""

"""Day 41 作业 3 参考答案：BFS 静态检测状态图孤岛节点。"""

from collections import deque
from typing import Dict, Set


def find_unreachable_nodes(
    node_names: Set[str],
    edges: Dict[str, str],
    cond_edges: Dict[str, Dict[str, str]],
) -> Set[str]:
    adj: Dict[str, Set[str]] = {}
    for src, dst in edges.items():
        adj.setdefault(src, set()).add(dst)
    for src, pmap in cond_edges.items():
        adj.setdefault(src, set()).update(pmap.values())

    visited: Set[str] = set()
    q = deque(["__start__"])
    while q:
        cur = q.popleft()
        for nxt in adj.get(cur, set()):
            if nxt not in visited:
                visited.add(nxt)
                q.append(nxt)
    return node_names - visited


if __name__ == "__main__":
    orphans = find_unreachable_nodes(
        node_names={"a", "b", "dead_node"},
        edges={"__start__": "a", "a": "b", "b": "__end__"},
        cond_edges={},
    )
    print("发现孤岛节点:", orphans)
    assert orphans == {"dead_node"}

