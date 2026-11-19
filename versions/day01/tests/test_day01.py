import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-001 自动化单元测试（阿杰验收脚本）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day01_env_check import check_environment, format_env_report
from day01_profile_card import mask_phone, calculate_token_quota, build_profile_card


def test_env_check_passes():
    report = check_environment()
    assert report["is_compatible"] is True
    assert "tsinghua" in report["recommended_mirror"]
    text = format_env_report(report)
    assert "[PASS]" in text


def test_mask_phone_normal_and_invalid():
    assert mask_phone("13857108899") == "138****8899"
    assert mask_phone(" 13900001234 ") == "139****1234"
    assert mask_phone("12345") == "格式异常(已隐藏)"


def test_calculate_token_quota():
    # 0.5 年经验 + AI 团队: (50000 + 5000) * 1.5 = 82500
    assert calculate_token_quota(0.5, True) == 82500
    # 2 年经验 + 非 AI 团队: (50000 + 20000) * 1.0 = 70000
    assert calculate_token_quota(2.0, False) == 70000
    # 负数工龄防御
    assert calculate_token_quota(-3.0, False) == 50000


def test_build_profile_card_contains_masked_info():
    card = build_profile_card("林小星", 7, "产品部", "18612345678", 3.0, False)
    assert "XM-0007" in card
    assert "186****5678" in card
    assert "18612345678" not in card
    assert "80,000 Tokens" in card

