"""
Day 66 - 模块一：STAR 法则项目经历生成器与简历量化体检 Linter
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List

STRONG_VERBS = ("主导", "设计", "架构", "构建", "实现", "重构", "优化", "落地", "搭建")
WEAK_VERBS = ("负责", "参与", "协助", "了解", "学习过", "使用过")
ATS_KEYWORDS = (
    "rag", "bm25", "rerank", "rrf", "agent", "langgraph", "mcp",
    "hitl", "fastapi", "sse", "vllm", "ragas", "docker", "token", "qps", "p95",
)


@dataclass
class StarEntry:
    situation_task: str
    action: str
    result: str

    def render(self) -> str:
        return f"针对{self.situation_task}，{self.action}，最终{self.result}。"


def lint_resume_bullet(bullet: str) -> Dict[str, object]:
    """对单条简历项目经历执行四维体检打分（满分 100）"""
    score = 0
    suggestions: List[str] = []
    low = bullet.lower()

    has_strong = any(v in bullet for v in STRONG_VERBS)
    has_weak = any(v in bullet for v in WEAK_VERBS)
    if has_strong and not has_weak:
        score += 25
    elif has_strong:
        score += 15
        suggestions.append("建议删除'负责/参与'等弱动词，直接用'主导/设计/落地'开头")
    else:
        suggestions.append("缺少强行动动词，建议以'主导设计/构建/优化'等动词突出个人贡献")

    # 检查量化数字（百分比、毫秒、倍数、金额、评分等）
    metrics = re.findall(r"\d+(?:\.\d+)?(?:%|ms|s|倍|元|条|万|k|qps)?", low)
    if len(metrics) >= 2:
        score += 35
    elif len(metrics) == 1:
        score += 20
        suggestions.append("仅有 1 处量化指标，建议补充优化前后对比基线（如从 X% 提升至 Y%）")
    else:
        suggestions.append("缺少量化成果数字！请补充 Recall/Faithfulness/P95延迟/Token降本等指标")

    matched_kw = [kw for kw in ATS_KEYWORDS if kw in low]
    if len(matched_kw) >= 3:
        score += 25
    elif matched_kw:
        score += 12
        suggestions.append("ATS 工程关键词偏少，建议补充具体技术方案词（如 BM25/Rerank/HITL/SSE/Ragas）")
    else:
        suggestions.append("未命中核心 AI 工程关键词，极易被简历初筛过滤")

    if 45 <= len(bullet) <= 160:
        score += 15
    else:
        suggestions.append(f"当前字数 {len(bullet)}，建议控制在 45~160 字以保证高信息密度")

    return {
        "score": score,
        "grade": "EXCELLENT" if score >= 85 else ("GOOD" if score >= 65 else "NEEDS_REWRITE"),
        "matched_keywords": matched_kw,
        "suggestions": suggestions,
    }


if __name__ == "__main__":
    star = StarEntry(
        situation_task="纯向量检索对企业专有错误码召回率偏低(62%)且偶发幻觉的痛点",
        action="主导设计 BM25+向量+RRF 混合检索与 Rerank 置信度拒答流水线，并落地 Ragas 自动化评测门禁",
        result="将 Context Recall 由 62% 提升至 91%，Faithfulness 达 92%，并通过语义缓存与 7B 分级路由降低 54% Token 成本",
    )
    bullet = star.render()
    print("生成 STAR 经历:", bullet)
    print("高分经历体检:", lint_resume_bullet(bullet))
    print("流水账体检:", lint_resume_bullet("负责参与公司知识库项目，使用了大模型和接口开发。"))

