"""
数据库持久层子包（SQLAlchemy + SQLite）。
"""

from starmind_platform.app.db.database import (
    AuditLogRecord,
    Base,
    ChatMessageRecord,
    ChatSessionRecord,
    DatabaseManager,
    EnterpriseSalesRecord,
    get_db_manager,
)

__all__ = [
    "Base",
    "ChatSessionRecord",
    "ChatMessageRecord",
    "AuditLogRecord",
    "EnterpriseSalesRecord",
    "DatabaseManager",
    "get_db_manager",
]
