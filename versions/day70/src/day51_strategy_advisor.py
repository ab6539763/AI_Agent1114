"""
Day 51 - 模块一：微调 vs RAG vs Prompt 企业选型决策引擎
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ScenarioProfile:
    """企业业务场景画像"""
    name: str
    knowledge_update_freq: str  # "realtime" | "weekly" | "static"
    style_strictness: int       # 1(宽松) ~ 5(极严格话术/格式)
    labeled_samples: int        # 已有或可清洗的高质量样本条数
    need_private_deploy: bool   # 是否要求私有化部署/数据不出域
    cost_sensitivity: int       # 1(不敏感) ~ 5(极度关注推理成本)


@dataclass
class DecisionReport:
    """选型决策报告"""
    scenario_name: str
    primary_strategy: str
    secondary_strategy: str
    warnings: List[str] = field(default_factory=list)
    action_plan: List[str] = field(default_factory=list)


def advise_llm_strategy(profile: ScenarioProfile) -> DecisionReport:
    """根据业务画像输出大模型技术路线决策报告"""
    warnings: List[str] = []
    action_plan: List[str] = []

    needs_rag = profile.knowledge_update_freq in ("realtime", "weekly")
    needs_ft = (
        profile.style_strictness >= 4
        or (profile.need_private_deploy and profile.cost_sensitivity >= 4)
    )

    if needs_rag and needs_ft:
        primary = "RAG + LoRA 微调混合架构"
        secondary = "先上线 Prompt + RAG 验证业务闭环，再积累日志做 LoRA 微调"
        action_plan.append("阶段1：搭建混合检索 RAG 解决高频知识准确性")
        action_plan.append("阶段2：收集 500~2000 条线上高分对话，LoRA 微调 Qwen2.5-7B 固化话术与降本")
    elif needs_rag:
        primary = "RAG 检索增强 + 精调 Prompt"
        secondary = "暂不微调，避免知识过时导致频繁重训"
        action_plan.append("构建增量文档切分与向量/BM25混合检索链路")
        action_plan.append("通过 System Prompt 约束引用溯源与拒答机制")
    elif needs_ft:
        primary = "LoRA / QLoRA 垂直领域微调"
        secondary = "若样本不足 300 条，先用大模型 Self-Instruct 合成并人工抽检"
        action_plan.append("清洗并构建 Alpaca/ShareGPT 格式领域数据集")
        action_plan.append("使用 LLaMA-Factory 在单卡 4090 上进行 Qwen2.5-7B LoRA 微调")
    else:
        primary = "Prompt Engineering + Few-Shot"
        secondary = "直接调用国产高性价比 API（DeepSeek / 通义千问）"
        action_plan.append("编写结构化提示词与 3~5 组高质量 Few-Shot 示例")
        action_plan.append("建立自动化评估集，确认基线达标后再考虑工程优化")

    # 风险预警校验
    if needs_ft and profile.labeled_samples < 300:
        warnings.append(
            f"当前标注样本仅 {profile.labeled_samples} 条，低于微调建议起步线(500条)，"
            "强行微调极易过拟合，请先扩充或合成高质量语料。"
        )
    if profile.knowledge_update_freq == "realtime" and needs_ft:
        warnings.append(
            "检测到实时知识更新诉求：切勿将实时变动事实（如价格、库存）写死在微调数据中，必须交给 RAG。"
        )

    return DecisionReport(
        scenario_name=profile.name,
        primary_strategy=primary,
        secondary_strategy=secondary,
        warnings=warnings,
        action_plan=action_plan,
    )


if __name__ == "__main__":
    cases = [
        ScenarioProfile("星辰政企智能客服", "weekly", 5, 800, True, 5),
        ScenarioProfile("每日促销政策问答", "realtime", 2, 120, False, 3),
        ScenarioProfile("内部邮件润色助手", "static", 2, 50, False, 2),
    ]
    for c in cases:
        rep = advise_llm_strategy(c)
        print(f"=== {rep.scenario_name} ===")
        print(f"主推方案: {rep.primary_strategy}")
        print(f"备选建议: {rep.secondary_strategy}")
        if rep.warnings:
            print(f"风险预警: {rep.warnings}")
        print(f"落地步骤: {rep.action_plan}\n")

