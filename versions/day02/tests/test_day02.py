import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-002 自动化单元测试。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day02_text_cleaner import clean_ticket_text, has_blocked_content
from day02_prompt_template import estimate_tokens_rough, render_support_prompt


def test_clean_ticket_text_whitespace_and_order_id():
    raw = " \u3000订单\t ord-10086 \n\n  未发货  "
    assert clean_ticket_text(raw) == "订单 ORD-10086 未发货"
    assert clean_ticket_text("") == ""


def test_clean_ticket_text_truncation():
    long_text = "星辰智脑" * 20  # 80 字符
    result = clean_ticket_text(long_text, max_length=15)
    assert len(result) == 15
    assert result.endswith("...")


def test_blocked_content_detection():
    assert has_blocked_content("你好请问支持刷单吗") is True
    assert has_blocked_content("请问发票怎么开") is False


def test_render_support_prompt_and_token_estimate():
    prompt = render_support_prompt("  查一下 ord-777  ", customer_tier="vip", max_reply_words=100)
    assert "VIP" in prompt
    assert "ORD-777" in prompt
    assert '{"intent":' in prompt
    assert estimate_tokens_rough(prompt) > 20
    assert render_support_prompt("点这个木马链接领取") .startswith("[BLOCKED]")

