"""
数据库持久层模块（SQLAlchemy 2.x + SQLite）。

数据表设计：
1. `chat_sessions`：多轮对话会话主表（记录 session_id、标题、创建时间、更新时间）。
2. `chat_messages`：多轮消息历史表（关联 session_id，记录 role、脱敏后 content、Token 消耗与成本）。
3. `audit_logs`：企业合规审计日志表（记录安全护栏拦截、审批动作、SQL 查询与高危工具调用）。
4. `enterprise_sales`：星辰数科企业销售业绩样例表（供 Text-to-SQL Agent 执行真实 SQL 分析）。
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from starmind_platform.app.config import Settings, get_settings
from starmind_platform.app.core.logging_utils import get_logger, get_trace_id

logger = get_logger("starmind.db")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明式 ORM 基类。"""


class ChatSessionRecord(Base):
    """对话会话表。"""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), default="新对话")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    messages: Mapped[List["ChatMessageRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessageRecord.id",
    )


class ChatMessageRecord(Base):
    """对话消息历史表。"""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(64), default="")
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_cny: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    session: Mapped[ChatSessionRecord] = relationship(back_populates="messages")


class AuditLogRecord(Base):
    """企业安全与操作审计日志表。"""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    actor: Mapped[str] = mapped_column(String(64), default="system")
    status: Mapped[str] = mapped_column(String(32), default="ok")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class EnterpriseSalesRecord(Base):
    """企业销售业绩示例表（供 Text-to-SQL 真实查询使用）。"""

    __tablename__ = "enterprise_sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(128))
    region: Mapped[str] = mapped_column(String(32), index=True)
    product_name: Mapped[str] = mapped_column(String(128), index=True)
    quarter: Mapped[str] = mapped_column(String(16), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    amount_cny: Mapped[float] = mapped_column(Float)
    sales_owner: Mapped[str] = mapped_column(String(64))


# 预置的企业销售测试数据（覆盖华东/华北/华南/西南四大区、4 个季度与核心 AI 产品线）
SEED_SALES_ROWS: List[Dict[str, Any]] = [
    {
        "order_no": "SM2026Q1001",
        "customer_name": "浙江云帆制造集团",
        "region": "华东",
        "product_name": "星辰智脑企业版",
        "quarter": "2026Q1",
        "quantity": 3,
        "amount_cny": 480000.0,
        "sales_owner": "陈明",
    },
    {
        "order_no": "SM2026Q1002",
        "customer_name": "上海恒瑞生物科技",
        "region": "华东",
        "product_name": "星辰RAG知识底座",
        "quarter": "2026Q1",
        "quantity": 2,
        "amount_cny": 260000.0,
        "sales_owner": "林晓",
    },
    {
        "order_no": "SM2026Q1003",
        "customer_name": "北京中科能源研究院",
        "region": "华北",
        "product_name": "星辰智脑企业版",
        "quarter": "2026Q1",
        "quantity": 4,
        "amount_cny": 620000.0,
        "sales_owner": "王磊",
    },
    {
        "order_no": "SM2026Q2001",
        "customer_name": "深圳鹏程金融科技",
        "region": "华南",
        "product_name": "星辰安全护栏网关",
        "quarter": "2026Q2",
        "quantity": 5,
        "amount_cny": 390000.0,
        "sales_owner": "赵敏",
    },
    {
        "order_no": "SM2026Q2002",
        "customer_name": "杭州西湖智造股份",
        "region": "华东",
        "product_name": "星辰多Agent编排引擎",
        "quarter": "2026Q2",
        "quantity": 2,
        "amount_cny": 340000.0,
        "sales_owner": "陈明",
    },
    {
        "order_no": "SM2026Q2003",
        "customer_name": "成都天府数字政务中心",
        "region": "西南",
        "product_name": "星辰RAG知识底座",
        "quarter": "2026Q2",
        "quantity": 3,
        "amount_cny": 410000.0,
        "sales_owner": "周浩",
    },
    {
        "order_no": "SM2026Q3001",
        "customer_name": "广州岭南供应链集团",
        "region": "华南",
        "product_name": "星辰智脑企业版",
        "quarter": "2026Q3",
        "quantity": 3,
        "amount_cny": 510000.0,
        "sales_owner": "赵敏",
    },
    {
        "order_no": "SM2026Q3002",
        "customer_name": "北京华信商业银行",
        "region": "华北",
        "product_name": "星辰安全护栏网关",
        "quarter": "2026Q3",
        "quantity": 6,
        "amount_cny": 540000.0,
        "sales_owner": "王磊",
    },
    {
        "order_no": "SM2026Q4001",
        "customer_name": "苏州工业园区智算中心",
        "region": "华东",
        "product_name": "星辰智脑企业版",
        "quarter": "2026Q4",
        "quantity": 5,
        "amount_cny": 820000.0,
        "sales_owner": "林晓",
    },
    {
        "order_no": "SM2026Q4002",
        "customer_name": "重庆两江智能网联汽车",
        "region": "西南",
        "product_name": "星辰多Agent编排引擎",
        "quarter": "2026Q4",
        "quantity": 3,
        "amount_cny": 465000.0,
        "sales_owner": "周浩",
    },
]


class DatabaseManager:
    """数据库生命周期与常用 CRUD 封装管理器。"""

    def __init__(self, database_url: Optional[str] = None) -> None:
        settings = get_settings()
        self.database_url = database_url or settings.database_url

        # 确保 SQLite 文件所在父目录存在
        if self.database_url.startswith("sqlite:///"):
            db_path = Path(self.database_url.replace("sqlite:///", "", 1))
            db_path.parent.mkdir(parents=True, exist_ok=True)

        connect_args = {"check_same_thread": False} if self.database_url.startswith("sqlite") else {}
        self.engine = create_engine(self.database_url, connect_args=connect_args, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def init_db(self) -> None:
        """创建所有 ORM 数据表，并在销售表为空时自动灌入企业样例数据。"""
        Base.metadata.create_all(bind=self.engine)
        self._seed_sales_data()

    def _seed_sales_data(self) -> None:
        with self.SessionLocal() as db:
            existing = db.scalar(select(EnterpriseSalesRecord.id).limit(1))
            if existing is not None:
                return
            for row in SEED_SALES_ROWS:
                db.add(EnterpriseSalesRecord(**row))
            db.commit()
            logger.info(f"已自动初始化企业销售业绩示例数据共 {len(SEED_SALES_ROWS)} 条。")

    def get_session(self) -> Session:
        return self.SessionLocal()

    def ensure_chat_session(self, session_id: str, title: str = "星辰智脑对话") -> ChatSessionRecord:
        with self.SessionLocal() as db:
            record = db.get(ChatSessionRecord, session_id)
            if record is None:
                record = ChatSessionRecord(id=session_id, title=title[:120])
                db.add(record)
                db.commit()
                db.refresh(record)
            return record

    def append_message(
        self,
        *,
        session_id: str,
        role: str,
        content: str,
        model: str = "",
        tokens: int = 0,
        cost_cny: float = 0.0,
    ) -> ChatMessageRecord:
        self.ensure_chat_session(session_id, title=content[:30] if role == "user" else "星辰智脑对话")
        with self.SessionLocal() as db:
            msg = ChatMessageRecord(
                session_id=session_id,
                role=role,
                content=content,
                model=model,
                tokens=tokens,
                cost_cny=cost_cny,
            )
            db.add(msg)
            session_obj = db.get(ChatSessionRecord, session_id)
            if session_obj is not None:
                session_obj.updated_at = _utcnow()
            db.commit()
            db.refresh(msg)
            return msg

    def get_session_messages(self, session_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        with self.SessionLocal() as db:
            stmt = (
                select(ChatMessageRecord)
                .where(ChatMessageRecord.session_id == session_id)
                .order_by(ChatMessageRecord.id.asc())
                .limit(limit)
            )
            rows = db.scalars(stmt).all()
            return [
                {
                    "id": r.id,
                    "role": r.role,
                    "content": r.content,
                    "model": r.model,
                    "tokens": r.tokens,
                    "cost_cny": r.cost_cny,
                    "created_at": r.created_at.isoformat() if r.created_at else "",
                }
                for r in rows
            ]

    def record_audit(
        self,
        *,
        action: str,
        status: str = "ok",
        detail: str = "",
        actor: str = "user",
        trace_id: Optional[str] = None,
    ) -> None:
        with self.SessionLocal() as db:
            log = AuditLogRecord(
                trace_id=trace_id or get_trace_id(),
                action=action,
                actor=actor,
                status=status,
                detail=detail[:2000],
            )
            db.add(log)
            db.commit()

    def execute_readonly_query(self, sql: str) -> Dict[str, Any]:
        """执行已通过安全校验的只读 SELECT SQL，返回列名与记录列表。"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {"columns": columns, "rows": rows, "row_count": len(rows)}


_GLOBAL_DB: Optional[DatabaseManager] = None


def get_db_manager(settings: Optional[Settings] = None) -> DatabaseManager:
    """获取平台全局单例数据库管理器，并确保表结构已就绪。"""
    global _GLOBAL_DB
    if _GLOBAL_DB is None:
        cfg = settings or get_settings()
        _GLOBAL_DB = DatabaseManager(cfg.database_url)
        _GLOBAL_DB.init_db()
    return _GLOBAL_DB
