"""
Day 66 - 模块二：高转化率 GitHub 作品集 README 自动生成器
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ProjectPortfolioSpec:
    project_name: str
    tagline: str
    tech_stack: List[str]
    highlights: List[str]
    benchmarks: Dict[str, str]
    quickstart_cmd: str


def generate_github_readme(spec: ProjectPortfolioSpec) -> str:
    badges = " ".join(f"`{t}`" for t in spec.tech_stack)
    hl_lines = "\n".join(f"- {h}" for h in spec.highlights)
    bm_rows = "\n".join(f"| {k} | {v} |" for k, v in spec.benchmarks.items())
    return (
        f"# {spec.project_name}\n\n"
        f"> {spec.tagline}\n\n"
        f"**核心技术栈**: {badges}\n\n"
        "## 核心工程亮点\n"
        f"{hl_lines}\n\n"
        "## 量化评测与压测指标 (Benchmarks)\n"
        "| 评估维度 | 实测指标 |\n"
        "| --- | --- |\n"
        f"{bm_rows}\n\n"
        "## 一键本地运行与验收\n"
        "```bash\n"
        f"{spec.quickstart_cmd}\n"
        "```\n"
    )


if __name__ == "__main__":
    spec = ProjectPortfolioSpec(
        project_name="StarMind 星辰智脑 - 企业级 RAG & 多 Agent 平台",
        tagline="面向企业知识问答与高危审批自动化的生产级 AI Agent 全栈系统",
        tech_stack=["Python 3.11", "FastAPI", "SSE", "Hybrid RAG + Rerank", "Multi-Agent + HITL", "Docker"],
        highlights=[
            "混合检索四段式流水线（BM25 + 语义向量 + RRF + Rerank），支持强制 `[DOC-xx]` 溯源与低分拒答",
            "多 Agent 编排 + MCP 工具注册 + 金额超限 HITL 人工审批幂等闭环",
            "内置 Ragas 四维质量门禁、异步并发压测与语义缓存/7B 分级降本引擎",
        ],
        benchmarks={
            "Ragas Faithfulness (忠实度)": "92.4%",
            "Ragas Context Recall (召回率)": "91.0%",
            "并发压测 P95 延迟": "185ms (错误率 0.0%)",
            "Token 综合成本优化": "直降 54.0%",
        },
        quickstart_cmd="pytest -q && uvicorn src.day62_api_server:app --reload",
    )
    print(generate_github_readme(spec))

