"""
Day 32 - 步骤一：检索前优化三板斧（Query Rewriting / Multi-Query / HyDE）
对应生产包：langchain.retrievers.multi_query / HypotheticalDocumentEmbedder
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_vector_store import StarMindVectorStore


class QueryRewriter:
    """
    企业级查询改写器：
    将员工口语、地域别称与公司黑话规范化为正式制度检索词（生产可叠加轻量 7B LLM）。
    """

    TERM_MAPPING: Dict[str, str] = {
        "魔都": "上海 一线城市",
        "帝都": "北京 一线城市",
        "鹏城": "深圳 一线城市",
        "住店": "酒店住宿标准上限",
        "吃饭": "餐饮补助发票",
        "推线上": "生产发布窗口上线变更",
        "发版": "生产发布窗口代码合并",
        "礼拜五": "周五",
        "居家": "远程办公",
        "连不上网": "零信任VPN动态令牌",
        "请假条": "医院诊断证明病假",
        "年休": "带薪年假天数申请",
    }

    def rewrite(self, query: str) -> str:
        rewritten = query
        additions: List[str] = []
        for slang, formal in self.TERM_MAPPING.items():
            if slang in rewritten:
                additions.append(formal)
        if not additions:
            return query
        return f"{query} {' '.join(additions)}"


class MultiQueryRetriever:
    """
    多路查询检索器：
    将一个复杂或口语提问扩展为多个互补视角子查询，分别检索向量库后按内容去重取最高分合并。
    """

    def __init__(self, vector_store: StarMindVectorStore, rewriter: QueryRewriter | None = None) -> None:
        self.vector_store = vector_store
        self.rewriter = rewriter or QueryRewriter()

    def generate_queries(self, original_query: str) -> List[str]:
        queries: List[str] = [original_query]
        formal = self.rewriter.rewrite(original_query)
        if formal != original_query:
            queries.append(formal)

        # 拆解复合连接词（「和/以及/还有/顺便」）生成独立子查询
        for splitter in ("以及", "还有", "顺便", "和", "跟", "，", ","):
            if splitter in original_query:
                parts = [p.strip() for p in original_query.split(splitter) if len(p.strip()) >= 3]
                for p in parts:
                    rewritten_p = self.rewriter.rewrite(p)
                    if rewritten_p not in queries:
                        queries.append(rewritten_p)
                break
        return queries[:4]

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        sub_queries = self.generate_queries(query)
        merged: Dict[str, Tuple[Document, float]] = {}

        for sq in sub_queries:
            for doc, score in self.vector_store.similarity_search_with_score(sq, k=k):
                key = doc.page_content
                if key not in merged or score > merged[key][1]:
                    merged[key] = (doc, score)

        ranked = sorted(merged.values(), key=lambda x: x[1], reverse=True)
        return ranked[:k]


class HyDERetriever:
    """
    HyDE（Hypothetical Document Embeddings）假设性文档嵌入检索器：
    先生成一段符合企业制度文风的假设性回答，再以假设文档的向量检索真实知识库。
    """

    def __init__(self, vector_store: StarMindVectorStore) -> None:
        self.vector_store = vector_store

    def generate_hypothetical_doc(self, query: str) -> str:
        """离线模拟 LLM 生成制度风格的假设性段落（生产环境调用轻量 ChatModel）。"""
        if any(w in query for w in ("住店", "魔都", "帝都", "酒店", "出差", "吃饭", "报销")):
            return (
                "根据杭州星辰数科财务报销制度，员工因公前往一线城市（北京、上海、深圳、广州）或新一线城市出差，"
                "需遵守酒店住宿每晚标准上限与餐饮补助定额发放规定，并提前在OA完成审批。"
            )
        if any(w in query for w in ("礼拜五", "周五", "推线上", "发版", "合并", "代码")):
            return (
                "根据研发工程规范，业务代码合并至main分支须通过GitLab Merge Request评审与CI测试，"
                "日常生产发布窗口限定为周一至周四，严禁周五17:00之后非紧急变更上线。"
            )
        if any(w in query for w in ("居家", "内网", "VPN", "脱敏", "手机号")):
            return (
                "根据IT信息安全指南，员工远程办公接入内网须使用星辰零信任VPN与动态令牌，"
                "同时严格遵守客户敏感数据脱敏红线。"
            )
        if any(w in query for w in ("年休", "年假", "病假", "请假", "休假")):
            return (
                "根据HR员工休假手册，员工按工龄享有带薪年假并需提前提交OA申请，"
                "病假超过规定天数须提供公立医院诊断证明。"
            )
        return f"关于「{query}」的企业正式管理制度条款与执行标准说明。"

    def retrieve(self, query: str, k: int = 3) -> List[Tuple[Document, float]]:
        hypo_doc = self.generate_hypothetical_doc(query)
        return self.vector_store.similarity_search_with_score(hypo_doc, k=k)


if __name__ == "__main__":
    from src.day30_kb_cli import build_starmind_kb

    kb = build_starmind_kb()
    q = "去魔都出差住店和吃饭分别怎么报？"
    mq = MultiQueryRetriever(kb.vector_store)
    hyde = HyDERetriever(kb.vector_store)

    print("Multi-Query 展开:", mq.generate_queries(q))
    print("Multi-Query 命中:", [(d.metadata["section"], s) for d, s in mq.retrieve(q, k=2)])
    print("HyDE 命中:", [(d.metadata["section"], s) for d, s in hyde.retrieve(q, k=2)])

