"""
Day 30 - 步骤一：端到端企业级 RAG 核心流水线（检索 + 引用溯源 + 防幻觉兜底）
对应生产栈：LangChain LCEL + Chroma/Milvus + DeepSeek/Qwen ChatModel
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import BaseMessage, HumanMessage, StarMindChatModel, SystemMessage
from src.day28_loaders import Document
from src.day28_text_splitter import RecursiveCharacterTextSplitter
from src.day29_vector_store import StarMindVectorStore


FALLBACK_ANSWER = (
    "抱歉，星辰知识库中暂未找到与该问题相关的确切依据，无法为您编造答案。"
    "建议联系对应业务部门（HR/财务/IT服务台）人工确认。"
)


@dataclass
class Citation:
    """单条结构化引用溯源对象，供前端展示来源卡片与原文片段。"""

    ref_id: int
    source: str
    section: str
    score: float
    snippet: str


@dataclass
class RAGResponse:
    """RAG 问答统一响应结构体。"""

    question: str
    answer: str
    citations: List[Citation] = field(default_factory=list)
    is_fallback: bool = False
    latency_ms: float = 0.0


def _grounded_rag_handler(messages: List[BaseMessage]) -> str:
    """
    离线确定性 Grounded 生成器（模拟严格遵循 <context> 的企业大模型）：
    从检索到的 [来源N] 片段中提取与问题最相关的事实句子并附带引用编号。
    生产环境替换为 DeepSeek-V3 / Qwen2.5-72B ChatModel 即可。
    """
    user_prompt = messages[-1].content
    # 解析 <context> 中的 [来源N] 块与 <question>
    q_match = re.search(r"<question>(.*?)</question>", user_prompt, re.DOTALL)
    ctx_match = re.search(r"<context>(.*?)</context>", user_prompt, re.DOTALL)
    question = q_match.group(1).strip() if q_match else ""
    context = ctx_match.group(1).strip() if ctx_match else ""

    if not context:
        return FALLBACK_ANSWER

    blocks = re.findall(r"(\[来源\d+\][^\n]*\n.*?)(?=\[来源\d+\]|\Z)", context, re.DOTALL)
    q_chars = set(re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", question.lower()))

    selected_lines: List[str] = []
    for block in blocks[:3]:
        header_match = re.match(r"(\[来源\d+\])[^\n]*\n(.*)", block.strip(), re.DOTALL)
        if not header_match:
            continue
        ref_tag, body = header_match.group(1), header_match.group(2).strip()
        # 按句拆分，挑出与提问重合度最高的 1~2 句忠实复述
        sentences = [s.strip() for s in re.split(r"(?<=[。！？；\n])", body) if s.strip()]
        scored = sorted(
            sentences,
            key=lambda s: len(q_chars & set(re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", s.lower()))),
            reverse=True,
        )
        best_sent = scored[0] if scored else body[:100]
        selected_lines.append(f"- {best_sent} {ref_tag}")

    if not selected_lines:
        return FALLBACK_ANSWER

    return "根据星辰数科企业知识库记录，为您整理如下：\n" + "\n".join(selected_lines)


class EnterpriseRAGPipeline:
    """
    星辰智脑端到端企业级 RAG 问答流水线：
    支持增量入库、相似度阈值拒答、部门元数据过滤与结构化引用溯源。
    """

    SYSTEM_PROMPT = (
        "你是杭州星辰数科「星辰智脑」企业知识库问答助手。\n"
        "严格遵守以下规则：\n"
        "1. 仅允许基于 <context> 标签内提供的参考资料作答，严禁编造未提及的数字、制度或流程。\n"
        "2. 每个关键事实后必须标注对应的引用编号（如 [来源1]）。\n"
        "3. 如果参考资料不足以回答问题，请直接输出标准拒答提示。"
    )

    def __init__(
        self,
        vector_store: Optional[StarMindVectorStore] = None,
        chunk_size: int = 200,
        chunk_overlap: int = 30,
        top_k: int = 3,
        score_threshold: float = 0.22,
        chat_model: Optional[StarMindChatModel] = None,
    ) -> None:
        self.vector_store = vector_store or StarMindVectorStore(collection_name="starmind_rag")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
        self.top_k = top_k
        self.score_threshold = score_threshold
        self.chat_model = chat_model or StarMindChatModel(
            model_name="starmind-rag-llm",
            temperature=0.0,
            handler=_grounded_rag_handler,
        )

    def ingest_documents(self, docs: Sequence[Document]) -> int:
        """离线入库流水线：分块 -> 向量化 -> 写入向量库。"""
        chunks = self.splitter.split_documents(docs)
        ids = self.vector_store.add_documents(chunks)
        return len(ids)

    def ask(
        self,
        question: str,
        where: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
    ) -> RAGResponse:
        """在线问答流水线：检索 -> 阈值门控 -> 增强生成 -> 溯源封装。"""
        start = time.perf_counter()
        k = top_k or self.top_k
        raw_hits = self.vector_store.similarity_search_with_score(question, k=k, where=where)

        # 第 1 层防幻觉硬护栏：剔除低于相似度阈值的噪音切片
        valid_hits = [(doc, score) for doc, score in raw_hits if score >= self.score_threshold]
        if not valid_hits:
            return RAGResponse(
                question=question,
                answer=FALLBACK_ANSWER,
                citations=[],
                is_fallback=True,
                latency_ms=round((time.perf_counter() - start) * 1000, 2),
            )

        citations: List[Citation] = []
        context_blocks: List[str] = []
        for idx, (doc, score) in enumerate(valid_hits, start=1):
            source = str(doc.metadata.get("source", "未知文档"))
            section = str(doc.metadata.get("section", "正文"))
            citations.append(
                Citation(
                    ref_id=idx,
                    source=source,
                    section=section,
                    score=score,
                    snippet=doc.page_content[:120],
                )
            )
            context_blocks.append(f"[来源{idx}] 文档：{source}（章节：{section}）\n{doc.page_content}")

        context_str = "\n\n".join(context_blocks)
        user_content = f"<context>\n{context_str}\n</context>\n\n<question>{question}</question>"
        ai_msg = self.chat_model.invoke([
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ])

        return RAGResponse(
            question=question,
            answer=ai_msg.content,
            citations=citations,
            is_fallback=False,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
        )


if __name__ == "__main__":
    rag = EnterpriseRAGPipeline()
    n = rag.ingest_documents([
        Document(
            "杭州星辰数科差旅报销标准：一线城市（北上广深）住宿上限600元/晚，新一线城市（杭州等）480元/晚，餐补100元/天。",
            {"source": "财务报销制度_2026.md", "section": "差旅标准", "dept": "财务部"},
        ),
        Document(
            "研发代码发布红线：合并 main 分支需 GitLab MR 至少1位架构师审批，严禁周五17:00后非紧急发布。",
            {"source": "研发发布规范.md", "section": "发布窗口", "dept": "研发部"},
        ),
    ])
    print(f"成功入库切片数: {n}")

    r_hit = rag.ask("去北京出差住酒店报销上限是多少？")
    print("\n【命中场景】\n", r_hit.answer)
    print("引用列表:", [(c.ref_id, c.source, c.score) for c in r_hit.citations])

    r_miss = rag.ask("火星距离地球有多少光年？")
    print("\n【库外拒答场景】\n", r_miss.answer, "| is_fallback =", r_miss.is_fallback)

