"""
StarMind Day 24 - 步骤一：SQLAlchemy 2.x + SQLite 企业对话历史持久化层
支持文件 SQLite 与内存 SQLite，提供完整的会话与消息 CRUD 仓库接口。
"""

from datetime import datetime, timezone
from typing import Dict, List

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """SQLAlchemy 2.x 声明式模型基类。"""


class ChatSession(Base):
    """会话主表：记录企业员工创建的对话线程。"""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(120), default="新企业会话")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.id",
    )


class ChatMessage(Base):
    """消息明细表：持久化保存每一轮 user / assistant 文本。"""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    session: Mapped[ChatSession] = relationship(back_populates="messages")


class ChatRepository:
    """面向 FastAPI 的对话历史持久化仓库。"""

    def __init__(self, database_url: str = "sqlite:///:memory:") -> None:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        engine_kwargs = {"connect_args": connect_args}
        if database_url == "sqlite:///:memory:":
            engine_kwargs["poolclass"] = StaticPool

        self.engine = create_engine(database_url, **engine_kwargs)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def ensure_session(self, session_id: str, title: str | None = None) -> ChatSession:
        """若会话不存在则自动创建，存在则直接返回。"""
        with self.SessionLocal() as db:
            sess = db.get(ChatSession, session_id)
            if sess is None:
                sess = ChatSession(id=session_id, title=(title or "星辰智脑会话")[:120])
                db.add(sess)
                db.commit()
                db.refresh(sess)
            return sess

    def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """追加一条对话消息到指定会话并提交落盘。"""
        with self.SessionLocal() as db:
            if db.get(ChatSession, session_id) is None:
                db.add(ChatSession(id=session_id, title=content[:30] or "星辰智脑会话"))
            msg = ChatMessage(session_id=session_id, role=role, content=content)
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return msg

    def list_sessions(self) -> List[Dict[str, object]]:
        """列出全部历史会话摘要及消息条数。"""
        with self.SessionLocal() as db:
            sessions = db.scalars(select(ChatSession).order_by(ChatSession.created_at.desc())).all()
            return [
                {
                    "session_id": s.id,
                    "title": s.title,
                    "message_count": len(s.messages),
                }
                for s in sessions
            ]

    def get_messages(self, session_id: str) -> List[Dict[str, str]] | None:
        """查询指定会话的全部历史消息；若会话不存在返回 None。"""
        with self.SessionLocal() as db:
            sess = db.get(ChatSession, session_id)
            if sess is None:
                return None
            return [{"role": m.role, "content": m.content} for m in sess.messages]

    def delete_session(self, session_id: str) -> bool:
        """删除会话并级联清理其名下全部消息。"""
        with self.SessionLocal() as db:
            sess = db.get(ChatSession, session_id)
            if sess is None:
                return False
            db.delete(sess)
            db.commit()
            return True


if __name__ == "__main__":
    repo = ChatRepository("sqlite:///:memory:")
    repo.add_message("sess_01", "user", "你好，杭州出差住宿报销上限多少？")
    repo.add_message("sess_01", "assistant", "一线及新一线城市住宿上限 600 元/晚。")
    print("会话列表:", repo.list_sessions())
    print("消息历史:", repo.get_messages("sess_01"))

