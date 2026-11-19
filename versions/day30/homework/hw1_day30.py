"""
Day 30 课后作业 1（基础巩固）：作业一：实现引用编号一致性校验器（CitationVerifier）
工单：STARMIND-030
"""

"""Day 30 作业一参考答案：防伪造引用一致性校验器"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day30_rag_pipeline import Citation, RAGResponse


def verify_citations(resp: RAGResponse) -> Tuple[bool, List[int]]:
    cited_ids = [int(x) for x in re.findall(r"\[来源(\d+)\]", resp.answer)]
    valid_ids = {c.ref_id for c in resp.citations}
    invalid = sorted({cid for cid in cited_ids if cid not in valid_ids})
    return (len(invalid) == 0), invalid


if __name__ == "__main__":
    good = RAGResponse("q", "一线城市上限600元 [来源1]。", [Citation(1, "fin.md", "差旅", 0.8, "...")])
    bad = RAGResponse("q", "一线城市上限600元 [来源1]，且周末双倍补贴 [来源9]。", [Citation(1, "fin.md", "差旅", 0.8, "...")])
    assert verify_citations(good) == (True, [])
    assert verify_citations(bad) == (False, [9])
    print("引用一致性校验通过！伪造引用 [来源9] 已被精准拦截。")

