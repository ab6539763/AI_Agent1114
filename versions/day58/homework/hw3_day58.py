"""
Day 58 课后作业 3（架构进阶）：架构进阶：定义毕业设计跨模块统一 Pydantic 数据契约
工单：STARMIND-058
"""

from typing import List
from pydantic import BaseModel, Field


class CitationItem(BaseModel):
    doc_id: str
    title: str
    score: float = Field(ge=0.0, le=1.0)
    snippet: str


class AgentResponse(BaseModel):
    trace_id: str
    answer: str
    citations: List[CitationItem] = Field(default_factory=list)
    token_cost_cny: float = Field(ge=0.0)


resp = AgentResponse(
    trace_id="tr-001",
    answer="详见星辰报销规范 [DOC-01]。",
    citations=[CitationItem(doc_id="DOC-01", title="报销制度", score=0.92, snippet="差旅补贴标准...")],
    token_cost_cny=0.004,
)
print(resp.model_dump_json(ensure_ascii=False))

