"""Day 44 - 步骤二：Agent 短期滑动窗口记忆 + SQLite 跨会话长期记忆引擎。"""

from __future__ import annotations

import sqlite3
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, List, Tuple, Union


@dataclass
class MemoryItem:
    memory_id: int
    user_id: str
    category: str  # "preference" | "fact" | "episodic"
    content: str
    importance: int  # 1 ~ 5
    updated_at: float


class ShortTermMemory:
    """短期工作记忆：滑动窗口保留最近 max_turns 轮对话，超限时自动滚动压缩旧摘要。"""

    def __init__(self, max_messages: int = 6) -> None:
        self.max_messages = max_messages
        self._messages: Deque[Dict[str, str]] = deque()
        self.evicted_summary: List[str] = []

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        while len(self._messages) > self.max_messages:
            old = self._messages.popleft()
            self.evicted_summary.append(f"{old['role']}: {old['content'][:24]}")

    def get_messages(self) -> List[Dict[str, str]]:
        return list(self._messages)


class SQLiteLongTermMemory:
    """基于 SQLite 的跨会话长期记忆库：支持写入、去重更新与相关性+重要性混合召回。"""

    def __init__(self, db_path: Union[str, Path] = ":memory:") -> None:
        self._conn = sqlite3.connect(str(db_path))
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS long_term_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                importance INTEGER NOT NULL,
                updated_at REAL NOT NULL,
                UNIQUE(user_id, category, content)
            )
            """
        )
        self._conn.commit()

    def remember(self, user_id: str, category: str, content: str, importance: int = 3) -> None:
        imp = max(1, min(5, int(importance)))
        now = time.time()
        self._conn.execute(
            """
            INSERT INTO long_term_memories (user_id, category, content, importance, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, category, content)
            DO UPDATE SET importance = excluded.importance, updated_at = excluded.updated_at
            """,
            (user_id, category, content, imp, now),
        )
        self._conn.commit()

    def recall(self, user_id: str, query: str, top_k: int = 3) -> List[MemoryItem]:
        rows = self._conn.execute(
            "SELECT id, user_id, category, content, importance, updated_at FROM long_term_memories WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        query_chars = {ch for ch in query.lower() if ch.strip()}
        scored: List[Tuple[float, MemoryItem]] = []
        for row in rows:
            item = MemoryItem(*row)
            content_chars = {ch for ch in item.content.lower() if ch.strip()}
            overlap = len(query_chars & content_chars) / max(len(query_chars), 1)
            # 综合打分：字符相关性 + 重要性加权
            score = overlap * 2.0 + item.importance * 0.4
            scored.append((score, item))
        scored.sort(key=lambda pair: (pair[0], pair[1].updated_at), reverse=True)
        return [item for _, item in scored[:top_k]]

    def close(self) -> None:
        self._conn.close()


class HybridMemoryManager:
    """双层记忆统一门面：拼装给大模型推理的完整记忆上下文。"""

    def __init__(self, user_id: str, long_term: SQLiteLongTermMemory, max_short_messages: int = 6) -> None:
        self.user_id = user_id
        self.short_term = ShortTermMemory(max_messages=max_short_messages)
        self.long_term = long_term

    def build_prompt_context(self, current_query: str, top_k: int = 2) -> Dict[str, object]:
        recalled = self.long_term.recall(self.user_id, current_query, top_k=top_k)
        return {
            "user_id": self.user_id,
            "long_term_memories": [f"[{m.category}/P{m.importance}] {m.content}" for m in recalled],
            "short_term_messages": self.short_term.get_messages(),
            "evicted_count": len(self.short_term.evicted_summary),
        }


if __name__ == "__main__":
    ltm = SQLiteLongTermMemory(":memory:")
    ltm.remember("u_chen", "preference", "汇报请始终使用三点式精简结论，不要长篇大论", importance=5)
    ltm.remember("u_chen", "fact", "负责杭州星辰数科 AI 平台架构团队", importance=4)
    ltm.remember("u_chen", "episodic", "上周五讨论过 MCP Server 安全接入规范", importance=3)

    mgr = HybridMemoryManager("u_chen", ltm, max_short_messages=2)
    mgr.short_term.add("user", "你好")
    mgr.short_term.add("assistant", "你好老陈，今天需要什么协助？")
    mgr.short_term.add("user", "帮我总结一下 MCP 接入汇报要点")

    ctx = mgr.build_prompt_context("MCP 汇报要点", top_k=2)
    print("组装后的双层记忆上下文:", ctx)
    ltm.close()

