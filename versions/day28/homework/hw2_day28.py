"""
Day 28 课后作业 2（企业实战）：作业二：实现基于内容哈希的文档切片去重过滤器
工单：STARMIND-028
"""

"""Day 28 作业二参考答案：基于 SHA-256 的切片去重过滤器"""
import hashlib
import re
import sys
from pathlib import Path
from typing import List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document


def deduplicate_chunks(chunks: List[Document]) -> Tuple[List[Document], int]:
    seen: Set[str] = set()
    unique: List[Document] = []
    dup_count = 0
    for doc in chunks:
        normalized = re.sub(r"\s+", "", doc.page_content)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if digest in seen:
            dup_count += 1
            continue
        seen.add(digest)
        doc_copy = Document(page_content=doc.page_content, metadata={**doc.metadata, "content_hash": digest[:12]})
        unique.append(doc_copy)
    return unique, dup_count


if __name__ == "__main__":
    docs = [
        Document("一线城市住宿标准600元。", {"source": "a.md"}),
        Document("一线城市住宿标准 600元。\n", {"source": "a_copy.md"}),
        Document("餐补每天100元。", {"source": "b.md"}),
    ]
    uniq, dups = deduplicate_chunks(docs)
    print(f"去重前 {len(docs)} -> 去重后 {len(uniq)}，剔除重复 {dups} 条")
    assert len(uniq) == 2 and dups == 1

