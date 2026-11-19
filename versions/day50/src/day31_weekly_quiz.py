"""
Day 31 - 步骤一：第 4-5 周核心考点自动化实战周测引擎（满分 100 分）
覆盖：LCEL管道与容错解析、SQLite会话隔离、中文分块边界、向量元数据过滤、RAG防幻觉兜底
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day26_lcel_core import RunnableLambda
from src.day26_parsers_and_chain import JsonOutputParser
from src.day27_sqlite_history import SQLiteChatMessageHistory
from src.day28_loaders import Document
from src.day28_text_splitter import RecursiveCharacterTextSplitter
from src.day29_vector_store import StarMindVectorStore
from src.day30_kb_cli import build_starmind_kb


@dataclass
class QuizResult:
    name: str
    passed: bool
    score: int
    detail: str


def _check_lcel_and_json() -> QuizResult:
    chain = RunnableLambda(lambda x: f'分析结果：```json\n{{"topic": "{x}", "ok": true}}\n```') | JsonOutputParser()
    out = chain.invoke("RAG架构")
    ok = out == {"topic": "RAG架构", "ok": True}
    return QuizResult("考点1: LCEL管道与JSON容错解析", ok, 20 if ok else 0, f"输出={out}")


def _check_sqlite_isolation() -> QuizResult:
    with tempfile.TemporaryDirectory() as tmp:
        db = str(Path(tmp) / "quiz.db")
        s1 = SQLiteChatMessageHistory("emp_a", db_path=db)
        s2 = SQLiteChatMessageHistory("emp_b", db_path=db)
        s1.add_user_message("秘密项目代号：星辰X")
        ok = len(s1.messages) == 1 and len(s2.messages) == 0
    return QuizResult("考点2: SQLite多会话隔离持久化", ok, 20 if ok else 0, "不同session_id严格零串台")


def _check_chinese_splitter() -> QuizResult:
    text = "第一条差旅规则说明住宿上限。第二条规则说明餐补标准。第三条规则说明交通报销流程。"
    chunks = RecursiveCharacterTextSplitter(chunk_size=18, chunk_overlap=4).split_text(text)
    ok = len(chunks) >= 3 and all(len(c) <= 18 for c in chunks)
    return QuizResult("考点3: 中文递归分块长度与断句", ok, 20 if ok else 0, f"切片数={len(chunks)}")


def _check_vector_where_filter() -> QuizResult:
    vs = StarMindVectorStore()
    vs.add_documents([
        Document("财务部：一线城市住宿600元", {"dept": "财务部"}),
        Document("研发部：周五禁止发布代码", {"dept": "研发部"}),
    ])
    hits = vs.similarity_search("住宿标准", k=2, where={"dept": "研发部"})
    ok = len(hits) == 1 and hits[0].metadata["dept"] == "研发部"
    return QuizResult("考点4: 向量数据库元数据where过滤", ok, 20 if ok else 0, f"命中部门={hits[0].metadata['dept']}")


def _check_rag_grounded_and_fallback() -> QuizResult:
    kb = build_starmind_kb()
    r1 = kb.ask("一线城市出差住宿上限是多少？")
    r2 = kb.ask("火星表面的大气压强是多少帕斯卡？")
    ok = (not r1.is_fallback) and ("600元" in r1.answer) and r2.is_fallback
    return QuizResult("考点5: RAG精准命中与库外拒答兜底", ok, 20 if ok else 0, f"库内命中={not r1.is_fallback}, 库外拒答={r2.is_fallback}")


def run_weekly_quiz() -> List[QuizResult]:
    checks: List[Callable[[], QuizResult]] = [
        _check_lcel_and_json,
        _check_sqlite_isolation,
        _check_chinese_splitter,
        _check_vector_where_filter,
        _check_rag_grounded_and_fallback,
    ]
    return [fn() for fn in checks]


if __name__ == "__main__":
    results = run_weekly_quiz()
    total = sum(r.score for r in results)
    print("=== 第 4-5 周实战周测成绩单 ===")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.name} ({r.score}/20) -> {r.detail}")
    print(f"总分: {total} / 100")

