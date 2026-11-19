"""
Day 32 课后作业 3（架构进阶）：作业三：实现子问题拆解与子答案汇总器（QueryDecomposition）
工单：STARMIND-032
"""

"""Day 32 作业三参考答案：跨部门复合问题拆解与汇总器"""
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day30_kb_cli import build_starmind_kb


def decompose_and_answer(kb, complex_query: str) -> Dict[str, Any]:
    parts = [p.strip() for p in re.split(r"[，,。；;]|另外|以及|还有", complex_query) if len(p.strip()) >= 4]
    sub_answers: List[str] = []
    all_sources: List[str] = []
    for idx, sub_q in enumerate(parts, start=1):
        resp = kb.ask(sub_q)
        sub_answers.append(f"【子问题{idx}：{sub_q}】\n{resp.answer}")
        for c in resp.citations:
            if c.source not in all_sources:
                all_sources.append(c.source)
    return {
        "sub_questions": parts,
        "combined_answer": "\n\n".join(sub_answers),
        "sources": all_sources,
    }


if __name__ == "__main__":
    kb = build_starmind_kb()
    kb.score_threshold = 0.12  # 短子问题场景适度放宽向量相似度阈值以保证跨部门召回
    out = decompose_and_answer(kb, "员工入职满一年有多少天年假，另外周五晚上能发布代码上线吗？")
    print("拆解子问题:", out["sub_questions"])
    print("涉及文档:", out["sources"])
    assert len(out["sources"]) >= 2

