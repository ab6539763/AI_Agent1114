"""
Day 40 课后作业 3（架构进阶）：实现动态工具权限过滤（RBAC）
工单：STARMIND-040
"""

"""Day 40 作业 3 参考答案：基于 RBAC 的工具动态裁剪与二次鉴权。"""

from typing import Dict, List, Set


class ToolPermissionFilter:
    ROLE_PERMISSIONS: Dict[str, Set[str]] = {
        "intern": {"knowledge_search"},
        "engineer": {"knowledge_search", "sandbox_python_calc", "safe_read_file", "safe_write_file"},
    }

    def filter_tool_names(self, role: str, all_tools: List[str]) -> List[str]:
        allowed = self.ROLE_PERMISSIONS.get(role, set())
        return [name for name in all_tools if name in allowed]

    def authorize(self, role: str, tool_name: str) -> bool:
        return tool_name in self.ROLE_PERMISSIONS.get(role, set())


if __name__ == "__main__":
    f = ToolPermissionFilter()
    all_t = ["knowledge_search", "safe_write_file"]
    assert f.filter_tool_names("intern", all_t) == ["knowledge_search"]
    assert f.authorize("intern", "safe_write_file") is False
    assert f.authorize("engineer", "safe_write_file") is True
    print("RBAC 工具鉴权验证通过")

