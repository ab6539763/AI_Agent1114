"""
Day 59 课后作业 1（基础巩固）：基础巩固：为 Repository 增加按租户统计总 Token 消耗的查询方法
工单：STARMIND-059
"""

from src.day59_db_repository import StarMindRepository


def sum_session_tokens(repo: StarMindRepository, session_id: str) -> int:
    return sum(int(m["tokens"]) for m in repo.get_history(session_id, limit=1000))


r = StarMindRepository()
r.create_session("s1", "t1", "demo")
r.append_message("s1", "user", "hi", 10)
r.append_message("s1", "assistant", "hello", 25)
assert sum_session_tokens(r, "s1") == 35
print("会话总 Token 统计通过: 35")

