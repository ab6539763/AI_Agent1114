"""
Day 41 课后作业 1（基础巩固）：为采购工作流增加二级审批（超过 2 万元需 VP 复审）
工单：STARMIND-041
"""

"""Day 41 作业 1 参考答案：二级分级审批路由逻辑。"""

def route_after_director(state: dict) -> str:
    if not state.get("approved"):
        return "rejected"
    if state["total_amount"] > 20000:
        return "need_vp"
    return "approved"


if __name__ == "__main__":
    assert route_after_director({"approved": False, "total_amount": 30000}) == "rejected"
    assert route_after_director({"approved": True, "total_amount": 12000}) == "approved"
    assert route_after_director({"approved": True, "total_amount": 25000}) == "need_vp"
    print("二级审批条件边测试通过")

