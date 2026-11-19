import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 28 自动化单元测试：验证多格式文档加载器与中文递归分块器。"""

import sys
import zipfile
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import CSVLoader, DocxLoader, Document, HTMLLoader, MarkdownLoader, PagePDFLoader
from src.day28_text_splitter import RecursiveCharacterTextSplitter, run_chunking_experiment


def test_multi_format_loaders(tmp_path):
    # Markdown
    md = MarkdownLoader().load_text("# 年假\n满一年5天。\n## 病假\n需三甲医院证明。")
    assert len(md) == 2 and md[0].metadata["section"] == "年假" and md[1].metadata["section"] == "病假"

    # HTML 过滤脚本
    html = HTMLLoader().load_text("<html><style>.a{}</style><script>evil()</script><body><p>星辰公告</p></body></html>")
    assert html[0].page_content == "星辰公告"
    assert "evil" not in html[0].page_content

    # CSV 表头绑定
    csv_docs = CSVLoader().load_text("城市,上限\n杭州,480")
    assert "城市: 杭州" in csv_docs[0].page_content and "上限: 480" in csv_docs[0].page_content

    # 构造真实最小 .docx 文件测试 DocxLoader
    docx_path = tmp_path / "policy.docx"
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:r><w:t>星辰数科保密协议第一条</w:t></w:r></w:p></w:body></w:document>'
    )
    with zipfile.ZipFile(docx_path, "w") as zf:
        zf.writestr("word/document.xml", xml)
    docx_docs = DocxLoader().load(docx_path)
    assert "星辰数科保密协议第一条" in docx_docs[0].page_content

    # PDF 分页
    pdf_docs = PagePDFLoader().load_pages(["P1内容", "P2内容"])
    assert len(pdf_docs) == 2 and pdf_docs[1].metadata["page"] == 2


def test_chinese_recursive_splitter_and_experiment():
    text = "第一句是关于报销的详细规则说明。第二句说明一线城市住宿标准600元。第三句说明餐补每天100元。第四句说明审批流程需要主管确认。"
    splitter = RecursiveCharacterTextSplitter(chunk_size=45, chunk_overlap=10)
    docs = splitter.split_documents([Document(page_content=text, metadata={"source": "rule.md"})])
    assert len(docs) >= 3
    for idx, d in enumerate(docs):
        assert len(d.page_content) <= 45
        assert d.metadata["source"] == "rule.md"
        assert d.metadata["chunk_index"] == idx

    report = run_chunking_experiment(text * 2)
    assert len(report) == 3
    assert all(r["num_chunks"] >= 1 for r in report)

    with pytest.raises(ValueError):
        RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=50)

