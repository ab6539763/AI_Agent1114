import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-007 第一周综合验收测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day07_week1_quiz import grade_quiz
from day07_contacts_app import (
    load_contacts,
    save_contacts,
    upsert_contact,
    delete_contact,
    search_contacts,
    summarize_by_dept,
)


def test_week1_quiz_grading():
    res = grade_quiz({"Q1": "True", "Q2": "set()", "Q3": "Star", "Q4": "ensure_ascii", "Q5": "None"})
    assert res["score"] == 100
    assert res["passed"] is True

    partial = grade_quiz({"Q1": "False"})
    assert partial["passed"] is False
    assert len(partial["wrong_details"]) == 5


def test_contacts_full_lifecycle_and_json_persistence(tmp_path: Path):
    db_file = tmp_path / "data" / "contacts.json"
    # 首次加载文件不存在应返回空字典
    book = load_contacts(db_file)
    assert book == {}

    upsert_contact(book, "xm-001", "老陈", "AI研发部", "13857101111", ["Python", "python", "LLM"])
    upsert_contact(book, "xm-002", "阿杰", "测试部", "13957102222", ["Pytest"])
    assert book["XM-001"]["masked_phone"] == "138****1111"
    assert book["XM-001"]["skills"] == ["llm", "python"]

    # 持久化并模拟重启重新加载
    save_contacts(db_file, book)
    reloaded = load_contacts(db_file)
    assert len(reloaded) == 2
    assert len(search_contacts(reloaded, "研发")) == 1
    assert summarize_by_dept(reloaded) == {"AI研发部": 1, "测试部": 1}

    assert delete_contact(reloaded, "XM-002") is True
    assert delete_contact(reloaded, "XM-999") is False

    with pytest.raises(ValueError):
        upsert_contact(reloaded, "", "无名", "部门", "13800000000")

