"""
Day 59 - 模块二：SQLAlchemy 2.0 持久化模型与 Repository 仓储底座
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(200), default="新会话")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    tokens: Mapped[int] = mapped_column(Integer, default=0)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    tenant_id: Mapped[str] = mapped_column(String(64))
    action: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))


class StarMindRepository:
    """统一数据访问仓储层（支持 SQLite / PostgreSQL 无缝切换）"""

    def __init__(self, database_url: str = "sqlite:///:memory:") -> None:
        self.engine = create_engine(database_url, future=True)
        Base.metadata.create_all(self.engine)

    def create_session(self, session_id: str, tenant_id: str, title: str) -> None:
        with Session(self.engine) as db:
            db.add(ChatSession(id=session_id, tenant_id=tenant_id, title=title))
            db.commit()

    def append_message(self, session_id: str, role: str, content: str, tokens: int = 0) -> int:
        with Session(self.engine) as db:
            msg = ChatMessage(session_id=session_id, role=role, content=content, tokens=tokens)
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return msg.id

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, object]]:
        with Session(self.engine) as db:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.id.asc())
                .limit(limit)
            )
            rows = db.scalars(stmt).all()
            return [{"role": r.role, "content": r.content, "tokens": r.tokens} for r in rows]

    def write_audit(self, trace_id: str, tenant_id: str, action: str, status: str) -> None:
        with Session(self.engine) as db:
            db.add(AuditLog(trace_id=trace_id, tenant_id=tenant_id, action=action, status=status))
            db.commit()

    def count_audits(self, tenant_id: str) -> int:
        with Session(self.engine) as db:
            rows = db.scalars(select(AuditLog).where(AuditLog.tenant_id == tenant_id)).all()
            return len(rows)


if __name__ == "__main__":
    repo = StarMindRepository()
    repo.create_session("sess-001", "dept_rd", "RAG 检索排查")
    repo.append_message("sess-001", "user", "如何优化检索召回率？", tokens=18)
    repo.append_message("sess-001", "assistant", "建议开启 BM25 + 向量混合检索并叠加 Rerank。", tokens=32)
    repo.write_audit("tr-demo01", "dept_rd", "chat_rag", "ALLOW")
    print("历史消息:", repo.get_history("sess-001"))
    print("审计条数:", repo.count_audits("dept_rd"))

