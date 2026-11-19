import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 60 单元测试：混合检索 RAG + Rerank + 引用溯源"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day60_hybrid_retriever import KnowledgeChunk
from src.day60_rag_pipeline import StarMindRAGEngine

SAMPLE_KB = [
    KnowledgeChunk("DOC-01", "差旅住宿报销标准", "一线城市出差住宿上限650元/晚，需在费用中心上传电子专票核销。"),
    KnowledgeChunk("DOC-02", "网关错误码ERR_4291手册", "错误码ERR_4291表示部门日Token配额已触发100%硬熔断，请联系管理员提额。"),
    KnowledgeChunk("DOC-03", "新员工飞书SSO登录指引", "新员工需管理员同步组织架构并分配基础角色后方可飞书扫码登录。"),
]


def test_rag_hits_exact_error_code_with_citation():
    rag = StarMindRAGEngine(SAMPLE_KB)
    res = rag.ask("调用接口报错 ERR_4291 怎么解决？")
    assert res.answered is True
    assert res.citations[0].doc_id == "DOC-02"
    assert "[DOC-02]" in res.answer


def test_rag_hits_synonym_query():
    rag = StarMindRAGEngine(SAMPLE_KB)
    res = rag.ask("出差住宾馆最多花多少钱？")
    assert res.answered is True
    assert res.citations[0].doc_id == "DOC-01"


def test_rag_refuses_out_of_domain_question():
    rag = StarMindRAGEngine(SAMPLE_KB)
    res = rag.ask("宇宙大爆炸奇点密度如何计算？")
    assert res.answered is False
    assert res.citations == []

