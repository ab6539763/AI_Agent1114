"""
Day 28 课后作业 1（基础巩固）：作业一：实现 Markdown 标题上下文注入器（Context-Enriched Splitter）
工单：STARMIND-028
"""

"""Day 28 作业一参考答案：切片标题上下文自动注入器"""
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document, MarkdownLoader


def enrich_chunks_with_headers(chunks: List[Document]) -> List[Document]:
    enriched: List[Document] = []
    for doc in chunks:
        source = doc.metadata.get("source", "未知文档")
        section = doc.metadata.get("section", "正文")
        prefix = f"【来源：{source} | 章节：{section}】\n"
        content = doc.page_content if doc.page_content.startswith("【来源：") else prefix + doc.page_content
        enriched.append(Document(page_content=content, metadata=dict(doc.metadata)))
    return enriched


if __name__ == "__main__":
    raw = MarkdownLoader().load_text("# 年假管理制度\n需提前3个工作日提交OA申请。", source="HR手册.md")
    result = enrich_chunks_with_headers(raw)
    print(result[0].page_content)
    assert "年假管理制度" in result[0].page_content

