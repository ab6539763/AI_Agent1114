"""
Day 17 课后作业 1（基础巩固）：Prompt 版本注册与 Diff 对比器
工单：STARMIND-017
"""

import difflib
from typing import Dict


class PromptVersionStore:
    """轻量级 Prompt 版本仓库与 Diff 对比工具。"""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, str]] = {}

    def register(self, scene_id: str, version: str, content: str) -> None:
        self._store.setdefault(scene_id, {})[version] = content

    def get(self, scene_id: str, version: str) -> str:
        return self._store[scene_id][version]

    def diff(self, scene_id: str, v1: str, v2: str) -> str:
        t1 = self.get(scene_id, v1).splitlines(keepends=True)
        t2 = self.get(scene_id, v2).splitlines(keepends=True)
        return "".join(difflib.unified_diff(t1, t2, fromfile=v1, tofile=v2))


if __name__ == "__main__":
    store = PromptVersionStore()
    store.register("customer_qa", "v1.0", "你是客服，请回答问题。")
    store.register("customer_qa", "v1.1", "你是星辰数科资深客服，请用JSON格式回答问题。")
    print(store.diff("customer_qa", "v1.0", "v1.1"))

