import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-008 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day08_chat_message import ChatMessage
from day08_chat_session import ChatSession


def test_chat_message_validation_and_factory():
    msg = ChatMessage("USER", "  测试消息  ")
    assert msg.role == "user"
    assert msg.content == "测试消息"
    assert msg.to_api_dict() == {"role": "user", "content": "测试消息"}

    rebuilt = ChatMessage.from_dict(msg.to_storage_dict())
    assert rebuilt.role == "user"
    assert rebuilt.content == "测试消息"

    with pytest.raises(ValueError):
        ChatMessage("boss", "非法角色")
    with pytest.raises(ValueError):
        ChatMessage("user", "   ")


def test_chat_session_window_and_isolation():
    s1 = ChatSession("s1", system_prompt="人设A", max_history=2)
    s2 = ChatSession("s2", system_prompt="人设B", max_history=2)

    s1.add_message("user", "q1")
    s1.add_message("assistant", "a1")
    s1.add_message("user", "q2")

    # s1 窗口裁剪后应保留 system + a1 + q2
    api_msgs = s1.to_api_messages()
    assert [m["content"] for m in api_msgs] == ["人设A", "a1", "q2"]
    # s2 应完全隔离不受 s1 影响
    assert [m["content"] for m in s2.to_api_messages()] == ["人设B"]

    s1.clear()
    assert [m["content"] for m in s1.to_api_messages()] == ["人设A"]

