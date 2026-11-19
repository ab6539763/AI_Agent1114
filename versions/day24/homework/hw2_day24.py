"""
Day 24 课后作业 2（企业实战）：按关键词全文检索历史消息（SQLite LIKE 查询）
工单：STARMIND-024
"""

from typing import Dict, List
from sqlalchemy import select
from src.day24_database import ChatMessage, ChatRepository


def search_messages(repo: ChatRepository, keyword: str) -> List[Dict[str, str]]:
    """使用 SQLAlchemy 2.x 在全量聊天记录中按关键词模糊检索。"""
    with repo.SessionLocal() as db:
        stmt = select(ChatMessage).where(ChatMessage.content.contains(keyword)).order_by(ChatMessage.id.desc())
        rows = db.scalars(stmt).all()
        return [{"session_id": r.session_id, "role": r.role, "content": r.content} for r in rows]


if __name__ == "__main__":
    repo = ChatRepository("sqlite:///:memory:")
    repo.add_message("s1", "user", "请问 VPN 怎么开通？")
    repo.add_message("s2", "user", "杭州差旅住宿报销标准？")
    print("搜索 VPN:", search_messages(repo, "VPN"))

