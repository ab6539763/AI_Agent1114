import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 33 自动化单元测试：验证 BM25、RRF 混合检索、bge-reranker 精排与父文档检索器。"""

from src.day33_hybrid_rrf import (
    BM25Index,
    DenseVectorIndex,
    Document,
    HybridRRFRetriever,
    build_enterprise_sample_docs,
)
from src.day33_rerank_parent import BGERerankerSimulator, ParentDocumentRetriever


def test_bm25_exact_error_code_and_hybrid_rrf():
    docs = build_enterprise_sample_docs()
    bm25 = BM25Index()
    dense = DenseVectorIndex()
    bm25.add_documents(docs)
    dense.add_documents(docs)
    hybrid = HybridRRFRetriever(bm25, dense, rrf_k=60)

    # 1. 错误码精确查询：BM25 与 Hybrid RRF 均应把 ops-5042 排第 1
    bm25_top1 = bm25.search("ERR-5042 报错怎么排查", k=1)[0][0]
    rrf_top1 = hybrid.retrieve("ERR-5042 报错怎么排查", top_k=1)[0][0]
    assert bm25_top1.doc_id == "ops-5042"
    assert rrf_top1.doc_id == "ops-5042"

    # 2. 内部项目代号查询：应精准命中天枢项目
    proj_top1 = hybrid.retrieve("天枢项目预算找谁审批？", top_k=1)[0][0]
    assert proj_top1.doc_id == "proj-tianshu"

    # 3. 口语语义查询：应精准命中差旅住宿标准
    sem_top1 = hybrid.retrieve("去魔都出差住店报销上限是多少", top_k=1)[0][0]
    assert sem_top1.doc_id == "fin-hotel"


def test_bge_reranker_promotes_exact_answer():
    reranker = BGERerankerSimulator()
    candidates = [
        Document("公司行政部负责园区物业、工位分配与班车管理。", {"section": "行政总览"}),
        Document("错误码 ERR-5042 属于统一网关超时，需优先检查上游推理服务显存并调整超时阈值。", {"section": "ERR-5042排查"}),
        Document("差旅报销需要上传电子发票到财务系统。", {"section": "财务流程"}),
    ]
    ranked = reranker.rerank("ERR-5042 网关超时排查方法", candidates, top_n=2)
    assert "ERR-5042" in ranked[0][0].page_content
    assert ranked[0][1] > ranked[1][1]
    assert 0.0 <= ranked[0][1] <= 1.0


def test_parent_document_retriever_deduplicates_and_returns_full_parent():
    p1 = Document(
        "【网关排障】遇到 ERR-5042 超时故障时：第一步查 Grafana 显存；"
        "第二步调大 proxy_read_timeout；第三步开启降级熔断并通知值班架构师。",
        {"doc_id": "P1", "section": "ERR-5042"},
    )
    p2 = Document(
        "【休假规范】入职满 1 年享 5 天年假，病假超 2 天须附公立医院诊断证明。",
        {"doc_id": "P2", "section": "休假规定"},
    )
    retriever = ParentDocumentRetriever(child_chunk_size=30, child_chunk_overlap=8, use_rerank=True)
    child_count = retriever.add_parent_documents([p1, p2])
    assert child_count >= 4

    results = retriever.retrieve_parents("ERR-5042 故障第三步怎么处置？", top_k=2)
    assert len(results) >= 1
    top_doc, score = results[0]
    assert top_doc.doc_id == "P1"
    assert "第一步" in top_doc.page_content and "第三步开启降级熔断" in top_doc.page_content
    # 确保 parent_id 无重复
    returned_ids = [d.doc_id for d, _ in results]
    assert len(returned_ids) == len(set(returned_ids))

