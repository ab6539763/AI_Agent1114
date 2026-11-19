"""
Day 33 - 步骤二：Cross-Encoder 重排序器（bge-reranker 原理）与父文档检索器（ParentDocumentRetriever）
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day33_hybrid_rrf import (
    BM25Index,
    DenseVectorIndex,
    Document,
    HybridRRFRetriever,
    tokenize_mixed_cn_en,
)


class BGERerankerSimulator:
    """
    类 BAAI/bge-reranker-v2-m3 交叉编码精排器（离线可运行版）：
    模拟 Cross-Encoder 将 (Query, Doc) 拼接后的细粒度交互特征：
    1. 查询关键实体/错误码在文档中的精确覆盖率；
    2. 连续二元词组（Bigram）匹配密度；
    3. 章节标题（section）强相关加权；
    4. 通过 Sigmoid 映射为 [0, 1] 规范化相关概率分数。
    """

    def score_pair(self, query: str, doc: Document) -> float:
        q_tokens = set(tokenize_mixed_cn_en(query))
        if not q_tokens:
            return 0.0
        d_tokens = set(tokenize_mixed_cn_en(doc.page_content))
        section_tokens = set(tokenize_mixed_cn_en(str(doc.metadata.get("section", ""))))

        # 1. 精确错误码/专有代码匹配（最高权重）
        q_codes = set(re.findall(r"[a-z0-9]+[-_][a-z0-9]+", query.lower()))
        code_hit = 0.0
        if q_codes:
            matched_codes = sum(1 for c in q_codes if c in doc.page_content.lower())
            code_hit = 4.0 * (matched_codes / len(q_codes))

        # 2. 二元词组与全词元覆盖率（模拟词级 Attention 交互）
        q_bigrams = {t for t in q_tokens if len(t) >= 2}
        d_bigrams = {t for t in d_tokens if len(t) >= 2}
        bigram_overlap = len(q_bigrams & d_bigrams) / max(1, len(q_bigrams))
        token_overlap = len(q_tokens & d_tokens) / max(1, len(q_tokens))

        # 3. 标题/章节命中加成
        section_overlap = len(q_bigrams & section_tokens) / max(1, len(q_bigrams)) if q_bigrams else 0.0

        logit = -2.2 + code_hit + 3.8 * bigram_overlap + 1.8 * token_overlap + 1.6 * section_overlap
        prob = 1.0 / (1.0 + math.exp(-logit))
        return round(prob, 4)

    def rerank(
        self,
        query: str,
        candidates: Sequence[Document],
        top_n: int = 3,
    ) -> List[Tuple[Document, float]]:
        scored = [(doc, self.score_pair(query, doc)) for doc in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]


class ParentDocumentRetriever:
    """
    父文档检索器（Small-to-Big 策略）：
    - 入库时：将完整父文档存入 docstore，同时切分为小粒度子切片（Child Chunks）写入混合索引；
    - 检索时：先对子切片执行 Hybrid RRF + Reranker 精排，再按 parent_id 去重反查完整父文档。
    """

    def __init__(
        self,
        child_chunk_size: int = 55,
        child_chunk_overlap: int = 12,
        use_rerank: bool = True,
    ) -> None:
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap
        self.use_rerank = use_rerank

        self.parent_store: Dict[str, Document] = {}
        self.bm25 = BM25Index()
        self.dense = DenseVectorIndex()
        self.hybrid = HybridRRFRetriever(self.bm25, self.dense)
        self.reranker = BGERerankerSimulator()
        self.total_child_chunks: int = 0

    def _split_to_children(self, parent_doc: Document, parent_id: str) -> List[Document]:
        text = parent_doc.page_content.strip()
        children: List[Document] = []
        step = max(1, self.child_chunk_size - self.child_chunk_overlap)
        for idx, start in enumerate(range(0, len(text), step)):
            piece = text[start : start + self.child_chunk_size].strip()
            if not piece:
                continue
            children.append(
                Document(
                    page_content=piece,
                    metadata={
                        **parent_doc.metadata,
                        "doc_id": f"{parent_id}#c{idx}",
                        "parent_id": parent_id,
                        "child_index": idx,
                    },
                )
            )
            if start + self.child_chunk_size >= len(text):
                break
        return children

    def add_parent_documents(self, parents: Sequence[Document]) -> int:
        all_children: List[Document] = []
        for idx, p_doc in enumerate(parents):
            parent_id = str(p_doc.metadata.get("doc_id") or f"parent-{idx}")
            self.parent_store[parent_id] = p_doc
            all_children.extend(self._split_to_children(p_doc, parent_id))

        self.bm25.add_documents(all_children)
        self.dense.add_documents(all_children)
        self.total_child_chunks += len(all_children)
        return len(all_children)

    def retrieve_parents(self, query: str, top_k: int = 2) -> List[Tuple[Document, float]]:
        # 第一阶段：Hybrid RRF 对子切片粗排 Top-8
        coarse_hits = self.hybrid.retrieve(query, top_k=8, recall_k=10)
        if not coarse_hits:
            return []

        # 第二阶段：Cross-Encoder 精排子切片
        if self.use_rerank:
            ranked_children = self.reranker.rerank(query, [d for d, _ in coarse_hits], top_n=6)
        else:
            ranked_children = coarse_hits

        # 第三阶段：按 parent_id 去重（保留得分最高的子块分数）并回溯完整父文档
        parent_best: Dict[str, float] = {}
        for child_doc, score in ranked_children:
            pid = str(child_doc.metadata["parent_id"])
            if pid not in parent_best or score > parent_best[pid]:
                parent_best[pid] = score

        sorted_pids = sorted(parent_best.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self.parent_store[pid], score) for pid, score in sorted_pids]


if __name__ == "__main__":
    parent_docs = [
        Document(
            "【星辰智脑运维排障全指南-网关篇】系统统一入口采用 Nginx + Envoy 双层网关。"
            "当监控告警出现错误码 ERR-5042 时，代表网关调用下游大模型推理服务超时（默认 15 秒）。"
            "标准处置流程：第一步登录 Grafana 查看推理节点显存与排队长度；"
            "第二步临时将 proxy_read_timeout 调大至 30 秒；第三步若持续 5 分钟则触发降级熔断并通知值班架构师。",
            {"doc_id": "P-OPS-01", "source": "运维排障全指南.md", "section": "ERR-5042网关超时"},
        ),
        Document(
            "【杭州星辰数科差旅报销总则】员工因公出差须提前 3 天在 OA 发起差旅申请并经直属主管审批。"
            "住宿标准方面，一线城市（北京、上海、深圳、广州）每晚报销上限 600 元，新一线城市每晚 450 元。"
            "餐饮补助按每天 100 元定额随工资发放，无需粘贴餐饮发票；超标住宿部分由个人承担。",
            {"doc_id": "P-FIN-01", "source": "差旅报销总则.md", "section": "差旅住宿与餐补"},
        ),
    ]

    retriever = ParentDocumentRetriever(child_chunk_size=50, child_chunk_overlap=10, use_rerank=True)
    n_children = retriever.add_parent_documents(parent_docs)
    print(f"父文档数: {len(parent_docs)} -> 切分子切片数: {n_children}")

    hits = retriever.retrieve_parents("ERR-5042 报警后第三步怎么处理？", top_k=1)
    top_parent, top_score = hits[0]
    print(f"精排回溯父文档: {top_parent.doc_id} (rerank_score={top_score})")
    print(f"完整父文档长度: {len(top_parent.page_content)} 字 -> 包含完整三步处置流程!")

