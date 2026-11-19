import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-005 自动化单元测试。"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day05_dict_utils import safe_get_path, merge_model_config
from day05_json_api_parser import (
    MOCK_API_RESPONSE_JSON,
    parse_llm_response,
    save_audit_record,
    load_audit_record,
)


def test_safe_get_path_and_merge():
    data = {"a": [{"b": "ok"}]}
    assert safe_get_path(data, "a.0.b") == "ok"
    assert safe_get_path(data, "a.5.b", "fallback") == "fallback"
    assert safe_get_path(data, "x.y", None) is None

    merged = merge_model_config({"temp": 0.7, "top_p": 0.9}, {"temp": 0.1, "top_p": None})
    assert merged == {"temp": 0.1, "top_p": 0.9}


def test_parse_llm_response_variants():
    ok_res = parse_llm_response(MOCK_API_RESPONSE_JSON)
    assert ok_res["ok"] is True
    assert ok_res["total_tokens"] == 170
    assert "顺丰" in ok_res["reply"]

    bad_res = parse_llm_response("{not valid json")
    assert bad_res["ok"] is False
    assert "JSON 解析失败" in bad_res["error"]

    err_res = parse_llm_response(json.dumps({"error": {"message": "rate limit exceeded"}}))
    assert err_res["ok"] is False
    assert "rate limit" in err_res["error"]


def test_json_save_and_load_roundtrip(tmp_path: Path):
    record = parse_llm_response(MOCK_API_RESPONSE_JSON)
    target = tmp_path / "logs" / "audit.json"
    save_audit_record(record, target)
    raw_text = target.read_text(encoding="utf-8")
    assert "顺丰" in raw_text  # 确保未转义为 \\uXXXX
    reloaded = load_audit_record(target)
    assert reloaded == record

