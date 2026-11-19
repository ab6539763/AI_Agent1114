"""
Day 35 - 步骤一：LlamaIndex 核心架构精简实现
还原：Document -> SentenceNodeParser -> TextNode(关系链表) -> VectorStoreIndex / SummaryIndex
      -> ResponseSynthesizer(compact/refine) -> RouterQueryEngine
"""

from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple


@dataclass
class Document:
    """LlamaIndex 风格原始文档对象。"""

    text: str
    doc_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.doc_id:
            self.doc_id = "doc_" + hashlib.md5(self.text.encode("utf-8")).hexdigest()[:8]


@dataclass
class TextNode:
    """
    LlamaIndex 核心知识节点：
    不仅保存文本与元数据，还通过 relationships 维护 SOURCE / PREVIOUS / NEXT 拓扑指针。
    """

    text: str
    node_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    relationships: Dict[str, str] = field(default_factory=dict)


@dataclass
class NodeWithScore:
    node: TextNode
    score: float


@dataclass
class QueryResponse:
    response: str
    source_nodes: List[NodeWithScore]
    routed_engine: str = "vector"


class SentenceNodeParser:
    """按句切分并自动串联 PREVIOUS / NEXT 双向链表的节点解析器。"""

    def __init__(self, sentences_per_node: int = 1) -> None:
        self.sentences_per_node = max(1, sentences_per_node)

    def get_nodes_from_documents(self, documents: Sequence[Document]) -> List[TextNode]:
        all_nodes: List[TextNode] = []
        for doc in documents:
            sents = [s.strip() for s in re.split(r"(?<=[。！？\n])", doc.text) if s.strip()]
            doc_nodes: List[TextNode] = []
            for idx in range(0, len(sents), self.sentences_per_node):
                chunk_text = "".join(sents[idx : idx + self.sentences_per_node])
                node_id = f"{doc.doc_id}_n{len(doc_nodes)}"
                node = TextNode(
                    text=chunk_text,
                    node_id=node_id,
                    metadata={**doc.metadata, "doc_id": doc.doc_id, "node_idx": len(doc_nodes)},
                    relationships={"SOURCE": doc.doc_id},
                )
                doc_nodes.append(node)

            # 串联同一文档内相邻节点的 PREVIOUS / NEXT 双向指针
            for i, node in enumerate(doc_nodes):
                if i > 0:
                    node.relationships["PREVIOUS"] = doc_nodes[i - 1].node_id
                if i < len(doc_nodes) - 1:
                    node.relationships["NEXT"] = doc_nodes[i + 1].node_id

            all_nodes.extend(doc_nodes)
        return all_nodes


