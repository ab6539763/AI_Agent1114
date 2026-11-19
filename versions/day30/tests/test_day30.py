import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 30 自动化单元测试：端到端验证星辰企业知识库 RAG 命中、部门过滤与拒答兜底。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day30_kb_cli import build_starmind_kb, format_cli_response
from src.day30_rag_pipeline import FALLBACK_ANSWER


def test_rag_hit_and_citations(tmp_path):
    kb = build_starmind_kb(persist_dir=tmp_path)
    resp = kb.ask("去上海出差住酒店每晚报销上限是多少？")
    assert resp.is_fallback is False
    assert "600元" in resp.answer
    assert "[来源1]" in resp.answer
    assert len(resp.citations) >= 1
    assert resp.citations[0].source == "财务报销制度_2026.md"


def test_rag_dept_filter(tmp_path):
    kb = build_starmind_kb(persist_dir=tmp_path)
    resp = kb.ask("代码发布窗口规定是什么？", where={"dept": "研发部"})
    assert resp.is_fallback is False
    assert all(c.source == "研发工程规范_v3.md" for c in resp.citations)

    # 用错误的部门过滤应当触发拒答
    resp_wrong_dept = kb.ask("代码发布窗口规定是什么？", where={"dept": "财务部"})
    assert resp_wrong_dept.is_fallback is True


def test_rag_out_of_domain_fallback(tmp_path):
    kb = build_starmind_kb(persist_dir=tmp_path)
    resp = kb.ask("量子纠缠与相对论的数学推导过程是什么？")
    assert resp.is_fallback is True
    assert resp.answer == FALLBACK_ANSWER
    assert resp.citations == []
    card = format_cli_response(resp)
    assert "兜底拒答" in card

