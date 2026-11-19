"""
Day 35 - 步骤二：LlamaIndex 风格 vs LangChain 风格扁平管道基准对比评测
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day35_llamaindex_core import (
    Document,
    RouterQueryEngine,
    SummaryIndex,
    VectorStoreIndex,
)


@dataclass
class BenchmarkRow:
    framework: str
    completeness_rate: float
    avg_latency_ms: float
    strengths: str


BENCHMARK_DOCS = [
    Document(
        text=(
            "一线城市（北京、上海、深圳、广州）出差酒店住宿报销上限为每晚600元。"
            "上述标准同样适用于外包人员及在岗实习生。"
            "出差餐饮补助按每天100元定额随月薪发放，无需粘贴发票。"
        ),
        doc_id="fin_travel",
        metadata={"source": "差旅制度.md"},
    ),
    Document(
        text=(
            "生产环境日常发布窗口为周一至周四10:00-18:00，严禁周五17:00后非紧急变更。"
            "若遇P0级线上故障需打破该窗口限制，必须经值班架构师与CTO双人审批。"
        ),
        doc_id="dev_release",
        metadata={"source": "研发发布规范.md"},
    ),
]

# 专门测试「跨段指代」与「全文总结」两类高难场景
BENCHMARK_CASES = [
    ("实习生出差住宿适用什么标准？", ["600元", "实习生"]),
    ("P0级线上故障打破发布窗口限制需要谁审批，原窗口是哪几天？", ["周一至周四", "CTO"]),
    ("请总结一下全部制度的核心要点", ["600元", "100元", "周一至周四"]),
]


def run_framework_benchmark() -> List[BenchmarkRow]:
    # 1. 模拟 LangChain 经典扁平切片检索（无 PREVIOUS 指针扩展、无 SummaryIndex 路由）
    flat_index = VectorStoreIndex.from_documents(BENCHMARK_DOCS)
    lc_flat_engine = flat_index.as_query_engine(
        similarity_top_k=1, response_mode="compact", expand_prev_next=False
    )

    # 2. LlamaIndex 风格：TextNode 邻域自动扩展 + RouterQueryEngine(Vector + Summary)
    li_router = RouterQueryEngine(
        vector_engine=flat_index.as_query_engine(
            similarity_top_k=1, response_mode="compact", expand_prev_next=True
        ),
        summary_engine=SummaryIndex.from_documents(BENCHMARK_DOCS).as_query_engine(
            response_mode="refine"
        ),
    )

    rows: List[BenchmarkRow] = []
    for name, engine, strength in [
        ("LangChain_Flat_RAG", lc_flat_engine, "LCEL灵活编排、生态最全、多Agent工作流强"),
        ("LlamaIndex_NodeRouter", li_router, "Node链表防断层、多态Index与全局摘要天然占优"),
    ]:
        passed = 0
        t0 = time.perf_counter()
        for q, must_keywords in BENCHMARK_CASES:
            resp = engine.query(q)
            if all(kw in resp.response for kw in must_keywords):
                passed += 1
        elapsed_ms = (time.perf_counter() - t0) * 1000.0 / len(BENCHMARK_CASES)
        rows.append(
            BenchmarkRow(
                framework=name,
                completeness_rate=round(passed / len(BENCHMARK_CASES), 4),
                avg_latency_ms=round(elapsed_ms, 3),
                strengths=strength,
            )
        )
    return rows


def recommend_framework(need_multi_agent: bool, heavy_doc_summary: bool) -> Dict[str, str]:
    """企业级技术选型决策辅助器。"""
    if heavy_doc_summary and not need_multi_agent:
        return {"choice": "LlamaIndex", "reason": "重度长文档索引、多级摘要与复杂数据连接场景最优"}
    if need_multi_agent and not heavy_doc_summary:
        return {"choice": "LangChain + LangGraph", "reason": "重度工具编排、状态机工作流与多 Agent 协作最优"}
    return {
        "choice": "Hybrid (LlamaIndex 索引检索 + LangGraph 上层编排)",
        "reason": "兼具强文档索引能力与复杂工作流编排，是中大型企业中台常见组合",
    }


if __name__ == "__main__":
    print("=== LangChain 扁平管道 vs LlamaIndex 节点路由基准对比 ===")
    for row in run_framework_benchmark():
        print(
            f"  {row.framework:22s} | 答案完整率={row.completeness_rate:6.2%} "
            f"| 平均耗时={row.avg_latency_ms:6.3f}ms | 优势: {row.strengths}"
        )
    print("\n星辰智脑项目二选型建议:", recommend_framework(need_multi_agent=True, heavy_doc_summary=True))

