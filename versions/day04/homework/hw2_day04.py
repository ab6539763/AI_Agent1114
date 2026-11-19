"""
Day 04 课后作业 2（企业实战）：企业实战：多模型权限交集校验器
工单：STARMIND-004
"""

"""Day 4 课后题 2：AI 工具权限集合校验器。"""

from typing import Set, Tuple, List


def check_permissions(user_perms: Set[str], required_perms: Set[str]) -> Tuple[bool, List[str]]:
    """检查用户是否具备全部所需权限，返回 (是否通过, 缺失权限列表)。"""
    missing = sorted(required_perms - user_perms)
    return (len(missing) == 0, missing)


if __name__ == "__main__":
    print(check_permissions({"chat", "rag"}, {"rag", "export"}))
    print(check_permissions({"chat", "rag", "export"}, {"rag", "export"}))

