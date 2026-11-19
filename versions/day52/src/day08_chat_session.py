"""
STARMIND-008 模块二：多轮会话记忆容器 ChatSession。
演示对象组合（ChatSession 持有多个 ChatMessage）、窗口裁剪与受保护状态管理。
"""

from typing import List, Dict, Optional
from day08_chat_message import ChatMessage


class ChatSession:
    """管理单个用户的多轮对话上下文与滑动窗口裁剪。"""

    def __init__(
        self,
        session_id: str,
        system_prompt: Optional[str] = None,
        max_history: int = 10,
    ) -> None:
        self.session_id: str = session_id
        self.max_history: int = max(1, int(max_history))
        # 系统指令单独保管，裁剪历史时绝不误删
        self._system_msg: Optional[ChatMessage] = (
            ChatMessage("system", system_prompt) if system_prompt else None
        )
        # 实例独享的消息历史列表（绝不能写成类属性！）
        self._messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str) -> ChatMessage:
        """向会话追加一条非 system 消息，并在超出窗口上限时自动裁剪最早消息。"""
        msg = ChatMessage(role, content)
        if msg.role == "system":
            self._system_msg = msg
            return msg

        self._messages.append(msg)
        # 滑动窗口裁剪：仅保留最近 max_history 条对话
        if len(self._messages) > self.max_history:
            self._messages = self._messages[-self.max_history :]
        return msg

    def total_tokens(self) -> int:
        """统计当前会话上下文（含系统指令）的估算总 Token 数。"""
        sys_tokens = self._system_msg.tokens if self._system_msg else 0
        return sys_tokens + sum(m.tokens for m in self._messages)

    def to_api_messages(self) -> List[Dict[str, str]]:
        """导出可直接传给大模型 API 的 messages 字典列表。"""
        payload: List[Dict[str, str]] = []
        if self._system_msg:
            payload.append(self._system_msg.to_api_dict())
        payload.extend(m.to_api_dict() for m in self._messages)
        return payload

    def clear(self) -> None:
        """清空历史对话，但保留 system_prompt 人设设定。"""
        self._messages.clear()


if __name__ == "__main__":
    session = ChatSession("sess-001", system_prompt="你是星辰智脑助手", max_history=2)
    session.add_message("user", "第一句提问")
    session.add_message("assistant", "第一句回复")
    session.add_message("user", "第二句提问")
    print("当前窗口消息数(不含system):", len(session.to_api_messages()) - 1)
    print("总 Token 估算:", session.total_tokens())
    print("导出 API Payload:", session.to_api_messages())

