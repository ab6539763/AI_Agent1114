"""
Day 35 课后作业 3（架构进阶）：作业三：实现 SubQuestionQueryEngine（跨文档子问题拆解引擎）
工单：STARMIND-035
"""

"""Day 35 作业三参考答案：SubQuestionQueryEngine 跨主题子问题拆解"""
import re
from typing import List
from src.day35_llamaindex_core import Document, QueryResponse, VectorStoreIndex


class SubQuestionQueryEngine:
    def __init__(self, vector_index: VectorStoreIndex) -> None:
        self.engine = vector_index.as_query_engine(similarity_top_k=1)

    def query(self, complex_q: str) -> QueryResponse:
        sub_qs = [s.strip() for s in re.split(r"以及|另外|[，,；;]", complex_q) if len(s.strip()) >= 4]
        answers: List[str] = []
        all_nodes = []
        for idx, sq in enumerate(sub_qs, start=1):
            r = self.engine.query(sq)
            answers.append(f"子问题{idx}({sq}) -> {r.source_nodes[0].node.text}")
            all_nodes.extend(r.source_nodes)
        return QueryResponse(response="\n".join(answers), source_nodes=all_nodes, routed_engine="sub_question")


if __name__ == "__main__":
    docs = [
        Document("北京出差酒店住宿上限每晚600元。", doc_id="fin", metadata={"source": "财务制度.md"}),
        Document("生产环境严禁周五17:00之后非紧急发版。", doc_id="dev", metadata={"source": "研发规范.md"}),
    ]
    sq_engine = SubQuestionQueryEngine(VectorStoreIndex.from_documents(docs))
    res = sq_engine.query("北京出差住宿上限多少，以及周五晚上能不能发版？")
    print(res.response)
    assert "600元" in res.response and "周五" in res.response

