"""
Day 61 课后作业 1（基础巩固）：基础巩固：为 MCPToolRegistry 增加按风险等级查询工具列表
工单：STARMIND-061
"""

from src.day61_multi_agent_hitl import StarMindMultiAgent

app = StarMindMultiAgent()
samples = {
    "rag_search": {"query": "住宿"},
    "submit_expense": {"employee": "小李", "amount": 5000, "reason": "采购"},
}
high_risk = [
    name for name, args in samples.items()
    if app.registry.validate_and_check_risk(name, args)
]
assert high_risk == ["submit_expense"]
print("高危工具识别通过:", high_risk)

