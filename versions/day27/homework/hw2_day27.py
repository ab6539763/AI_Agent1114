"""
Day 27 课后作业 2（企业实战）：作业二：给 SQLiteChatMessageHistory 增加会话 TTL 自动过期清理
工单：STARMIND-027
"""

"""Day 27 作业二参考答案：SQLite 会话历史 TTL 过期清理"""
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day27_sqlite_history import SQLiteChatMessageHistory


def purge_expired_messages(db_path: str, ttl_seconds: float, now: float | None = None) -> int:
    cutoff = (now or time.time()) - ttl_seconds
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute("DELETE FROM chat_messages WHERE created_at < ?", (cutoff,))
        return cur.rowcount


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        db = str(Path(tmpdir) / "ttl.db")
        h = SQLiteChatMessageHistory("emp_01", db_path=db)
        h.add_user_message("一条旧消息")
        # 模拟 2 天后清理 TTL=86400 的过期消息
        deleted = purge_expired_messages(db, ttl_seconds=86400, now=time.time() + 172800)
        print("清理过期消息条数:", deleted)
        assert deleted == 1
        assert len(h.messages) == 0

