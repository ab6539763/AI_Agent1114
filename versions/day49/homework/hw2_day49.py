"""
Day 49 课后作业 2（企业实战）：为 /confirm 接口增加审批人角色权限校验
工单：STARMIND-049
"""

"""Day 49 作业 2 参考答案：高危动作审批人 RBAC 权限校验。"""

from typing import Dict, Set

ACTION_APPROVER_ROLES: Dict[str, Set[str]] = {
    "SUBMIT_EXPENSE": {"director", "finance"},
    "SEND_EMAIL": {"employee", "manager", "director"},
}


def can_approve(action_type: str, reviewer_role: str) -> bool:
    return reviewer_role in ACTION_APPROVER_ROLES.get(action_type, set())


if __name__ == "__main__":
    assert can_approve("SUBMIT_EXPENSE", "employee") is False
    assert can_approve("SUBMIT_EXPENSE", "director") is True
    assert can_approve("SEND_EMAIL", "employee") is True
    print("审批人权限校验通过")

