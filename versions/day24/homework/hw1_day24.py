"""
Day 24 课后作业 1（基础巩固）：为 ChatRepository 增加会话标题重命名方法
工单：STARMIND-024
"""

from src.day24_database import ChatRepository, ChatSession


def rename_session(repo: ChatRepository, session_id: str, new_title: str) -> bool:
    """更新指定会话的展示标题并持久化到 SQLite。"""
    with repo.SessionLocal() as db:
        sess = db.get(ChatSession, session_id)
        if sess is None:
            return False
        sess.title = new_title.strip()[:120]
        db.commit()
        return True


if __name__ == "__main__":
    repo = ChatRepository("sqlite:///:memory:")
    repo.add_message("s_rename", "user", "初始提问")
    print("重命名结果:", rename_session(repo, "s_rename", "2026 差旅报销咨询"))
    print("最新列表:", repo.list_sessions())

