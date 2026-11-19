"""
Day 28 课后作业 3（架构进阶）：作业三：实现保护代码块的 Markdown 智能分块器
工单：STARMIND-028
"""

"""Day 28 作业三参考答案：保护代码块完整性的 Markdown 分块器"""
import re
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_text_splitter import RecursiveCharacterTextSplitter


class CodeAwareMarkdownSplitter:
    CODE_BLOCK_RE = re.compile(r"(```[\s\S]*?```)")

    def __init__(self, chunk_size: int = 120, chunk_overlap: int = 20) -> None:
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split_text(self, md_text: str) -> List[str]:
        segments = self.CODE_BLOCK_RE.split(md_text)
        chunks: List[str] = []
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            if seg.startswith("```") and seg.endswith("```"):
                # 代码块整体保留，绝不拦腰切断
                chunks.append(seg)
            else:
                chunks.extend(self._text_splitter.split_text(seg))
        return chunks


if __name__ == "__main__":
    md = (
        "星辰后端要求所有接口必须使用 Pydantic 校验。\n"
        "```python\nclass QueryReq(BaseModel):\n    question: str\n    top_k: int = 5\n```\n"
        "发布前必须通过全部单元测试。"
    )
    splitter = CodeAwareMarkdownSplitter(chunk_size=30, chunk_overlap=5)
    result = splitter.split_text(md)
    for i, c in enumerate(result):
        print(f"[{i}] {c!r}")
    assert any("class QueryReq" in c and c.endswith("```") for c in result)

