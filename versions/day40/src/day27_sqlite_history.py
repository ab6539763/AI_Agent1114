"""
Day 27 - 步骤一：基于 SQLite 的多会话隔离历史存储（SQLiteChatMessageHistory）
对应生产包：langchain_community.chat_message_histories.SQLChatMessageHistory
"""

from __future__ import annotations

import json
import sqlite3
import sys
import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import AIMessage, BaseMessage, HumanMessage, SystemMessage


class BaseChatMessageHistory(ABC):
    """对话历史存储抽象基类。"""

    @property
    @abstractmethod
    def messages(self) -> List[BaseMessage]:
        """返回当前会话按时间升序排列的所有消息。"""

    @abstractmethod
    def add_message(self, message: BaseMessage) -> None:
        """追加单条消息。"""

    def add_user_message(self, content: str) -> None:
        self.add_message(HumanMessage(content=content))

    def add_ai_message(self, content: str) -> None:
        self.add_message(AIMessage(content=content))

    @abstractmethod
    def clear(self) -> None:
        """清空当前会话的全部消息（不影响其他 session_id）。"""


class InMemoryChatMessageHistory(BaseChatMessageHistory):
    """内存态会话存储，适合临时脚本与轻量单测。"""

    def __init__(self) -> None:
        self._messages: List[BaseMessage] = []

    @property
    def messages(self) -> List[BaseMessage]:
        return list(self._messages)

    def add_message(self, message: BaseMessage) -> None:
        self._messages.append(message)

    def clear(self) -> None:
        self._messages.clear()


class SQLiteChatMessageHistory(BaseChatMessageHistory):
    """
    企业级 SQLite 持久化会话历史：
    - 通过 session_id 严格隔离多员工对话。
    - 内置复合索引 (session_id, id) 与线程锁，支持多线程并发读写。
    """

    _lock = threading.Lock()
    _ROLE_TO_CLS = {
        "system": SystemMessage,
        "user": HumanMessage,
        "assistant": AIMessage,
    }

    def __init__(self, session_id: str, db_path: str = "starmind_memory.db") -> None:
        if not session_id or not session_id.strip():
            raise ValueError("session_id 不能为空")
        self.session_id = session_id.strip()
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chat_session_id
                ON chat_messages (session_id, id)
                """
            )

    @property
    def messages(self) -> List[BaseMessage]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT role, content, metadata_json FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
                (self.session_id,),
            ).fetchall()
        result: List[BaseMessage] = []
        for row in rows:
            cls = self._ROLE_TO_CLS.get(row["role"], HumanMessage)
            meta = json.loads(row["metadata_json"])
            msg = cls(content=row["content"])
            msg.additional_kwargs = meta
            result.append(msg)
        return result

    def add_message(self, message: BaseMessage) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chat_messages (session_id, role, content, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    self.session_id,
                    message.role,
                    message.content,
                    json.dumps(message.additional_kwargs, ensure_ascii=False),
                    time.time(),
                ),
            )

    def clear(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (self.session_id,))

    @classmethod
    def list_sessions(cls, db_path: str) -> List[str]:
        """运维辅助：列出数据库中所有活跃的 session_id。"""
        with cls._lock, sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                "SELECT DISTINCT session_id FROM chat_messages ORDER BY session_id ASC"
            ).fetchall()
        return [r[0] for r in rows]


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        db = str(Path(tmpdir) / "demo_chat.db")
        h_zhang = SQLiteChatMessageHistory("emp_zhangsan", db_path=db)
        h_li = SQLiteChatMessageHistory("emp_lisi", db_path=db)

        h_zhang.add_user_message("我叫张三，在杭州星辰数科财务部")
        h_zhang.add_ai_message("你好张三，请问财务报销有什么可以帮您？")
        h_li.add_user_message("我叫李四，VPN连不上了")

        print("活跃会话:", SQLiteChatMessageHistory.list_sessions(db))
        print("张三历史条数:", len(h_zhang.messages), "| 内容:", [m.content for m in h_zhang.messages])
        print("李四历史条数:", len(h_li.messages), "| 内容:", [m.content for m in h_li.messages])

