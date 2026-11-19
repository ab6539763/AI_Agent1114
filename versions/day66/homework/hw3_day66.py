"""
Day 66 课后作业 3（架构进阶）：架构进阶：生成个人技术博客/作品集索引页（Portfolio Index JSON）
工单：STARMIND-066
"""

def group_portfolio_projects(projects: list[dict]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for p in projects:
        grouped.setdefault(p["category"], []).append(p["name"])
    return grouped


out = group_portfolio_projects([
    {"name": "StarMind", "category": "Agent/RAG"},
    {"name": "LoRA-Eval-Gate", "category": "FineTuning"},
    {"name": "MCP-Gateway", "category": "Agent/RAG"},
])
assert out["Agent/RAG"] == ["StarMind", "MCP-Gateway"]
print("作品集分类索引通过:", out)

