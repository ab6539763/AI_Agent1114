import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 47 自动化单元测试：验证真实 SQLite 销售库 Text-to-SQL、防注入拦截及浏览器/代码助手原型。"""

import pytest
from src.day47_text2sql_agent import SQLSafetyError, TextToSQLAgent, init_sales_sqlite_db
from src.day47_browser_code_agent import BrowserDOMPlanner, CodingAssistantPrototype, DOMElement


def test_text2sql_queries_real_sqlite_and_self_corrects():
    conn = init_sales_sqlite_db()
    agent = TextToSQLAgent(conn, default_limit=50)

    res_region = agent.analyze("统计各区域有效销售额（模拟纠错）")
    assert res_region["retries"] == 1
    assert "LIMIT 50" in res_region["sql"]
    # 华东有效已支付订单应为 150000 + 120000 = 270000（不含 40000 的 CANCELLED 退单）
    assert res_region["rows"][0]["region"] == "华东"
    assert res_region["rows"][0]["total_sales"] == 270000.0

    res_prod = agent.analyze("最畅销的商品是什么")
    assert res_prod["rows"][0]["product_name"] == "星辰智脑企业版"
    assert res_prod["rows"][0]["total_sales"] == 250000.0
    conn.close()


@pytest.mark.parametrize(
    "malicious_sql",
    [
        "DROP TABLE sales_orders",
        "DELETE FROM sales_orders WHERE order_id = 101",
        "SELECT * FROM products; DROP TABLE products",
        "SELECT * FROM products -- 注释绕过",
        "PRAGMA query_only = OFF",
    ],
)
def test_text2sql_blocks_injection_and_writes(malicious_sql: str):
    conn = init_sales_sqlite_db()
    agent = TextToSQLAgent(conn)
    with pytest.raises(SQLSafetyError):
        agent.analyze(malicious_sql)
    conn.close()


def test_browser_planner_and_coding_assistant():
    planner = BrowserDOMPlanner()
    compact = planner.compress_dom(
        [
            DOMElement(1, "div", "text", "噪音", visible=True, interactive=False),
            DOMElement(2, "input", "textbox", "搜索框", visible=True, interactive=True),
            DOMElement(3, "button", "button", "查询", visible=True, interactive=True),
        ]
    )
    assert len(compact) == 2
    actions = planner.plan_actions("查询 订单101", compact)
    assert [a["action"] for a in actions] == ["type", "click"]

    coder = CodingAssistantPrototype()
    res = coder.fix_zero_division_bug("def avg(total, count):\n    return total / count\n")
    assert res["changed"] is True
    assert "-    return total / count" in res["diff"]
    assert "+    return total / count if count else 0.0" in res["diff"]

