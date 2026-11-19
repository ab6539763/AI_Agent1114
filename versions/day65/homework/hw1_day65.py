"""
Day 65 课后作业 1（基础巩固）：基础巩固：补充 2 道评委追问的标准应答条目
工单：STARMIND-065
"""

from src.day65_defense_planner import JUDGE_QA_BANK


def filter_qa_by_keyword(qa_bank: list[dict], keyword: str) -> list[dict]:
    return [q for q in qa_bank if keyword in q["topic"] or keyword in q["question"]]


hits = filter_qa_by_keyword(JUDGE_QA_BANK, "幻觉")
assert len(hits) == 1 and "RAG" in hits[0]["topic"]
print("追问库检索通过:", hits[0]["topic"])

