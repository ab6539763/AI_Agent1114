import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-010 自动化单元测试（含故障注入）。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day10_exceptions import StarMindError, RateLimitError, ModelTimeoutError, AuthError
from day10_resilient_runner import call_with_fallback, audit_requirements_text


def test_primary_success():
    res = call_with_fallback(lambda p: f"P:{p}", lambda p: f"F:{p}", "hi")
    assert res["channel"] == "primary"
    assert res["reply"] == "P:hi"
    assert res["audit_events"] == ["try_primary", "primary_ok", "audit_closed"]


def test_fallback_on_rate_limit_and_timeout():
    def fail_429(_p):
        raise RateLimitError("too many requests")

    def fail_504(_p):
        raise ModelTimeoutError("gateway timeout")

    r1 = call_with_fallback(fail_429, lambda p: f"BACKUP:{p}", "hello")
    assert r1["channel"] == "fallback"
    assert "fallback_on_E429" in r1["audit_events"]

    r2 = call_with_fallback(fail_504, lambda p: f"BACKUP:{p}", "hello")
    assert r2["channel"] == "fallback"
    assert "fallback_on_E504" in r2["audit_events"]


def test_auth_error_never_falls_back():
    def fail_401(_p):
        raise AuthError("invalid key")

    with pytest.raises(AuthError) as exc_info:
        call_with_fallback(fail_401, lambda p: "should not run", "hello")
    assert exc_info.value.to_error_dict()["error_code"] == "E401"


def test_audit_requirements_text():
    res = audit_requirements_text("# comment\npytest==8.3.0\nhttpx\n")
    assert res["pinned"] == ["pytest==8.3.0"]
    assert res["unpinned"] == ["httpx"]

