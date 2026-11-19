"""
Day 27 - 步骤二：窗口记忆、摘要缓冲记忆与 RunnableWithMessageHistory 包装器
对应生产包：langchain_core.runnables.history.RunnableWithMessageHistory
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import AIMessage, BaseMessage, HumanMessage, StarMindChatModel, SystemMessage
from src.day26_lcel_core import Runnable
from src.day27_sqlite_history import BaseChatMessageHistory, SQLiteChatMessageHistory


class WindowMemoryStrategy:
    """滑动窗口记忆策略：仅保留最近 k 轮对话（每轮 = 1条用户 + 1条AI）。"""

    def __init__(self, k: int = 3) -> None:
        if k < 1:
            raise ValueError("窗口轮数 k 必须 >= 1")
        self.k = k

    def compress(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        max_msgs = self.k * 2
        if len(messages) <= max_msgs:
            return list(messages)
        return list(messages[-max_msgs:])


class SummaryBufferMemoryStrategy:
    """
    摘要缓冲记忆策略（对应 ConversationSummaryBufferMemory）：
    - 当历史消息总字符数 <= max_chars 时原样保留；
    - 超限时将早期消息压缩为一条 SystemMessage 摘要，并保留最近 keep_recent_turns 轮原文。
    """

    def __init__(
        self,
        max_chars: int = 180,
        keep_recent_turns: int = 2,
        summarizer: Optional[Callable[[List[BaseMessage]], str]] = None,
    ) -> None:
        self.max_chars = max_chars
        self.keep_recent_turns = keep_recent_turns
        self._summarizer = summarizer or self._default_extractive_summarizer

    @staticmethod
    def _default_extractive_summarizer(older_msgs: List[BaseMessage]) -> str:
        """离线确定性摘要器（生产环境可替换为轻量 LLM 摘要链）。"""
        facts: List[str] = []
        for msg in older_msgs:
            if msg.role == "user":
                snippet = msg.content.strip().replace("\n", " ")[:40]
                facts.append(f"用户提及「{snippet}」")
        joined = "；".join(facts) if facts else "此前进行了常规寒暄"
        return f"【早期对话摘要】{joined}。"

    def compress(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        total_chars = sum(len(m.content) for m in messages)
        keep_count = self.keep_recent_turns * 2
        if total_chars <= self.max_chars or len(messages) <= keep_count:
            return list(messages)
        older = messages[:-keep_count]
        recent = messages[-keep_count:]
        summary_text = self._summarizer(older)
        return [SystemMessage(content=summary_text), *recent]


class RunnableWithMessageHistory(Runnable[Dict[str, Any], AIMessage]):
    """
    无侵入多轮记忆包装器：
    自动根据 session_id 读取历史 -> 执行记忆裁剪/摘要 -> 注入 history 运行底层链 -> 写回本轮对话。
    """

    def __init__(
        self,
        runnable: Runnable[Dict[str, Any], AIMessage],
        get_session_history: Callable[[str], BaseChatMessageHistory],
        memory_strategy: WindowMemoryStrategy | SummaryBufferMemoryStrategy | None = None,
        input_messages_key: str = "input",
        history_messages_key: str = "history",
    ) -> None:
        self.runnable = runnable
        self.get_session_history = get_session_history
        self.memory_strategy = memory_strategy or WindowMemoryStrategy(k=5)
        self.input_messages_key = input_messages_key
        self.history_messages_key = history_messages_key

    def invoke(self, input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> AIMessage:
        session_id = (config or {}).get("configurable", {}).get("session_id")
        if not session_id:
            raise ValueError("调用 RunnableWithMessageHistory 必须在 config.configurable 中提供 session_id")

        history_store = self.get_session_history(session_id)
        compressed_history = self.memory_strategy.compress(history_store.messages)

        user_input = str(input_data[self.input_messages_key])
        payload = {**input_data, self.history_messages_key: compressed_history}
        ai_msg = self.runnable.invoke(payload)

        # 对话完成后再持久化落盘（确保异常时不污染历史）
        history_store.add_user_message(user_input)
        history_store.add_ai_message(ai_msg.content)
        return ai_msg


def _memory_aware_chat_handler(messages: List[BaseMessage]) -> str:
    """模拟能读取多轮历史上下文（含摘要）的星辰智能助手。"""
    full_context = "\n".join(m.content for m in messages[:-1])
    question = messages[-1].content

    # 简单从历史上下文中提取员工姓名与部门，验证记忆是否生效
    name_match = re.search(r"我叫([\u4e00-\u9fffA-Za-z0-9]{2,8})", full_context)
    dept_match = re.search(r"在([\u4e00-\u9fffA-Za-z0-9]{2,10}部)", full_context)

    if "我是谁" in question or "我叫什么" in question:
        if name_match:
            dept_info = f"，来自{dept_match.group(1)}" if dept_match else ""
            return f"我记得您！您是{name_match.group(1)}{dept_info}。"
        return "抱歉，当前会话记忆里还没有您的姓名信息，方便告诉我怎么称呼您吗？"

    return f"已收到您的消息：「{question}」（当前参考历史消息 {len(messages) - 1} 条）。"


class ContextualChatChain(Runnable[Dict[str, Any], AIMessage]):
    """将 system + history + current_input 拼装后送入 ChatModel。"""

    def __init__(self, system_prompt: str) -> None:
        self.system_prompt = system_prompt
        self.model = StarMindChatModel(model_name="starmind-memory-llm", handler=_memory_aware_chat_handler)

    def invoke(self, input_data: Dict[str, Any]) -> AIMessage:
        msgs: List[BaseMessage] = [SystemMessage(content=self.system_prompt)]
        msgs.extend(input_data.get("history", []))
        msgs.append(HumanMessage(content=input_data["input"]))
        return self.model.invoke(msgs)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = str(Path(tmpdir) / "starmind_sessions.db")
        base_chain = ContextualChatChain("你是杭州星辰数科企业助手，请结合上下文准确回答。")
        chat_with_memory = RunnableWithMessageHistory(
            runnable=base_chain,
            get_session_history=lambda sid: SQLiteChatMessageHistory(sid, db_path=db_file),
            memory_strategy=SummaryBufferMemoryStrategy(max_chars=120, keep_recent_turns=1),
        )

        cfg_a = {"configurable": {"session_id": "emp_wang"}}
        cfg_b = {"configurable": {"session_id": "emp_chen"}}

        print("小王 第1轮:", chat_with_memory.invoke({"input": "你好，我叫王小明，在研发部做Python后端开发"}, config=cfg_a).content)
        print("小王 第2轮:", chat_with_memory.invoke({"input": "请问今年年假怎么折算，另外出差补贴标准是多少？"}, config=cfg_a).content)
        print("小王 第3轮:", chat_with_memory.invoke({"input": "考考你，我叫什么名字？"}, config=cfg_a).content)
        print("老陈 第1轮:", chat_with_memory.invoke({"input": "考考你，我叫什么名字？"}, config=cfg_b).content)

