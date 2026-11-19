"""
Day 62 课后作业 2（企业实战）：企业实战：给审批工作台增加待审批列表查询接口
工单：STARMIND-062
"""

def list_pending_tickets(tickets: dict) -> list[dict]:
    pending = [t for t in tickets.values() if t["status"] == "PENDING"]
    return sorted(pending, key=lambda x: x["amount"], reverse=True)


sample = {
    "T1": {"ticket_id": "T1", "amount": 3000, "status": "PENDING"},
    "T2": {"ticket_id": "T2", "amount": 9000, "status": "PENDING"},
    "T3": {"ticket_id": "T3", "amount": 5000, "status": "REJECTED"},
}
res = list_pending_tickets(sample)
assert [x["ticket_id"] for x in res] == ["T2", "T1"]
print("待审批高额优先队列通过:", res)

