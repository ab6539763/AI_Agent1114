"""
Day 27 课后作业 3（架构进阶）：作业三：实现带用户越权防护的 SafeSessionFactory
工单：STARMIND-027
"""

"""Day 27 作业三参考答案：防水平越权（IDOR）的安全会话工厂"""
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day27_sqlite_history import SQLiteChatMessageHistory


class SafeSessionFactory:
    VALID_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def get_history(self, user_id: str, conv_id: str) -> SQLiteChatMessageHistory:
        if not self.VALID_ID_RE.match(user_id) or not self.VALID_ID_RE.match(conv_id):
            raise ValueError("非法的 user_id 或 conv_id，存在注入或越权风险")
        scoped_session_id = f"{user_id}::{conv_id}"
        return SQLiteChatMessageHistory(session_id=scoped_session_id, db_path=self.db_path)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        factory = SafeSessionFactory(str(Path(tmpdir) / "safe.db"))
        h_a = factory.get_history("user_1001", "conv_1")
        h_b = factory.get_history("user_1002", "conv_1")
        h_a.add_user_message("仅1001可见的机密对话")
        assert len(h_b.messages) == 0
        print("越权隔离校验通过，user_1002 无法访问 conv_1 的 1001 数据。")

