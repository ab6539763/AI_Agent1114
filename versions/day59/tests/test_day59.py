import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 59 单元测试：配置中心、结构化日志与 SQLAlchemy 仓储底座"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from pydantic import ValidationError
from src.day59_core_infra import StarMindError, StarMindSettings, format_json_log, new_trace_id
from src.day59_db_repository import StarMindRepository


def test_settings_validation():
    cfg = StarMindSettings(rag_top_k=8, daily_budget_cny=200.0)
    assert cfg.rag_top_k == 8
    with pytest.raises(ValidationError):
        StarMindSettings(daily_budget_cny=-10.0)


def test_json_log_and_error_format():
    tid = new_trace_id()
    raw = format_json_log("warning", "high_latency", tid, {"ms": 1450})
    parsed = json.loads(raw)
    assert parsed["level"] == "WARNING"
    assert parsed["trace_id"] == tid

    err = StarMindError(4001, "参数缺失", 400, tid)
    assert err.to_dict()["code"] == 4001


def test_repository_session_messages_and_audit():
    repo = StarMindRepository("sqlite:///:memory:")
    repo.create_session("s1", "t1", "测试会话")
    m1 = repo.append_message("s1", "user", "你好", 5)
    m2 = repo.append_message("s1", "assistant", "您好，请问有什么可以帮您？", 14)
    assert m2 > m1
    hist = repo.get_history("s1")
    assert len(hist) == 2 and hist[0]["role"] == "user"
    repo.write_audit("tr-1", "t1", "rag_query", "ALLOW")
    assert repo.count_audits("t1") == 1

