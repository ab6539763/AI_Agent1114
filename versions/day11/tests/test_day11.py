import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-011 自动化单元测试。"""

import csv
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day11_regex_extractor import extract_entities, count_keywords
from day11_doc_scanner import scan_directory, export_reports


def test_regex_extraction_and_keywords():
    text = "联系 hr@starmind.cn 或 dev@starmind.cn，参考 starmind-008 和 STARMIND-011。Python 很好用，python！"
    ent = extract_entities(text)
    assert ent["emails"] == ["dev@starmind.cn", "hr@starmind.cn"]
    assert ent["tickets"] == ["STARMIND-008", "STARMIND-011"]
    assert count_keywords(text, ["Python", "Java"]) == {"Python": 2, "Java": 0}


def test_scan_directory_and_export_csv_json(tmp_path: Path):
    kb = tmp_path / "docs"
    (kb / "sub").mkdir(parents=True)
    (kb / "a.md").write_text("星辰智脑 RAG 方案 STARMIND-001", encoding="utf-8")
    (kb / "sub" / "b.txt").write_text("RAG 与 Agent 结合 dev@starmind.cn", encoding="utf-8")
    (kb / "ignore.bin").write_bytes(b"\x00\x01")  # 非文本文件应自动忽略

    summary = scan_directory(kb, ["RAG", "Agent"])
    assert summary["total_files"] == 2
    assert summary["global_keyword_totals"] == {"RAG": 2, "Agent": 1}

    out = export_reports(summary, tmp_path / "reports")
    loaded_json = json.loads(out["json"].read_text(encoding="utf-8"))
    assert loaded_json["total_files"] == 2

    with out["csv"].open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["file_name"] == "a.md"
    assert rows[1]["file_name"] == "sub/b.txt"

    with pytest.raises(FileNotFoundError):
        scan_directory(tmp_path / "not_exist", ["RAG"])

