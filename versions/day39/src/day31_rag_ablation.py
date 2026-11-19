"""
Day 31 - 步骤二：RAG 超参数多维消融实验框架（Hit@K / MRR / Latency 量化对比）
"""

from __future__ import annotations

import hashlib
import math
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document, MarkdownLoader
from src.day28_text_splitter import RecursiveCharacterTextSplitter
from src.day29_embeddings_hnsw import StarMindLocalEmbeddings
from src.day29_vector_store import StarMindVectorStore
from src.day30_kb_cli import STARMIND_CORPUS


class BaselineCharEmbeddings(StarMindLocalEmbeddings):
    """弱基线 Embedding（仅用单字特征、无双字词组与同义词槽），用于消融对比。"""

    def __init__(self, dim: int = 64) -> None:
        super().__init__(dim=dim)

    def _extract_features(self, text: str) -> List[Tuple[str, float]]:
        return [(f"c1:{ch}", 1.0) for ch in re.findall(r"[\u4e00-\u9fff]", text)]


@dataclass
class EvalCase:
    question: str
    expected_source: str
    expected_keyword: str


@dataclass
class ExperimentResult:
    exp_name: str
    embedding_name: str
    chunk_size: int
    top_k: int
    num_chunks: int
    hit_at_k: float
    mrr: float
    avg_latency_ms: float


GOLDEN_EVAL_SET: List[EvalCase] = [
    EvalCase("去上海出差住酒店每晚报销上限是多少？", "财务报销制度_2026.md", "600元"),
    EvalCase("杭州新一线城市住宿标准多少钱？", "财务报销制度_2026.md", "480元"),
    EvalCase("出差餐补需要贴餐饮发票吗？", "财务报销制度_2026.md", "无需提供餐饮发票"),
    EvalCase("入职满一年有多少天年假？", "HR员工休假手册_2026.md", "5天"),
    EvalCase("生病请病假超过一天要开什么证明？", "HR员工休假手册_2026.md", "诊断证明"),
    EvalCase("代码合入main分支需要代码评审吗？", "研发工程规范_v3.md", "Merge Request"),
    EvalCase("周五晚上可以做生产环境发版吗？", "研发工程规范_v3.md", "17:00"),
    EvalCase("居家办公连不上内网VPN怎么处理？", "IT信息安全指南.md", "动态令牌"),
    EvalCase("可以把客户明文手机号发给公有云大模型吗？", "IT信息安全指南.md", "脱敏"),
]


def load_base_corpus() -> List[Document]:
    loader = MarkdownLoader()
    docs: List[Document] = []
    for filename, dept, md_text in STARMIND_CORPUS:
        parsed = loader.load_text(md_text, source=filename)
        for d in parsed:
            d.metadata["dept"] = dept
        docs.extend(parsed)
    return docs


def evaluate_config(
    exp_name: str,
    embedding_name: str,
    embeddings: StarMindLocalEmbeddings,
    chunk_size: int,
    chunk_overlap: int,
    top_k: int,
    eval_set: Sequence[EvalCase] = GOLDEN_EVAL_SET,
) -> ExperimentResult:
    """运行单组超参数配置，返回 Hit@K、MRR 与平均检索延迟。"""
    base_docs = load_base_corpus()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    ).split_documents(base_docs)

    store = StarMindVectorStore(collection_name=f"ablation_{exp_name}", embedding_function=embeddings)
    store.add_documents(chunks)

    hits = 0
    rr_sum = 0.0
    total_ms = 0.0

    for case in eval_set:
        t0 = time.perf_counter()
        results = store.similarity_search(case.question, k=top_k)
        total_ms += (time.perf_counter() - t0) * 1000

        found_rank = 0
        for rank, doc in enumerate(results, start=1):
            if doc.metadata.get("source") == case.expected_source and case.expected_keyword in doc.page_content:
                found_rank = rank
                break
        if found_rank > 0:
            hits += 1
            rr_sum += 1.0 / found_rank

    n = max(1, len(eval_set))
    return ExperimentResult(
        exp_name=exp_name,
        embedding_name=embedding_name,
        chunk_size=chunk_size,
        top_k=top_k,
        num_chunks=len(chunks),
        hit_at_k=round(hits / n, 4),
        mrr=round(rr_sum / n, 4),
        avg_latency_ms=round(total_ms / n, 3),
    )


def run_ablation_suite() -> List[ExperimentResult]:
    """执行 6 组控制变量消融实验。"""
    configs = [
        ("E1_基线单字_64d", "Char-64d", BaselineCharEmbeddings(dim=64), 160, 20, 3),
        ("E2_小切片_60字", "StarMind-256d", StarMindLocalEmbeddings(dim=256), 60, 10, 3),
        ("E3_中切片_140字", "StarMind-256d", StarMindLocalEmbeddings(dim=256), 140, 20, 3),
        ("E4_大切片_260字", "StarMind-256d", StarMindLocalEmbeddings(dim=256), 260, 30, 3),
        ("E5_中切片_Top1", "StarMind-256d", StarMindLocalEmbeddings(dim=256), 140, 20, 1),
        ("E6_中切片_Top5", "StarMind-256d", StarMindLocalEmbeddings(dim=256), 140, 20, 5),
    ]
    return [evaluate_config(*cfg) for cfg in configs]


def render_markdown_report(results: Sequence[ExperimentResult]) -> str:
    lines = [
        "| 实验组 | Embedding模型 | ChunkSize | TopK | 切片数 | Hit@K | MRR | 平均耗时(ms) |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r.exp_name} | {r.embedding_name} | {r.chunk_size} | {r.top_k} | "
            f"{r.num_chunks} | {r.hit_at_k:.2%} | {r.mrr:.3f} | {r.avg_latency_ms:.3f} |"
        )
    best = max(results, key=lambda x: (x.mrr, x.hit_at_k, -x.avg_latency_ms))
    lines.append(f"\n推荐线上配置：**{best.exp_name}**（MRR={best.mrr:.3f}, Hit@K={best.hit_at_k:.2%}）")
    return "\n".join(lines)


if __name__ == "__main__":
    suite = run_ablation_suite()
    print(render_markdown_report(suite))

