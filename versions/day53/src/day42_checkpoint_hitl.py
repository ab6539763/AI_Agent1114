"""Day 42 - 步骤一：SQLite Checkpointer 状态持久化、HITL 中断恢复与节点重试机制。"""

from __future__ import annotations

import copy
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

START = "__start__"
END = "__end__"


@dataclass
class RetryPolicy:
    """节点级错误重试策略（对齐 LangGraph RetryPolicy）。"""

    max_attempts: int = 3
    initial_delay_sec: float = 0.01
    backoff_factor: float = 2.0
    retry_on: Tuple[Type[Exception], ...] = (ConnectionError, TimeoutError, RuntimeError)


class SQLiteCheckpointer:
    """基于 SQLite 的状态快照持久化存储，支持断点续跑与历史回溯。"""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_table()

    def _init_table(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                step_no INTEGER NOT NULL,
                next_node TEXT NOT NULL,
                status TEXT NOT NULL,
                state_json TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    def save(self, thread_id: str, step_no: int, next_node: str, status: str, state: Dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO checkpoints (thread_id, step_no, next_node, status, state_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (thread_id, step_no, next_node, status, json.dumps(state, ensure_ascii=False), time.time()),
        )
        self._conn.commit()

    def load_latest(self, thread_id: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT step_no, next_node, status, state_json FROM checkpoints "
            "WHERE thread_id = ? ORDER BY id DESC LIMIT 1",
            (thread_id,),
        ).fetchone()
        if not row:
            return None
        return {
            "step_no": row[0],
            "next_node": row[1],
            "status": row[2],
            "state": json.loads(row[3]),
        }

    def get_history(self, thread_id: str) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT step_no, next_node, status, state_json FROM checkpoints "
            "WHERE thread_id = ? ORDER BY id ASC",
            (thread_id,),
        ).fetchall()
        return [
            {"step_no": r[0], "next_node": r[1], "status": r[2], "state": json.loads(r[3])}
            for r in rows
        ]

    def close(self) -> None:
        self._conn.close()


class PersistentGraph:
    """支持 Checkpointer、HITL 中断恢复与节点重试的进阶状态图引擎。"""

    def __init__(
        self,
        checkpointer: SQLiteCheckpointer,
        interrupt_before: Optional[List[str]] = None,
    ) -> None:
        self.checkpointer = checkpointer
        self.interrupt_before = set(interrupt_before or [])
        self._nodes: Dict[str, Tuple[Callable[[Dict[str, Any]], Dict[str, Any]], Optional[RetryPolicy]]] = {}
        self._edges: Dict[str, str] = {}

    def add_node(
        self,
        name: str,
        func: Callable[[Dict[str, Any]], Dict[str, Any]],
        retry_policy: Optional[RetryPolicy] = None,
    ) -> "PersistentGraph":
        self._nodes[name] = (func, retry_policy)
        return self

    def add_edge(self, src: str, dst: str) -> "PersistentGraph":
        self._edges[src] = dst
        return self

    def _run_node_with_retry(self, name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        func, policy = self._nodes[name]
        if policy is None:
            return func(copy.deepcopy(state))

        delay = policy.initial_delay_sec
        last_exc: Optional[Exception] = None
        for attempt in range(1, policy.max_attempts + 1):
            try:
                return func(copy.deepcopy(state))
            except policy.retry_on as exc:
                last_exc = exc
                if attempt < policy.max_attempts:
                    time.sleep(delay)
                    delay *= policy.backoff_factor
        assert last_exc is not None
        raise last_exc

    def run(self, thread_id: str, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """启动新线程任务，若命中 interrupt_before 则落库挂起并返回 INTERRUPTED。"""
        state = copy.deepcopy(initial_state)
        next_node = self._edges[START]
        return self._drive(thread_id=thread_id, state=state, current=next_node, step_no=0, resuming=False)

    def resume(self, thread_id: str, human_patch: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """从 SQLite 加载最新断点，合并人工输入补丁，继续执行后续节点。"""
        ckpt = self.checkpointer.load_latest(thread_id)
        if not ckpt:
            raise ValueError(f"未找到 thread_id='{thread_id}' 的持久化快照")
        if ckpt["status"] != "INTERRUPTED":
            raise ValueError(f"当前状态为 {ckpt['status']}，无需恢复")

        state = ckpt["state"]
        if human_patch:
            state.update(human_patch)
        return self._drive(
            thread_id=thread_id,
            state=state,
            current=ckpt["next_node"],
            step_no=ckpt["step_no"],
            resuming=True,
        )

    def _drive(
        self,
        thread_id: str,
        state: Dict[str, Any],
        current: str,
        step_no: int,
        resuming: bool,
    ) -> Dict[str, Any]:
        first_node = True
        while current != END:
            # 命中人工中断点（恢复执行时的首个节点放行）
            if current in self.interrupt_before and not (resuming and first_node):
                self.checkpointer.save(thread_id, step_no, current, "INTERRUPTED", state)
                return {"status": "INTERRUPTED", "waiting_node": current, "state": state}

            first_node = False
            update = self._run_node_with_retry(current, state)
            state.update(update)
            step_no += 1
            current = self._edges[current]
            self.checkpointer.save(thread_id, step_no, current, "RUNNING" if current != END else "COMPLETED", state)

        return {"status": "COMPLETED", "waiting_node": None, "state": state}


if __name__ == "__main__":
    ckpt = SQLiteCheckpointer(":memory:")
    g = PersistentGraph(checkpointer=ckpt, interrupt_before=["publish"])
    g.add_node("draft", lambda s: {"outline": [f"1.{s['topic']}背景", f"2.{s['topic']}架构"]})
    g.add_node("publish", lambda s: {"published": True, "reviewer": s.get("reviewer", "未知")})
    g.add_edge(START, "draft")
    g.add_edge("draft", "publish")
    g.add_edge("publish", END)

    r1 = g.run("doc-001", {"topic": "星辰智脑中台"})
    print("第一次执行状态:", r1["status"], "| 等待节点:", r1["waiting_node"])
    r2 = g.resume("doc-001", human_patch={"reviewer": "林产品", "approved": True})
    print("人工放行后状态:", r2["status"], "| 最终状态:", r2["state"])

