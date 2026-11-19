import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 35 自动化单元测试：验证 LlamaIndex Node 链表、双索引路由与框架基准对比。"""

from src.day35_framework_benchmark import recommend_framework, run_framework_benchmark
from src.day35_llamaindex_core import (
    Document,
    RouterQueryEngine,
    SentenceNodeParser,
    SummaryIndex,
    VectorStoreIndex,
)


def test_sentence_node_parser_builds_doubly_linked_relationships():
    doc = Document("第一句规定标准。第二句补充例外。第三句说明审批。", doc_id="d_test")
    nodes = SentenceNodeParser(sentences_per_node=1).get_nodes_from_documents([doc])
    assert len(nodes) == 3
    assert nodes[0].relationships["SOURCE"] == "d_test"
    assert "PREVIOUS" not in nodes[0].relationships
    assert nodes[0].relationships["NEXT"] == nodes[1].node_id
    assert nodes[1].relationships["PREVIOUS"] == nodes[0].node_id
    assert nodes[1].relationships["NEXT"] == nodes[2].node_id
    assert nodes[2].relationships["PREVIOUS"] == nodes[1].node_id
    assert "NEXT" not in nodes[2].relationships


def test_router_query_engine_routes_vector_and_summary():
    doc = Document(
        "一线城市出差住宿上限每晚600元。上述标准同样适用于实习生。餐饮补助每天100元。",
        doc_id="fin01",
        metadata={"source": "差旅制度.md"},
    )
    vec_idx = VectorStoreIndex.from_documents([doc])
    sum_idx = SummaryIndex.from_documents([doc])
    router = RouterQueryEngine(
        vector_engine=vec_idx.as_query_engine(similarity_top_k=1, expand_prev_next=True),
        summary_engine=sum_idx.as_query_engine(response_mode="refine"),
    )

    detail_resp = router.query("实习生出差住宿适用什么标准？")
    assert detail_resp.routed_engine == "vector_index"
    assert "600元" in detail_resp.response and "实习生" in detail_resp.response

    summary_resp = router.query("请总结这份差旅制度的全部要点")
    assert summary_resp.routed_engine == "summary_index"
    assert "600元" in summary_resp.response and "100元" in summary_resp.response


def test_framework_benchmark_shows_node_router_advantage():
    rows = run_framework_benchmark()
    by_name = {r.framework: r for r in rows}
    assert by_name["LlamaIndex_NodeRouter"].completeness_rate > by_name["LangChain_Flat_RAG"].completeness_rate
    assert by_name["LlamaIndex_NodeRouter"].completeness_rate == 1.0

    rec = recommend_framework(need_multi_agent=True, heavy_doc_summary=True)
    assert "Hybrid" in rec["choice"]

