"""
STARMIND-014 模块一：多轮对话记忆引擎与 JSON 持久化存储。
负责维护 system 人设、多轮 messages 历史、滑动窗口裁剪、异常回滚与 JSON 读写。
"""

import json
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ChatMessage:
    """单条对话消息记录。"""

    role: str  # "user" 或 "assistant"
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )


class ConversationMemory:
    """星辰智脑多轮对话上下文记忆管理器。"""

    def __init__(
        self,
        system_prompt: str = "你是杭州星辰数科企业 AI 助手「星辰智脑」，请提供专业简洁的中文解答。",
        max_history_messages: int = 10,
        session_id: str = "default-session",
    ) -> None:
        if max_history_messages < 2:
            raise ValueError("max_history_messages 至少为 2（一问一答）")
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages
        self.session_id = session_id
        self.messages: List[ChatMessage] = []

    def add_user_message(self, content: str) -> ChatMessage:
        """追加一条用户消息。"""
        cleaned = content.strip()
        if not cleaned:
            raise ValueError("用户消息不能为空")
        msg = ChatMessage(role="user", content=cleaned)
        self.messages.append(msg)
        return msg

    def add_assistant_message(self, content: str) -> ChatMessage:
        """追加一条助手回复消息。"""
        msg = ChatMessage(role="assistant", content=content.strip())
        self.messages.append(msg)
        return msg

    def rollback_last_user_message(self) -> bool:
        """当模型调用失败时回滚最后一条孤立的 user 消息，防止上下文损坏。"""
        if self.messages and self.messages[-1].role == "user":
            self.messages.pop()
            return True
        return False

    def build_payload_messages(self) -> List[Dict[str, str]]:
        """
        构造发送给大模型的标准 messages 数组：
        始终保留 system_prompt 在首位 + 最近 max_history_messages 条历史消息。
        """
        window = self.messages[-self.max_history_messages :]
        payload: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        for item in window:
            payload.append({"role": item.role, "content": item.content})
        return payload

    def clear(self) -> None:
        """清空多轮历史消息（保留 system_prompt 人设）。"""
        self.messages.clear()

    def get_stats(self) -> Dict[str, Any]:
        """统计当前会话轮数、消息总数及粗略 Token 估算。"""
        user_turns = sum(1 for m in self.messages if m.role == "user")
        total_chars = len(self.system_prompt) + sum(len(m.content) for m in self.messages)
        return {
            "session_id": self.session_id,
            "turns": user_turns,
            "message_count": len(self.messages),
            "estimated_tokens": max(1, int(total_chars * 1.2)),
            "window_limit": self.max_history_messages,
        }

    def save_to_json(self, file_path: Path) -> Path:
        """将当前多轮对话完整持久化为 UTF-8 JSON 文件。"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "session_id": self.session_id,
            "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "system_prompt": self.system_prompt,
            "max_history_messages": self.max_history_messages,
            "messages": [asdict(m) for m in self.messages],
        }
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return file_path

    @classmethod
    def load_from_json(cls, file_path: Path) -> "ConversationMemory":
        """从 JSON 存档文件恢复历史会话记忆。"""
        if not file_path.exists():
            raise FileNotFoundError(f"会话文件不存在: {file_path}")
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"会话 JSON 文件已损坏: {exc}") from exc

        if not isinstance(raw, dict) or not isinstance(raw.get("messages"), list):
            raise ValueError("会话 JSON 结构无效：缺少 messages 列表")

        mem = cls(
            system_prompt=str(raw.get("system_prompt", "")),
            max_history_messages=int(raw.get("max_history_messages", 10)),
            session_id=str(raw.get("session_id", "restored-session")),
        )
        for item in raw["messages"]:
            mem.messages.append(
                ChatMessage(
                    role=str(item["role"]),
                    content=str(item["content"]),
                    timestamp=str(item.get("timestamp", "")),
                )
            )
        return mem


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        mem = ConversationMemory(session_id="demo-014", max_history_messages=4)
        mem.add_user_message("我叫小王，负责杭州研发部。")
        mem.add_assistant_message("你好小王！很高兴为杭州研发部服务。")
        saved = mem.save_to_json(Path(tmp) / "chat_history.json")
        restored = ConversationMemory.load_from_json(saved)
        print("持久化恢复成功，统计信息:", restored.get_stats())
        print("Payload 消息数:", len(restored.build_payload_messages()))

