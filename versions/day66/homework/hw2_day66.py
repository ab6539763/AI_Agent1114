"""
Day 66 课后作业 2（企业实战）：企业实战：批量体检整份简历并按得分从低到高输出待优化列表
工单：STARMIND-066
"""

from src.day66_star_resume_builder import lint_resume_bullet

bullets = [
    "主导设计 BM25+Rerank+Ragas RAG 流水线，将召回率由 60% 提升至 90%，Token 成本降 50%。",
    "负责日常接口维护与文档整理。",
]
ranked = sorted([(b, lint_resume_bullet(b)["score"]) for b in bullets], key=lambda x: x[1])
assert ranked[0][1] < ranked[1][1]
print("最急需改写条目:", ranked[0])

