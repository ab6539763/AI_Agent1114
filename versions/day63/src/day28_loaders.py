"""
Day 28 - 步骤一：统一 Document 模型与多格式文档加载器（MD/HTML/CSV/DOCX/PDF）
对应生产包：langchain_core.documents / langchain_community.document_loaders
"""

from __future__ import annotations

import csv
import io
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Document:
    """统一文档片段模型，100% 对齐 langchain_core.documents.Document。"""

    page_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class _CleanHTMLParser(HTMLParser):
    """过滤 <script>/<style>/<nav> 标签，仅提取干净正文。"""

    SKIP_TAGS = {"script", "style", "noscript", "nav", "footer"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag.lower() in self.SKIP_TAGS:
            self._skip_depth += 1
        elif tag.lower() in {"p", "div", "br", "li", "h1", "h2", "h3", "tr"} and self._skip_depth == 0:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self._parts.append(text)

    def get_text(self) -> str:
        raw = " ".join(self._parts)
        raw = re.sub(r"[ \t]*\n[ \t]*", "\n", raw)
        return re.sub(r"\n{3,}", "\n\n", raw).strip()


class MarkdownLoader:
    """按一级/二级标题切分 Markdown，并把章节标题写入 metadata。"""

    def load_text(self, text: str, source: str = "inline.md") -> List[Document]:
        docs: List[Document] = []
        current_title = "概述"
        buffer: List[str] = []

        def flush() -> None:
            content = "\n".join(buffer).strip()
            if content:
                docs.append(
                    Document(
                        page_content=content,
                        metadata={"source": source, "doc_type": "markdown", "section": current_title},
                    )
                )

        for line in text.splitlines():
            heading = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
            if heading:
                flush()
                buffer = []
                current_title = heading.group(2).strip()
            else:
                buffer.append(line)
        flush()
        return docs

    def load(self, file_path: str | Path) -> List[Document]:
        path = Path(file_path)
        return self.load_text(path.read_text(encoding="utf-8"), source=path.name)


class HTMLLoader:
    """加载 HTML 并剥离脚本、样式与导航噪音。"""

    def load_text(self, html: str, source: str = "inline.html") -> List[Document]:
        parser = _CleanHTMLParser()
        parser.feed(html)
        clean_text = parser.get_text()
        return [Document(page_content=clean_text, metadata={"source": source, "doc_type": "html"})]

    def load(self, file_path: str | Path) -> List[Document]:
        path = Path(file_path)
        return self.load_text(path.read_text(encoding="utf-8"), source=path.name)


class CSVLoader:
    """将 CSV 每一行与表头拼接为语义完整的自然语言 Document，避免表头丢失。"""

    def load_text(self, csv_text: str, source: str = "inline.csv") -> List[Document]:
        reader = csv.DictReader(io.StringIO(csv_text.strip()))
        docs: List[Document] = []
        for row_idx, row in enumerate(reader, start=1):
            content = " | ".join(f"{k.strip()}: {(v or '').strip()}" for k, v in row.items() if k)
            docs.append(
                Document(
                    page_content=content,
                    metadata={"source": source, "doc_type": "csv", "row": row_idx},
                )
            )
        return docs


class DocxLoader:
    """零第三方依赖解析真实 .docx 文件（读取 ZIP 内 word/document.xml 段落）。"""

    W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    def load(self, file_path: str | Path) -> List[Document]:
        path = Path(file_path)
        paragraphs: List[str] = []
        with zipfile.ZipFile(path, "r") as zf:
            xml_bytes = zf.read("word/document.xml")
        root = ET.fromstring(xml_bytes)
        for p in root.iter(f"{self.W_NS}p"):
            texts = [t.text for t in p.iter(f"{self.W_NS}t") if t.text]
            joined = "".join(texts).strip()
            if joined:
                paragraphs.append(joined)
        return [
            Document(
                page_content="\n".join(paragraphs),
                metadata={"source": path.name, "doc_type": "docx", "paragraphs": len(paragraphs)},
            )
        ]


class PagePDFLoader:
    """
    分页 PDF 加载器（离线教学版按分页符 `\\f` 或 `---PAGE---` 模拟真实 PyPDFLoader 分页输出；
    生产环境直接替换为 langchain_community.document_loaders.PyPDFLoader 或 MinerU）。
    """

    def load_pages(self, raw_pages: List[str], source: str = "handbook.pdf") -> List[Document]:
        docs: List[Document] = []
        for page_num, content in enumerate(raw_pages, start=1):
            cleaned = re.sub(r"\n{3,}", "\n\n", content.strip())
            if cleaned:
                docs.append(
                    Document(
                        page_content=cleaned,
                        metadata={"source": source, "doc_type": "pdf", "page": page_num},
                    )
                )
        return docs


if __name__ == "__main__":
    md_docs = MarkdownLoader().load_text("# 报销制度\n差旅住宿一线城市上限600元。\n## 审批流程\n需直属主管审批。")
    html_docs = HTMLLoader().load_text("<html><script>alert(1)</script><body><h1>公告</h1><p>周五晚8点升级VPN。</p></body></html>")
    csv_docs = CSVLoader().load_text("城市,住宿上限,餐补\n杭州,500元,100元\n上海,600元,120元")
    pdf_docs = PagePDFLoader().load_pages(["第1页：员工入职满1年享5天年假。", "第2页：年假需提前3个工作日申请。"])

    for d in [*md_docs, *html_docs, *csv_docs, *pdf_docs]:
        print(f"[{d.metadata['doc_type']}] {d.metadata} -> {d.page_content}")

