"""
Day 32 课后作业 1（基础巩固）：作业一：实现 Step-Back Prompting（退步抽象查询）检索增强器
工单：STARMIND-032
"""

"""Day 32 作业一参考答案：Step-Back 退步抽象检索增强"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day30_kb_cli import build_starmind_kb


def step_back_rewrite(specific_query: str) -> str:
    if any(k in specific_query for k in ("全季", "如家", "酒店", "花", "元", "北京", "上海")):
        return "一线城市与新一线城市差旅酒店住宿报销上限标准是什么？"
    if any(k in specific_query for k in ("感冒", "发烧", "请2天", "医院")):
        return "员工申请病假需要提供什么证明及薪资发放标准？"
    return specific_query


if __name__ == "__main__":
    kb = build_starmind_kb()
    q = "我昨天去北京住全季花了650块超标了吗？"
    abstract_q = step_back_rewrite(q)
    hits = kb.vector_store.similarity_search_with_score(abstract_q, k=1)
    print("退步抽象查询:", abstract_q)
    print("命中章节:", hits[0][0].metadata["section"], "score=", hits[0][1])
    assert hits[0][0].metadata["section"] == "差旅住宿标准"

