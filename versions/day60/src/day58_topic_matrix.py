"""
Day 58 - 模块一：8 大 AI 应用毕业设计方向量化选题矩阵
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class CapstoneTopic:
    """毕业设计选题条目"""
    code: str
    name: str
    resume_value: int      # 简历含金量 1-10
    engineering_depth: int # 工程深度 1-10
    six_day_feasibility: int  # 6天可控度 1-10
    demo_impact: int       # 答辩视觉/业务冲击力 1-10
    core_stack: str


TOPICS_8: List[CapstoneTopic] = [
    CapstoneTopic("T1", "星辰智脑：企业级 RAG + 多Agent + MCP 综合平台", 10, 10, 9, 10, "FastAPI+LangGraph+HybridRAG+Docker"),
    CapstoneTopic("T2", "金融/政务合同智能审查与风控溯源系统", 9, 9, 8, 9, "HybridRAG+结构化抽取+合规护栏"),
    CapstoneTopic("T3", "企业级 NL2SQL 智能商业问数助手", 9, 9, 8, 9, "Schema检索+SQL沙箱+图表生成"),
    CapstoneTopic("T4", "垂直领域智能客服（LoRA微调+RAG混合架构）", 9, 8, 8, 8, "LLaMA-Factory+vLLM+RAG+熔断"),
    CapstoneTopic("T5", "GitLab 自动化 Code Review 与研发效能 Agent", 8, 9, 9, 8, "AST解析+MCP工具+多Agent协作"),
    CapstoneTopic("T6", "多模态研报/财报表格解析与投研问答引擎", 9, 9, 7, 9, "OCR/表格解析+父子分块+Rerank"),
    CapstoneTopic("T7", "跨境电商多语种合规选品与客服自动化平台", 8, 8, 8, 8, "多语种Prompt+工作流+记忆"),
    CapstoneTopic("T8", "个人数字分身与日程/邮件自动协同助理", 7, 7, 9, 8, "MCP生态+HITL审批+长短期记忆"),
]


def rank_capstone_topics(
    prefer_feasibility: bool = False,
) -> List[tuple[CapstoneTopic, float]]:
    """按综合加权得分对 8 大选题排序"""
    weights = (0.25, 0.20, 0.40, 0.15) if prefer_feasibility else (0.35, 0.25, 0.25, 0.15)
    scored = []
    for t in TOPICS_8:
        score = round(
            t.resume_value * weights[0]
            + t.engineering_depth * weights[1]
            + t.six_day_feasibility * weights[2]
            + t.demo_impact * weights[3],
            2,
        )
        scored.append((t, score))
    return sorted(scored, key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    for rank, (topic, sc) in enumerate(rank_capstone_topics(), start=1):
        print(f"Top{rank}: [{topic.code}] {topic.name} -> 综合分 {sc} ({topic.core_stack})")

