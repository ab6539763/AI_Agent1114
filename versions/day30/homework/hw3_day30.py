"""
Day 30 课后作业 3（架构进阶）：作业三：实现上下文 Token 预算自适应截断组装器
工单：STARMIND-030
"""

"""Day 30 作业三参考答案：预算感知的 RAG 上下文装箱器"""
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document


def pack_context_within_budget(
    hits: List[Tuple[Document, float]],
    max_chars: int = 200,
) -> Tuple[str, int]:
    blocks: List[str] = []
    used = 0
    for idx, (doc, score) in enumerate(hits, start=1):
        block = f"[来源{idx}] ({doc.metadata.get('source', 'doc')}): {doc.page_content}"
        if not blocks and len(block) > max_chars:
            blocks.append(block[:max_chars])
            break
        if used + len(block) > max_chars:
            break
        blocks.append(block)
        used += len(block)
    return "\n\n".join(blocks), len(blocks)


if __name__ == "__main__":
    sample_hits = [
        (Document("一线城市住宿上限600元，新一线480元，需提前在OA审批通过。" * 2, {"source": "a.md"}), 0.9),
        (Document("餐饮补助按每天100元定额发放，无需提供餐饮发票。" * 2, {"source": "b.md"}), 0.8),
        (Document("市内交通实报实销，单次超过150元需备注说明。" * 2, {"source": "c.md"}), 0.7),
    ]
    ctx, kept = pack_context_within_budget(sample_hits, max_chars=160)
    print(f"保留切片数: {kept}, 总字符数: {len(ctx)}\n{ctx}")
    assert kept < len(sample_hits) and len(ctx) <= 165

