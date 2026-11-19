"""
Day 49 课后作业 1（基础巩固）：为 FastAPI 增加列出全部待审批任务的 GET 接口
工单：STARMIND-049
"""

"""Day 49 作业 1 参考答案：待审批 HITL 任务列表查询。"""

import json
import sqlite3
from typing import Any, Dict, List


def list_pending_tasks(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    rows = conn.execute(
        "SELECT thread_id, routed_agent, state_json FROM office_tasks WHERE status = 'WAITING_CONFIRMATION' ORDER BY updated_at DESC"
    ).fetchall()
    return [{"thread_id": r[0], "routed_agent": r[1], "state": json.loads(r[2])} for r in rows]


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE office_tasks (thread_id TEXT, status TEXT, routed_agent TEXT, state_json TEXT, updated_at REAL)")
    conn.execute("INSERT INTO office_tasks VALUES ('t1', 'WAITING_CONFIRMATION', 'approval_agent', '{\"amount\": 8000}', 200.0)")
    conn.execute("INSERT INTO office_tasks VALUES ('t2', 'COMPLETED', 'knowledge_agent', '{}', 300.0)")
    pending = list_pending_tasks(conn)
    print("待办审批:", pending)
    assert len(pending) == 1 and pending[0]["thread_id"] == "t1"

