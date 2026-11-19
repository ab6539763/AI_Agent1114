"""
Day 28 - 步骤二：中文递归分块器（RecursiveCharacterTextSplitter）与参数调优实验
对应生产包：langchain_text_splitters.RecursiveCharacterTextSplitter
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document


class RecursiveCharacterTextSplitter:
    """
    中文增强版递归字符文本分割器：
    按语义优先级（段落 -> 换行 -> 句末标点 -> 逗号 -> 字符）递归切分，
    并通过 chunk_overlap 保持相邻切片的上下文连贯性。
    """

    DEFAULT_ZH_SEPARATORS = ["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""]

    def __init__(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 30,
        separators: Sequence[str] | None = None,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size 必须大于 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap 必须满足 0 <= chunk_overlap < chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = list(separators) if separators is not None else list(self.DEFAULT_ZH_SEPARATORS)

    def _split_with_separator(self, text: str, sep: str) -> List[str]:
        """按分隔符切分，并将标点分隔符保留在前一段末尾，保护中文句末标点。"""
        if sep == "":
            return list(text)
        raw_parts = text.split(sep)
        pieces: List[str] = []
        for idx, part in enumerate(raw_parts):
            if idx < len(raw_parts) - 1:
                pieces.append(part + sep)
            elif part:
                pieces.append(part)
        return [p for p in pieces if p]

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text.strip()] if text.strip() else []

        # 找到第一个在当前文本中出现的分隔符
        chosen_sep = ""
        remaining_seps: List[str] = []
        for i, sep in enumerate(separators):
            if sep == "" or sep in text:
                chosen_sep = sep
                remaining_seps = separators[i + 1 :]
                break

        splits = self._split_with_separator(text, chosen_sep)
        final_chunks: List[str] = []
        good_splits: List[str] = []

        for piece in splits:
            if len(piece) <= self.chunk_size:
                good_splits.append(piece)
            else:
                if good_splits:
                    final_chunks.extend(self._merge_splits(good_splits))
                    good_splits = []
                if remaining_seps:
                    final_chunks.extend(self._recursive_split(piece, remaining_seps))
                else:
                    # 最终定长硬切兜底
                    step = self.chunk_size - self.chunk_overlap
                    for start in range(0, len(piece), step):
                        sub = piece[start : start + self.chunk_size].strip()
                        if sub:
                            final_chunks.append(sub)
        if good_splits:
            final_chunks.extend(self._merge_splits(good_splits))
        return final_chunks

    def _merge_splits(self, splits: List[str]) -> List[str]:
        """将细粒度片段合并为接近 chunk_size 的块，并保留 chunk_overlap 重叠尾部。"""
        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for piece in splits:
            piece_len = len(piece)
            if current and current_len + piece_len > self.chunk_size:
                chunk_text = "".join(current).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                # 从末尾回溯保留不超过 chunk_overlap 的上下文片段
                overlap_buf: List[str] = []
                overlap_len = 0
                for prev in reversed(current):
                    if overlap_len + len(prev) <= self.chunk_overlap or not overlap_buf:
                        if overlap_len + len(prev) <= self.chunk_size - piece_len:
                            overlap_buf.insert(0, prev)
                            overlap_len += len(prev)
                        else:
                            break
                    else:
                        break
                current = overlap_buf
                current_len = overlap_len
            current.append(piece)
            current_len += piece_len

        if current:
            chunk_text = "".join(current).strip()
            if chunk_text:
                chunks.append(chunk_text)
        return chunks

    def split_text(self, text: str) -> List[str]:
        return self._recursive_split(text.strip(), self.separators)

    def split_documents(self, documents: Sequence[Document]) -> List[Document]:
        """批量切分 Document 列表，并自动注入 chunk_index、start_index 等溯源元数据。"""
        result: List[Document] = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            cursor = 0
            for idx, chunk_text in enumerate(chunks):
                pos = doc.page_content.find(chunk_text[:20], max(0, cursor - self.chunk_overlap))
                if pos != -1:
                    cursor = pos
                meta = {
                    **doc.metadata,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "start_index": pos if pos != -1 else 0,
                    "chunk_length": len(chunk_text),
                }
                result.append(Document(page_content=chunk_text, metadata=meta))
        return result


def run_chunking_experiment(sample_text: str) -> List[Dict[str, Any]]:
    """对比多组 chunk_size / chunk_overlap 参数的切片质量指标。"""
    configs = [
        (80, 15),
        (140, 25),
        (220, 40),
    ]
    report: List[Dict[str, Any]] = []
    for size, overlap in configs:
        splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
        chunks = splitter.split_text(sample_text)
        # 统计以中文句末标点结尾的切片比例（衡量断句完整度）
        clean_endings = sum(1 for c in chunks if c[-1] in "。！？；")
        total_chars = sum(len(c) for c in chunks)
        report.append({
            "chunk_size": size,
            "chunk_overlap": overlap,
            "num_chunks": len(chunks),
            "avg_len": round(total_chars / max(1, len(chunks)), 1),
            "clean_sentence_ratio": round(clean_endings / max(1, len(chunks)), 2),
            "overhead_ratio": round(total_chars / max(1, len(sample_text)), 2),
        })
    return report


if __name__ == "__main__":
    HANDBOOK = (
        "第一章 杭州星辰数科差旅报销制度。员工因公出差前须在OA系统提交出差申请，经直属主管审批通过后方可订票。"
        "一线城市（北京、上海、深圳、广州）酒店住宿标准为每晚不超过600元，新一线城市（杭州、南京、成都、武汉）每晚不超过480元。"
        "餐饮补助按每天100元定额发放，无需提供餐饮发票。\n\n"
        "第二章 研发代码发布规范。所有后端服务合并到 main 分支前，必须在 GitLab 发起 Merge Request，至少经过一位架构师或高级工程师 Review 通过。"
        "CI 流水线需保证 pytest 单元测试通过率达到100%，严禁在周五17:00之后向生产环境执行非紧急发布！"
    )
    print("=== 分块参数调优实验报告 ===")
    for row in run_chunking_experiment(HANDBOOK):
        print(row)

    docs = [Document(page_content=HANDBOOK, metadata={"source": "星辰员工手册.md", "dept": "综合"})]
    chunks = RecursiveCharacterTextSplitter(chunk_size=140, chunk_overlap=25).split_documents(docs)
    print(f"\n最佳配置切分预览（共 {len(chunks)} 块）：")
    for c in chunks:
        print(f"  [Chunk {c.metadata['chunk_index']}] len={c.metadata['chunk_length']} | {c.page_content}")

