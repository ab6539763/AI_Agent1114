"""
Day 43 课后作业 3（架构进阶）：按角色生成最小化上下文视图（Context Projection）
工单：STARMIND-043
"""

"""Day 43 作业 3 参考答案：多 Agent 最小化上下文视图投影。"""

from typing import Any, Dict, Set

ROLE_FIELDS: Dict[str, Set[str]] = {
    "researcher": {"topic"},
    "analyst": {"topic", "facts"},
    "writer": {"topic", "analysis", "writer_revisions"},
}


def project_context(state: Dict[str, Any], role: str) -> Dict[str, Any]:
    allowed = ROLE_FIELDS.get(role, set())
    return {k: v for k, v in state.items() if k in allowed}


if __name__ == "__main__":
    full_state = {"topic": "企业级Agent", "facts": [1, 2], "raw_html": "<html>超长噪音</html>", "analysis": {"ok": True}}
    w_view = project_context(full_state, "writer")
    print("Writer 视图:", w_view)
    assert "raw_html" not in w_view and "facts" not in w_view and "analysis" in w_view

