"""
Day 42 课后作业 3（架构进阶）：为 HITL 中断增加超时自动过期清理策略
工单：STARMIND-042
"""

"""Day 42 作业 3 参考答案：HITL 挂起会话超时过期清理。"""

import sqlite3
import time


def expire_stale_threads(conn: sqlite3.Connection, ttl_seconds: float, now: float | None = None) -> int:
    ts = now if now is not None else time.time()
    cutoff = ts - ttl_seconds
    cur = conn.execute(
        "UPDATE checkpoints SET status = 'EXPIRED' WHERE status = 'INTERRUPTED' AND created_at < ?",
        (cutoff,),
    )
    conn.commit()
    return cur.rowcount


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE checkpoints (thread_id TEXT, status TEXT, created_at REAL)")
    conn.execute("INSERT INTO checkpoints VALUES ('old-1', 'INTERRUPTED', 100.0)")
    conn.execute("INSERT INTO checkpoints VALUES ('new-1', 'INTERRUPTED', 990.0)")
    expired = expire_stale_threads(conn, ttl_seconds=50.0, now=1000.0)
    print("过期清理数量:", expired)
    assert expired == 1

