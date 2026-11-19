"""
Day 32 - 步骤二：上下文压缩器（ContextualCompressor）与高级检索召回率对比实验
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_embeddings_hnsw import StarMindLocalEmbeddings, cosine_similarity
from src.day30_kb_cli import build_starmind_kb
from src.day32_query_transform import HyDERetriever, MultiQueryRetriever, QueryRewriter


class ContextualCompressor:
    """
    句子级上下文压缩器：
    将召回的长切片按中文句末标点拆句，计算每句与查询的语义相似度，
    仅保留超过阈值的核心证据句，降低 LLM 输入 Token 与注意力噪音。
    """

    def __init__(
        self,
        embeddings: StarMindLocalEmbeddings | None = None,
        min_sentence_score: float = 0.12,
        max_sentences_per_doc: int = 2,
    ) -> None:
        self.embeddings = embeddings or StarMindLocalEmbeddings()
        self.min_sentence_score = min_sentence_score
        self.max_sentences_per_doc = max_sentences_per_doc

    def compress_documents(
        self,
        query: str,
        docs: Sequence[Document],
    ) -> Tuple[List[Document], float]:
        q_vec = self.embeddings.embed_query(query)
        orig_chars = sum(len(d.page_content) for d in docs)
        compressed: List[Document] = []

        for doc in docs:
            sentences = [s.strip() for s in re.split(r"(?<=[。！？；\n])", doc.page_content) if s.strip()]
            if not sentences:
                continue
            scored = [
                (cosine_similarity(q_vec, self.embeddings.embed_query(s)), idx, s)
                for idx, s in enumerate(sentences)
            ]
            # 筛选超过阈值的高相关句，至少保留最高分 1 句并还原原文顺序
            kept = [item for item in scored if item[0] >= self.min_sentence_score]
            if not kept:
                kept = [max(scored, key=lambda x: x[0])]
            kept_top = sorted(sorted(kept, key=lambda x: x[0], reverse=True)[: self.max_sentences_per_doc], key=lambda x: x[1])
            new_text = "".join(item[2] for item in kept_top)
            compressed.append(
                Document(
                    page_content=new_text,
                    metadata={**doc.metadata, "compressed": True, "orig_len": len(doc.page_content)},
                )
            )

        new_chars = sum(len(d.page_content) for d in compressed)
        saved_ratio = round(1.0 - (new_chars / max(1, orig_chars)), 4)
        return compressed, saved_ratio


# 专门构造贴近真实员工口语/黑话/复合意图的难题测试集
SLANG_EVAL_CASES = [
    ("去魔都住店最多能报多少？", "差旅住宿标准"),
    ("礼拜五下班前能不能推线上？", "生产发布窗口"),
    ("居家干活连不上网咋整？", "VPN与内网接入"),
    ("生病开请假条有啥要求？", "病假与证明"),
    ("老员工年休几天怎么申请？", "年假规定"),
    ("出差吃饭要贴票吗？", "餐饮与交通补助"),
]


def run_recall_comparison(top_k: int = 2) -> Dict[str, float]:
    kb = build_starmind_kb()
    vs = kb.vector_store
    rewriter = QueryRewriter()
    mq = MultiQueryRetriever(vs, rewriter)
    hyde = HyDERetriever(vs)

    strategies = {
        "Baseline_Naive": lambda q: vs.similarity_search_with_score(q, k=top_k),
        "QueryRewriting": lambda q: vs.similarity_search_with_score(rewriter.rewrite(q), k=top_k),
        "MultiQuery": lambda q: mq.retrieve(q, k=top_k),
        "HyDE": lambda q: hyde.retrieve(q, k=top_k),
    }

    report: Dict[str, float] = {}
    for name, fn in strategies.items():
        hits = 0
        for q, expected_section in SLANG_EVAL_CASES:
            docs = [d for d, _ in fn(q)]
            if any(d.metadata.get("section") == expected_section for d in docs):
                hits += 1
        report[name] = round(hits / len(SLANG_EVAL_CASES), 4)
    return report


if __name__ == "__main__":
    print("=== 口语/黑话难题集 Recall@2 对比实验 ===")
    for k_name, score in run_recall_comparison(top_k=2).items():
        print(f"  {k_name:16s} -> Recall@2 = {score:.2%}")

    # 演示上下文压缩节省 Token 效果
    long_doc = Document(
        "公司成立于2018年位于杭州未来科技城，拥有超过800名员工。"
        "一线城市（北京、上海、深圳、广州）酒店住宿上限每晚600元。"
        "园区地下车库免费向全体员工开放，请勿占用消防通道。"
        "食堂二楼提供杭帮菜和轻食沙拉。",
        {"source": "综合手册.md"},
    )
    comp = ContextualCompressor(max_sentences_per_doc=1)
    slim_docs, saved = comp.compress_documents("上海出差住酒店上限是多少", [long_doc])
    print(f"\n上下文压缩节省字符比例: {saved:.1%}")
    print("压缩后保留证据句:", slim_docs[0].page_content)

