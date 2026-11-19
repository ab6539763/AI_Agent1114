"""
Day 70 - 模块一：多模态 Agent + MCP 能力路由原型与高级 AI 工程师 12 个月成长路线图
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MultimodalRequest:
    modality: str  # text | image | audio
    intent: str    # qa | invoice_ocr | voice_assistant | gui_action
    payload_summary: str


@dataclass
class MultimodalPlan:
    modality: str
    pipeline_steps: List[str]
    mcp_servers: List[str]


def route_multimodal_agent(req: MultimodalRequest) -> MultimodalPlan:
    """根据输入模态与意图编排下一代多模态 Agent + MCP 执行管线"""
    if req.modality == "image":
        if req.intent == "invoice_ocr":
            return MultimodalPlan(
                modality="image",
                pipeline_steps=["vlm_vision_parse", "schema_extract_json", "hitl_amount_check"],
                mcp_servers=["mcp-finance-erp", "mcp-approval-center"],
            )
        return MultimodalPlan(
            modality="image",
            pipeline_steps=["vlm_screen_grounding", "action_planner", "sandbox_gui_executor"],
            mcp_servers=["mcp-browser-playwright", "mcp-audit-logger"],
        )
    if req.modality == "audio":
        return MultimodalPlan(
            modality="audio",
            pipeline_steps=["streaming_asr", "hybrid_rag_agent", "low_latency_tts"],
            mcp_servers=["mcp-knowledge-base", "mcp-calendar-feishu"],
        )
    return MultimodalPlan(
        modality="text",
        pipeline_steps=["input_guardrail", "hybrid_rag_or_agent", "output_citation_check"],
        mcp_servers=["mcp-knowledge-base", "mcp-ticket-system"],
    )


def build_12month_roadmap(engineer_name: str, current_level: str = "AI 应用工程师") -> Dict[str, object]:
    quarters = [
        {"quarter": "Q1 (1-3月)", "theme": "生产稳定性与可观测性", "milestone": "主导线上 RAG/Agent 服务 SLA >= 99.9%，全链路 Trace 与告警完备"},
        {"quarter": "Q2 (4-6月)", "theme": "评测数据飞轮与 FinOps", "milestone": "搭建 Ragas + 人工反馈闭环，通过语义缓存与分级路由降低 50% 推理成本"},
        {"quarter": "Q3 (7-9月)", "theme": "模型微调与多模态深水区", "milestone": "落地 QLoRA 垂直小模型 + vLLM 高吞吐部署，拓展视觉/语音多模态 Agent"},
        {"quarter": "Q4 (10-12月)", "theme": "企业级 MCP 平台与技术影响力", "milestone": "沉淀公司级 MCP 工具中台与安全规范，完成向高级 AI 架构师跃迁"},
    ]
    return {
        "engineer": engineer_name,
        "from_level": current_level,
        "target_level": "高级 AI 工程师 / AI 架构师",
        "quarters": quarters,
    }


if __name__ == "__main__":
    p = route_multimodal_agent(MultimodalRequest("image", "invoice_ocr", "差旅电子专票截图.png"))
    print("多模态发票识别编排:", p)
    rm = build_12month_roadmap("星辰学员")
    print("12个月成长路线:", [q["quarter"] + " " + q["theme"] for q in rm["quarters"]])