def _embed_text(text: str, dim: int = 96) -> List[float]:
    vec = [0.0] * dim
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", lowered)
    for chunk in re.findall(r"[\u4e00-\u9fff]+", lowered):
        for ch in chunk:
            tokens.append(ch)
        for i in range(len(chunk) - 1):
            tokens.append(chunk[i : i + 2])
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
        vec[h % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class ResponseSynthesizer:
    """LlamaIndex 风格响应合成器，支持 compact（紧凑拼装）与 refine（逐块精炼）模式。"""

    def __init__(self, response_mode: str = "compact") -> None:
        if response_mode not in ("compact", "refine"):
            raise ValueError(f"Unsupported response_mode: {response_mode}")
        self.response_mode = response_mode

    def synthesize(self, query: str, nodes: Sequence[NodeWithScore]) -> str:
        if not nodes:
            return "知识库中未检索到与当前问题直接相关的制度条款。"

        if self.response_mode == "compact":
            evidences = [
                f"[{i}] ({n.node.metadata.get('source', '未知')}) {n.node.text}"
                for i, n in enumerate(nodes, start=1)
            ]
            return f"【Compact综合回答】针对「{query}」，依据以下制度条款：\n" + "\n".join(evidences)

        # refine 模式：逐个节点增量精炼摘要（典型用于 SummaryIndex 全局总结）
        refined_points: List[str] = []
        for idx, n in enumerate(nodes, start=1):
            source = n.node.metadata.get("source", "文档")
            refined_points.append(f"要点{idx}（{source}）：{n.node.text}")
        return f"【Refine全量摘要】针对「{query}」，汇总全文核心要点如下：\n" + "\n".join(refined_points)


class VectorStoreIndex:
    """LlamaIndex 风格向量索引：支持邻域节点扩展（expand_prev_next=True）。"""

    def __init__(self, nodes: Sequence[TextNode]) -> None:
        self.nodes: List[TextNode] = list(nodes)
        self.node_map: Dict[str, TextNode] = {n.node_id: n for n in self.nodes}
        self.vectors: Dict[str, List[float]] = {n.node_id: _embed_text(n.text) for n in self.nodes}

    @classmethod
    def from_documents(
        cls,
        documents: Sequence[Document],
        parser: Optional[SentenceNodeParser] = None,
    ) -> "VectorStoreIndex":
        node_parser = parser or SentenceNodeParser(sentences_per_node=1)
        return cls(node_parser.get_nodes_from_documents(documents))

    def retrieve(
        self,
        query: str,
        similarity_top_k: int = 2,
        expand_prev_next: bool = True,
    ) -> List[NodeWithScore]:
        q_vec = _embed_text(query)
        scored = [
            NodeWithScore(node=n, score=round(_cosine(q_vec, self.vectors[n.node_id]), 4))
            for n in self.nodes
        ]
        scored.sort(key=lambda x: x.score, reverse=True)
        top_hits = scored[:similarity_top_k]

        if not expand_prev_next:
            return top_hits

        # 利用 TextNode.relationships 的 PREVIOUS 指针自动补全前文上下文，消除「上述标准」指代断层
        expanded: List[NodeWithScore] = []
        for hit in top_hits:
            prev_id = hit.node.relationships.get("PREVIOUS")
            merged_text = hit.node.text
            if prev_id and prev_id in self.node_map:
                merged_text = self.node_map[prev_id].text + merged_text
            expanded.append(
                NodeWithScore(
                    node=TextNode(
                        text=merged_text,
                        node_id=hit.node.node_id,
                        metadata={**hit.node.metadata, "expanded_prev": bool(prev_id)},
                        relationships=dict(hit.node.relationships),
                    ),
                    score=hit.score,
                )
            )
        return expanded

    def as_query_engine(
        self,
        similarity_top_k: int = 2,
        response_mode: str = "compact",
        expand_prev_next: bool = True,
    ) -> "RetrieverQueryEngine":
        return RetrieverQueryEngine(
            retriever_fn=lambda q: self.retrieve(
                q, similarity_top_k=similarity_top_k, expand_prev_next=expand_prev_next
            ),
            synthesizer=ResponseSynthesizer(response_mode=response_mode),
            engine_name="vector_index",
        )


class SummaryIndex:
    """LlamaIndex 风格摘要索引：遍历全量节点用于全局归纳总结。"""

    def __init__(self, nodes: Sequence[TextNode]) -> None:
        self.nodes = list(nodes)

    @classmethod
    def from_documents(
        cls,
        documents: Sequence[Document],
        parser: Optional[SentenceNodeParser] = None,
    ) -> "SummaryIndex":
        node_parser = parser or SentenceNodeParser(sentences_per_node=1)
        return cls(node_parser.get_nodes_from_documents(documents))

    def as_query_engine(self, response_mode: str = "refine") -> "RetrieverQueryEngine":
        return RetrieverQueryEngine(
            retriever_fn=lambda _q: [NodeWithScore(node=n, score=1.0) for n in self.nodes],
            synthesizer=ResponseSynthesizer(response_mode=response_mode),
            engine_name="summary_index",
        )


class RetrieverQueryEngine:
    def __init__(self, retriever_fn, synthesizer: ResponseSynthesizer, engine_name: str) -> None:
        self.retriever_fn = retriever_fn
        self.synthesizer = synthesizer
        self.engine_name = engine_name

    def query(self, question: str) -> QueryResponse:
        nodes = self.retriever_fn(question)
        answer = self.synthesizer.synthesize(question, nodes)
        return QueryResponse(response=answer, source_nodes=nodes, routed_engine=self.engine_name)


class RouterQueryEngine:
    """意图路由查询引擎：自动判断走 SummaryIndex 全局总结还是 VectorStoreIndex 细节精查。"""

    SUMMARY_TRIGGERS = ("总结", "概览", "全文", "要点", "归纳", "都有哪些规定", "梳理一下")

    def __init__(
        self,
        vector_engine: RetrieverQueryEngine,
        summary_engine: RetrieverQueryEngine,
    ) -> None:
        self.vector_engine = vector_engine
        self.summary_engine = summary_engine

    def query(self, question: str) -> QueryResponse:
        if any(kw in question for kw in self.SUMMARY_TRIGGERS):
            return self.summary_engine.query(question)
        return self.vector_engine.query(question)


if __name__ == "__main__":
    doc = Document(
        text=(
            "一线城市（北京、上海、深圳、广州）出差酒店住宿报销上限为每晚600元。"
            "上述标准同样适用于外包人员及在岗实习生。"
            "出差餐饮补助按每天100元定额随月薪发放，无需粘贴发票。"
        ),
        doc_id="fin_travel_2026",
        metadata={"source": "财务差旅制度_2026.md"},
    )
    vec_idx = VectorStoreIndex.from_documents([doc])
    sum_idx = SummaryIndex.from_documents([doc])
    router = RouterQueryEngine(
        vector_engine=vec_idx.as_query_engine(similarity_top_k=1, expand_prev_next=True),
        summary_engine=sum_idx.as_query_engine(response_mode="refine"),
    )

    r_detail = router.query("实习生出差住宿适用什么标准？")
    print(f"[路由={r_detail.routed_engine}]\n{r_detail.response}\n")

    r_summary = router.query("请总结一下这份差旅制度的全部要点")
    print(f"[路由={r_summary.routed_engine}]\n{r_summary.response}")

