import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 22 自动化单元测试：验证企业聊天前端生成、HTML闭合平衡与XSS安全校验。"""

from pathlib import Path
from src.day22_frontend_builder import build_frontend_assets
from src.day22_frontend_validator import validate_frontend_bundle


def test_build_and_validate_enterprise_frontend(tmp_path: Path):
    assets = build_frontend_assets(tmp_path)
    assert assets["html"].exists()
    assert assets["css"].exists()
    assert assets["js"].exists()

    report = validate_frontend_bundle(tmp_path)
    assert report.passed is True
    assert report.errors == []
    assert {"chat-log", "chat-form", "chat-input", "send-btn"}.issubset(report.found_ids)


def test_validator_catches_xss_and_unclosed_html(tmp_path: Path):
    build_frontend_assets(tmp_path)
    # 故意注入不安全的 innerHTML 赋值与未闭合标签
    (tmp_path / "chat_app.js").write_text("fetch('/api/v1/chat/stream'); el.innerHTML = userText;", encoding="utf-8")
    (tmp_path / "index.html").write_text("<html><body><div id='chat-log'>未闭合</body></html>", encoding="utf-8")

    report = validate_frontend_bundle(tmp_path)
    assert report.passed is False
    assert any("innerHTML" in err for err in report.errors)
    assert any("标签" in err for err in report.errors)

