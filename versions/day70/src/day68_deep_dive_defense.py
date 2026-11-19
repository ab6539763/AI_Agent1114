"""
Day 68 - 模块二：应对'项目被问穿'的 5 层架构决策记录 (ADR) 生成与完整度校验器
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ArchitectureDecisionCard:
    topic: str
    l1_problem: str
    l2_alternatives: List[str]
    l3_pitfall_lesson: str
    l4_metric_proof: str
    l5_scale_10x_plan: str

    def to_markdown(self) -> str:
        alts = " / ".join(self.l2_alternatives)
        return (
            f"### ADR: {self.topic}\n"
            f"- **L1 痛点与目标**: {self.l1_problem}\n"
            f"- **L2 备选方案权衡**: {alts}\n"
            f"- **L3 真实踩坑与解法**: {self.l3_pitfall_lesson}\n"
            f"- **L4 量化指标实证**: {self.l4_metric_proof}\n"
            f"- **L5 十倍扩容演进**: {self.l5_scale_10x_plan}\n"
        )


def audit_adr_readiness(card: ArchitectureDecisionCard) -> Dict[str, object]:
    missing: List[str] = []
    if len(card.l1_problem.strip()) < 8:
        missing.append("L1 痛点描述过于空泛")
    if len(card.l2_alternatives) < 2:
        missing.append("L2 至少需对比 2 种备选技术方案及其取舍")
    if len(card.l3_pitfall_lesson.strip()) < 8:
        missing.append("L3 缺少真实踩坑排障细节，容易被面试官怀疑是纸上谈兵")
    if not any(ch.isdigit() for ch in card.l4_metric_proof):
        missing.append("L4 缺少量化指标数字支撑")
    if len(card.l5_scale_10x_plan.strip()) < 8:
        missing.append("L5 缺少流量或数据量扩大 10 倍后的演进预案")
    return {"ready": len(missing) == 0, "missing": missing}


if __name__ == "__main__":
    rag_adr = ArchitectureDecisionCard(
        topic="为什么采用 BM25 + 向量 + RRF 而不是单一向量检索？",
        l1_problem="企业制度包含大量专有错误码与编号，纯稠密向量召回率仅 62%。",
        l2_alternatives=["纯向量检索(同义强但专词差)", "线性加权融合(量纲难调参)", "RRF倒数秩融合(无量纲免调参)"],
        l3_pitfall_lesson="初期英文错误码被中文分词拆散，改为正则保留完整字母数字 token + 中文 2-gram 后精准命中。",
        l4_metric_proof="黄金集 Context Recall 由 62% 提升至 91%，检索 P95 保持在 35ms 内。",
        l5_scale_10x_plan="千万切片规模下切换 Milvus(SQ8量化) + ES 分布式分片，前置 RBAC 部门分区过滤。",
    )
    print("ADR 备战体检:", audit_adr_readiness(rag_adr))
    print(rag_adr.to_markdown())

