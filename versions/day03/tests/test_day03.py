import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-003 自动化单元测试。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day03_ticket_router import route_single_ticket, process_ticket_batch
from day03_cli_menu import build_multiplication_table, play_guess_number, run_cli_menu


def test_route_single_ticket():
    assert route_single_ticket("   ", 0, False) == "INVALID"
    assert route_single_ticket("我要投诉服务差", 10, False) == "L3_HUMAN"
    assert route_single_ticket("大额订单异常", 6000, False) == "L3_HUMAN"
    assert route_single_ticket("普通咨询", 100, True) == "L2_FLAGSHIP_LLM"
    assert route_single_ticket("查物流", 50, False) == "L1_FAST_LLM"


def test_batch_circuit_breaker():
    batch = [
        {"text": "正常问题", "amount": 10, "is_vip": False},
        {"text": "", "amount": 0, "is_vip": False},
        {"text": "ATTACK_PAYLOAD_999", "amount": 0, "is_vip": False},
        {"text": "熔断后不应被处理", "amount": 9999, "is_vip": True},
    ]
    res = process_ticket_batch(batch)
    assert res["L1_FAST_LLM"] == 1
    assert res["skipped"] == 1
    assert res["circuit_broken"] is True
    assert res["completed_cleanly"] is False
    assert res["L3_HUMAN"] == 0


def test_multiplication_and_guess_and_cli():
    table = build_multiplication_table(9)
    assert "9x9=81" in table
    assert len(table.splitlines()) == 9

    won, logs = play_guess_number(secret=50, guesses=[25, 75, 50])
    assert won is True
    assert len(logs) == 3

    lost, _ = play_guess_number(secret=50, guesses=[1, 2, 3], max_attempts=2)
    assert lost is False

    out = run_cli_menu(["1", "2", "unknown", "q", "1"])
    assert len(out) == 4  # q 之后的 '1' 不应执行
    assert "安全退出" in out[-1]

