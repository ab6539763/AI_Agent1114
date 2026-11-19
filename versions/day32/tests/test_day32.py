import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 32 自动化单元测试：验证 Query改写、MultiQuery、HyDE、上下文压缩与召回率提升。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day30_kb_cli import build_starmind_kb
from src.day32_compression_eval import ContextualCompressor, run_recall_comparison
from src.day32_query_transform import HyDERetriever, MultiQueryRetriever, QueryRewriter


def test_query_rewriter_and_multiquery():
    rw = QueryRewriter()
    out = rw.rewrite("礼拜五能不能推线上？")
    assert "周五" in out and "生产发布窗口" in out

    kb = build_starmind_kb()
    mq = MultiQueryRetriever(kb.vector_store, rw)
    sub_qs = mq.generate_queries("去魔都出差住店和吃饭怎么报销？")
    assert len(sub_qs) >= 3
    hits = mq.retrieve("去魔都出差住店和吃饭怎么报销？", k=2)
    sections = {d.metadata["section"] for d, _ in hits}
    assert "差旅住宿标准" in sections


def test_hyde_and_recall_improvement():
    report = run_recall_comparison(top_k=2)
    assert report["QueryRewriting"] >= report["Baseline_Naive"]
    assert report["MultiQuery"] >= report["Baseline_Naive"]
    assert report["HyDE"] >= 0.80


def test_contextual_compressor_saves_tokens():
    doc = Document(
        "园区班车每天早8点从地铁站发车。一线城市住宿上限每晚600元。周五下午茶在3楼茶水间领取。",
        {"source": "guide.md"},
    )
    comp = ContextualCompressor(max_sentences_per_doc=1)
    slim, saved = comp.compress_documents("一线城市住宿上限", [doc])
    assert saved > 0.4
    assert "600元" in slim[0].page_content
    assert "下午茶" not in slim[0].page_content

