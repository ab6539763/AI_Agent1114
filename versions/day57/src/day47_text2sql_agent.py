"""Day 47 - 步骤一：连接真实 SQLite 销售库的只读安全 Text-to-SQL 数据分析 Agent。"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union


class SQLSafetyError(ValueError):
    """当候选 SQL 违反只读安全策略或疑似注入攻击时抛出。"""


class SQLSafetyGuard:
    """应用层 SQL 只读安全守卫：仅允许单条 SELECT 查询，自动补齐 LIMIT。"""

    FORBIDDEN_KEYWORDS = re.compile(
        r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|PRAGMA|EXEC|UNION\s+ALL\s+SELECT\s+sqlite_master)\b",
        re.IGNORECASE,
    )
    COMMENT_PATTERN = re.compile(r"(--|/\*|\*/)")

    def __init__(self, default_limit: int = 100) -> None:
        self.default_limit = default_limit

    def sanitize_and_validate(self, sql: str) -> str:
        cleaned = sql.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()

        if not cleaned:
            raise SQLSafetyError("SQL 不能为空")
        if ";" in cleaned:
            raise SQLSafetyError("安全拦截：禁止多语句分号注入")
        if self.COMMENT_PATTERN.search(cleaned):
            raise SQLSafetyError("安全拦截：禁止 SQL 注释符绕过")
        if not re.match(r"^(SELECT|WITH)\b", cleaned, re.IGNORECASE):
            raise SQLSafetyError("安全拦截：仅允许执行只读 SELECT / WITH 查询")
        if self.FORBIDDEN_KEYWORDS.search(cleaned):
            raise SQLSafetyError("安全拦截：检测到写操作或高危系统关键字")

        # 自动补齐 LIMIT 保护，防止全表扫描撑爆内存
        if not re.search(r"\bLIMIT\s+\d+\b", cleaned, re.IGNORECASE):
            cleaned = f"{cleaned} LIMIT {self.default_limit}"
        return cleaned


def init_sales_sqlite_db(db_path: Union[str, Path] = ":memory:") -> sqlite3.Connection:
    """创建并初始化星辰数科真实 SQLite 销售数据库，初始化完成后开启只读模式。"""
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit_price REAL NOT NULL
        );
        CREATE TABLE sales_orders (
            order_id INTEGER PRIMARY KEY,
            region TEXT NOT NULL,
            quarter TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(product_id)
        );
        INSERT INTO products VALUES
            (1, '星辰智脑企业版', 'AI平台', 50000.0),
            (2, 'RAG知识库套件', 'AI应用', 20000.0),
            (3, '多Agent办公助手', 'AI应用', 30000.0);
        INSERT INTO sales_orders VALUES
            (101, '华东', '2025Q3', 1, 3, 150000.0, 'PAID'),
            (102, '华东', '2025Q3', 3, 4, 120000.0, 'PAID'),
            (103, '华东', '2025Q3', 2, 2, 40000.0, 'CANCELLED'),
            (104, '华南', '2025Q3', 1, 2, 100000.0, 'PAID'),
            (105, '华南', '2025Q3', 2, 5, 100000.0, 'PAID'),
            (106, '华北', '2025Q3', 3, 3, 90000.0, 'PAID');
        """
    )
    conn.commit()
    # 数据库引擎级物理只读锁（第二道防线）
    conn.execute("PRAGMA query_only = ON;")
    return conn


class TextToSQLAgent:
    """只读安全 Text-to-SQL 数据分析 Agent（含报错自修复重试与业务洞察生成）。"""

    def __init__(self, conn: sqlite3.Connection, default_limit: int = 100) -> None:
        self.conn = conn
        self.guard = SQLSafetyGuard(default_limit=default_limit)

    def get_schema_summary(self) -> str:
        rows = self.conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        return "\n".join(f"{name}: {ddl}" for name, ddl in rows)

    def _plan_sql(self, question: str, prev_error: str = "") -> str:
        """本地确定性 SQL 规划器（生产环境替换为对接大模型的 SQL 生成节点）。"""
        # 模拟常见注入攻击语句透传，交由 SQLSafetyGuard 统一拦截验证
        if any(k in question.upper() for k in ("DROP ", "DELETE ", "UPDATE ", ";", "--", "PRAGMA ")):
            return question

        # 演示自纠错：首次故意写错列名 total_amt，捕获 OperationalError 后二次修正为 amount
        if "各区域" in question and not prev_error and "模拟纠错" in question:
            return "SELECT region, SUM(total_amt) AS total_sales FROM sales_orders WHERE status = 'PAID' GROUP BY region"

        if "各区域" in question or "区域" in question:
            return (
                "SELECT region, SUM(amount) AS total_sales, COUNT(*) AS order_cnt "
                "FROM sales_orders WHERE status = 'PAID' "
                "GROUP BY region ORDER BY total_sales DESC"
            )
        if "最畅销" in question or "商品" in question or "产品" in question:
            return (
                "SELECT p.product_name, SUM(o.amount) AS total_sales, SUM(o.quantity) AS total_qty "
                "FROM sales_orders o JOIN products p ON o.product_id = p.product_id "
                "WHERE o.status = 'PAID' GROUP BY p.product_name ORDER BY total_sales DESC"
            )
        return "SELECT COUNT(*) AS paid_orders, SUM(amount) AS total_sales FROM sales_orders WHERE status = 'PAID'"

    def analyze(self, question: str, max_retries: int = 2) -> Dict[str, Any]:
        prev_error = ""
        retries = 0
        for attempt in range(max_retries + 1):
            candidate_sql = self._plan_sql(question, prev_error=prev_error)
            safe_sql = self.guard.sanitize_and_validate(candidate_sql)
            try:
                cur = self.conn.execute(safe_sql)
                columns = [desc[0] for desc in cur.description or []]
                rows = [dict(zip(columns, r)) for r in cur.fetchall()]
                return {
                    "question": question,
                    "sql": safe_sql,
                    "row_count": len(rows),
                    "rows": rows,
                    "retries": retries,
                    "insight": self._format_insight(question, rows),
                }
            except sqlite3.OperationalError as exc:
                prev_error = str(exc)
                retries += 1
                if attempt >= max_retries:
                    raise RuntimeError(f"SQL 执行连续失败: {prev_error}") from exc
        raise RuntimeError("未预期的执行分支")

    @staticmethod
    def _format_insight(question: str, rows: List[Dict[str, Any]]) -> str:
        if not rows:
            return f"针对「{question}」，未查询到符合条件的有效已支付订单记录。"
        top = rows[0]
        summary_pairs = ", ".join(f"{k}={v}" for k, v in top.items())
        return f"共检索到 {len(rows)} 条聚合结果，排首位的核心数据为：{summary_pairs}。"


if __name__ == "__main__":
    conn = init_sales_sqlite_db()
    agent = TextToSQLAgent(conn)
    res1 = agent.analyze("请统计各区域有效销售额排名（模拟纠错）")
    print("SQL:", res1["sql"])
    print("自纠错次数:", res1["retries"], "| 洞察:", res1["insight"])
    print("数据明细:", res1["rows"])
    conn.close()

