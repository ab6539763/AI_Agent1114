"""
Day 61 课后作业 3（架构进阶）：架构进阶：实现多级审批链（2000~10000 元经理批，>10000 元总监批）
工单：STARMIND-061
"""

def required_approvers(amount: float) -> list[str]:
    if amount <= 2000:
        return []
    if amount <= 10000:
        return ["dept_manager"]
    return ["dept_manager", "vp_finance"]


assert required_approvers(1500) == []
assert required_approvers(6000) == ["dept_manager"]
assert required_approvers(25000) == ["dept_manager", "vp_finance"]
print("多级审批链路由通过")

