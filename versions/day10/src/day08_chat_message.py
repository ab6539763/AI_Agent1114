"""
STARMIND-008 模块一：核心领域模型 ChatMessage。
演示类属性、__init__ 初始化与不变式校验、实例方法、@classmethod 与 @staticmethod。
"""

from datetime import datetime, timezone
from typing import Dict, Any, Tuple


class ChatMessage:
    """表示大模型多轮对话中的单条标准化消息。"""

    # 类属性：所有消息实例共享的合法角色白名单（不可变元组）
    VALID_ROLES: Tuple[str, ...] = ("system", "user", "assistant", "tool")

    def __init__(self, role: str, content: str, created_at: str | None = None) -> None:
        normalized_role = role.strip().lower()
        # 构造期不变式校验：杜绝非法角色进入系统
        if normalized_role not in self.VALID_ROLES:
            raise ValueError(f"非法角色 '{role}'，允许的角色: {self.VALID_ROLES}")

        cleaned_content = content.strip()
        if not cleaned_content:
            raise ValueError("消息正文 content 不能为空")

        # 实例属性：每条消息独立拥有
        self.role: str = normalized_role
        self.content: str = cleaned_content
        self.created_at: str = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.tokens: int = self.estimate_tokens(self.content)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """静态工具方法：粗略估算文本 Token 数量。"""
        if not text:
            return 0
        return max(1, (len(text) * 3 + 3) // 4)

    def to_api_dict(self) -> Dict[str, str]:
        """实例方法：转换为 OpenAI/DeepSeek 兼容的最小 API 消息字典。"""
        return {"role": self.role, "content": self.content}

    def to_storage_dict(self) -> Dict[str, Any]:
        """实例方法：转换为包含元数据的完整持久化字典。"""
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "tokens": self.tokens,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """类方法工厂：从字典反序列化构造 ChatMessage 实例。"""
        return cls(
            role=str(data.get("role", "")),
            content=str(data.get("content", "")),
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        preview = self.content if len(self.content) <= 20 else self.content[:17] + "..."
        return f"ChatMessage(role={self.role!r}, tokens={self.tokens}, content={preview!r})"


if __name__ == "__main__":
    m1 = ChatMessage("user", "你好，请介绍一下杭州星辰数科")
    m2 = ChatMessage.from_dict({"role": "assistant", "content": "您好！星辰数科专注于企业级大模型应用研发。"})
    print(m1)
    print("API 协议格式:", m1.to_api_dict())
    print("反序列化对象:", m2)

