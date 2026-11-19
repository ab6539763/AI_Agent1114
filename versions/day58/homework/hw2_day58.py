"""
Day 58 课后作业 2（企业实战）：企业实战：导出星辰智脑 v1.0 架构评审 Markdown 纪要
工单：STARMIND-058
"""

def render_review_md(project: str, approved: bool, milestones: dict[int, str]) -> str:
    status = "PASS（准予开发）" if approved else "REJECT（需整改）"
    rows = "\n".join(f"| Day {d} | {desc} |" for d, desc in sorted(milestones.items()))
    return f"# {project} 架构评审纪要\n\n- 评审结论：{status}\n\n| 日期 | 交付目标 |\n|---|---|\n{rows}\n"


print(render_review_md("星辰智脑 v1.0", True, {59: "底座搭建", 60: "混合RAG"}))

