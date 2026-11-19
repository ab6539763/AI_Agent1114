import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-004 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day04_todo_manager import add_task, complete_task, remove_task, filter_tasks, summarize_tasks
from day04_tag_analyzer import normalize_tags, compare_tag_versions


def test_todo_crud_lifecycle():
    tasks = []
    t1 = add_task(tasks, "任务A")
    t2 = add_task(tasks, "任务B")
    assert t1 == (1, "任务A", False)
    assert t2 == (2, "任务B", False)

    assert complete_task(tasks, 1) is True
    assert complete_task(tasks, 999) is False
    assert summarize_tasks(tasks) == (2, 1, 1)
    assert len(filter_tasks(tasks, only_pending=True)) == 1

    assert remove_task(tasks, 1) is True
    assert remove_task(tasks, 1) is False
    assert summarize_tasks(tasks) == (1, 0, 1)

    with pytest.raises(ValueError):
        add_task(tasks, "   ")


def test_tag_analyzer():
    assert normalize_tags([" AI ", "ai", "", "LLM"]) == {"ai", "llm"}
    diff = compare_tag_versions(["Python", "Git"], ["python", "RAG"])
    assert diff["common"] == ["python"]
    assert diff["added"] == ["rag"]
    assert diff["removed"] == ["git"]
    assert diff["all_unique"] == ["git", "python", "rag"]

