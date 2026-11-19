import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 27 自动化单元测试：验证 SQLite 持久化、多会话隔离、窗口裁剪与摘要压缩。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import HumanMessage, AIMessage, SystemMessage
from src.day27_sqlite_history import SQLiteChatMessageHistory
from src.day27_memory_chain import (
    ContextualChatChain,
    RunnableWithMessageHistory,
    SummaryBufferMemoryStrategy,
    WindowMemoryStrategy,
)


def test_sqlite_persistence_and_isolation(tmp_path):
    db_path = str(tmp_path / "test_mem.db")
    h1 = SQLiteChatMessageHistory("sess_a", db_path=db_path)
    h2 = SQLiteChatMessageHistory("sess_b", db_path=db_path)
    h1.add_user_message("A的消息")
    h2.add_user_message("B的消息")

    # 模拟服务重启：重新实例化读取
    h1_reloaded = SQLiteChatMessageHistory("sess_a", db_path=db_path)
    assert len(h1_reloaded.messages) == 1
    assert h1_reloaded.messages[0].content == "A的消息"

    h1_reloaded.clear()
    assert len(h1_reloaded.messages) == 0
    assert len(SQLiteChatMessageHistory("sess_b", db_path=db_path).messages) == 1


def test_window_and_summary_strategies():
    msgs = []
    for i in range(5):
        msgs.append(HumanMessage(content=f"第{i}轮用户提问：非常详细的业务背景描述内容"))
        msgs.append(AIMessage(content=f"第{i}轮AI回复：好的收到"))

    win = WindowMemoryStrategy(k=2)
    trimmed = win.compress(msgs)
    assert len(trimmed) == 4
    assert "第3轮" in trimmed[0].content

    summary = SummaryBufferMemoryStrategy(max_chars=80, keep_recent_turns=1)
    compressed = summary.compress(msgs)
    assert isinstance(compressed[0], SystemMessage)
    assert "早期对话摘要" in compressed[0].content
    assert len(compressed) == 3  # 1条摘要 + 最近1轮(2条)


def test_runnable_with_message_history_end_to_end(tmp_path):
    db_path = str(tmp_path / "e2e.db")
    chain = RunnableWithMessageHistory(
        runnable=ContextualChatChain("你是星辰助手"),
        get_session_history=lambda sid: SQLiteChatMessageHistory(sid, db_path=db_path),
        memory_strategy=SummaryBufferMemoryStrategy(max_chars=100, keep_recent_turns=1),
    )

    cfg_u1 = {"configurable": {"session_id": "u1"}}
    cfg_u2 = {"configurable": {"session_id": "u2"}}

    chain.invoke({"input": "你好，我叫林悦，在产品部"}, config=cfg_u1)
    chain.invoke({"input": "请帮我查一下下周会议室预定规则和投影仪报修流程"}, config=cfg_u1)
    r1 = chain.invoke({"input": "我叫什么？"}, config=cfg_u1)
    r2 = chain.invoke({"input": "我叫什么？"}, config=cfg_u2)

    assert "林悦" in r1.content and "产品部" in r1.content
    assert "还没有您的姓名" in r2.content

    with pytest.raises(ValueError, match="session_id"):
        chain.invoke({"input": "没有传session_id"})

