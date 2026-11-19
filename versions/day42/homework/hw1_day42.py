"""
Day 42 课后作业 1（基础巩固）：为 Checkpointer 实现时间旅行回滚方法
工单：STARMIND-042
"""

"""Day 42 作业 1 参考答案：Checkpointer 时间旅行按步回溯。"""

import json
import sqlite3


def load_step(conn: sqlite3.Connection, thread_id: str, step_no: int) -> dict | None:
    row = conn.execute(
        "SELECT next_node, status, state_json FROM checkpoints WHERE thread_id = ? AND step_no = ? LIMIT 1",
        (thread_id, step_no),
    ).fetchone()
    if not row:
        return None
    return {"next_node": row[0], "status": row[1], "state": json.loads(row[2])}


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE checkpoints (thread_id TEXT, step_no INT, next_node TEXT, status TEXT, state_json TEXT)")
    conn.execute("INSERT INTO checkpoints VALUES ('t1', 1, 'b', 'RUNNING', '{\"step\": 1}')")
    conn.execute("INSERT INTO checkpoints VALUES ('t1', 2, '__end__', 'COMPLETED', '{\"step\": 2}')")
    snap = load_step(conn, "t1", 1)
    print("回溯到第 1 步:", snap)
    assert snap["state"]["step"] == 1

