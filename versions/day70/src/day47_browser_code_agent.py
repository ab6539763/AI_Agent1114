"""Day 47 - 步骤二：浏览器 DOM 压缩规划器与代码助手 Unified Diff 补丁验证原型。"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class DOMElement:
    elem_id: int
    tag: str
    role: str
    text: str
    visible: bool = True
    interactive: bool = False


class BrowserDOMPlanner:
    """浏览器自动化核心：将原始 DOM 压缩为紧凑可交互快照，再规划原子操作序列。"""

    def compress_dom(self, raw_nodes: List[DOMElement]) -> List[Dict[str, Any]]:
        """过滤不可见与纯装饰节点，只保留可交互元素，通常可削减 85%+ Token。"""
        return [
            {"id": n.elem_id, "tag": n.tag, "role": n.role, "label": n.text}
            for n in raw_nodes
            if n.visible and n.interactive
        ]

    def plan_actions(self, goal: str, compact_dom: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        actions: List[Dict[str, Any]] = []
        search_box = next((e for e in compact_dom if e["tag"] == "input"), None)
        submit_btn = next((e for e in compact_dom if e["tag"] == "button" and "查询" in e["label"]), None)
        if search_box:
            keyword = goal.replace("查询", "").strip() or "星辰智脑"
            actions.append({"action": "type", "target_id": search_box["id"], "value": keyword})
        if submit_btn:
            actions.append({"action": "click", "target_id": submit_btn["id"]})
        return actions


class CodingAssistantPrototype:
    """代码助手核心：最小化 Unified Diff 补丁生成与沙箱函数验证闭环。"""

    def generate_unified_diff(self, file_name: str, original: str, patched: str) -> str:
        diff_lines = difflib.unified_diff(
            original.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=f"a/{file_name}",
            tofile=f"b/{file_name}",
        )
        return "".join(diff_lines)

    def fix_zero_division_bug(self, source_code: str) -> Dict[str, Any]:
        """定位除零隐患并生成带防御判断的最小化补丁与 Unified Diff。"""
        buggy_line = "return total / count"
        fixed_line = "return total / count if count else 0.0"
        if buggy_line not in source_code:
            return {"changed": False, "patched_code": source_code, "diff": ""}

        patched = source_code.replace(buggy_line, fixed_line, 1)
        diff_text = self.generate_unified_diff("metrics.py", source_code, patched)
        return {"changed": True, "patched_code": patched, "diff": diff_text}


if __name__ == "__main__":
    raw_dom = [
        DOMElement(1, "div", "banner", "装饰横幅", visible=True, interactive=False),
        DOMElement(2, "input", "textbox", "输入客户名称", visible=True, interactive=True),
        DOMElement(3, "button", "button", "查询客户", visible=True, interactive=True),
        DOMElement(4, "button", "button", "隐藏导出", visible=False, interactive=True),
    ]
    planner = BrowserDOMPlanner()
    compact = planner.compress_dom(raw_dom)
    print("压缩后 DOM 元素数:", len(compact), "| 规划动作:", planner.plan_actions("查询 华东客户", compact))

    buggy_src = "def avg_order(total: float, count: int) -> float:\n    return total / count\n"
    coder = CodingAssistantPrototype()
    fix = coder.fix_zero_division_bug(buggy_src)
    print("代码助手生成 Diff:\n" + fix["diff"])

