"""
STARMIND-014 模块二：星辰智脑命令行多轮对话 AI 助手 v1.0。
支持多轮上下文记忆、/help /history /stats /clear /save /exit 斜杠指令、
JSON 持久化存档与模型异常自动回滚。
"""

import re
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from day14_session_memory import ConversationMemory


class BaseChatBackend(ABC):
    """大模型对话后端抽象基类，便于无缝切换本地 Mock 或 DeepSeek/通义千问 HTTP 客户端。"""

    @abstractmethod
    def complete(self, messages: List[Dict[str, str]]) -> str:
        """接收标准 OpenAI 格式 messages 列表并返回助手回复正文。"""


class LocalSmartMockBackend(BaseChatBackend):
    """具备基础多轮上下文记忆能力的离线模拟后端（零外网依赖）。"""

    NAME_PATTERN = re.compile(r"(?:我叫|我是)([\u4e00-\u9fa5a-zA-Z0-9_]{1,12})")

    def complete(self, messages: List[Dict[str, str]]) -> str:
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        if not user_msgs:
            return "你好！我是星辰智脑，请问有什么可以帮您？"

        latest = user_msgs[-1]
        if "__TRIGGER_ERROR__" in latest:
            raise RuntimeError("模拟上游大模型网关 503 临时故障")

        # 扫描全部历史 user 消息，提取用户此前介绍过的名字（演示多轮记忆）
        remembered_name: Optional[str] = None
        for text in user_msgs:
            match = self.NAME_PATTERN.search(text)
            if match:
                candidate = match.group(1)
                if not any(q in candidate for q in ("什么", "谁", "吗", "呢")):
                    remembered_name = candidate

        if "我是谁" in latest or "我叫什么" in latest or "记得我" in latest:
            if remembered_name:
                return f"当然记得！你之前告诉我，你叫「{remembered_name}」。当前已累计记忆 {len(user_msgs)} 轮提问。"
            return "你还没有告诉我你的名字呢，可以说「我叫XXX」让我记住你！"

        if "报销" in latest:
            prefix = f"{remembered_name}同学，" if remembered_name else ""
            return f"{prefix}星辰数科报销请在钉钉提交费用单，500元以上需主管与财务双审批。"

        prefix = f"收到，{remembered_name}！" if remembered_name else "收到！"
        return f"{prefix}你刚才说：「{latest}」（当前上下文共携带 {len(messages)} 条消息）。"


class StarMindCLIAssistant:
    """星辰智脑命令行多轮对话助手主控类。"""

    HELP_TEXT = (
        "可用指令列表：\n"
        "  /help              查看帮助信息\n"
        "  /history           查看当前对话历史\n"
        "  /stats             查看对话轮数与 Token 估算\n"
        "  /clear             清空当前多轮记忆（保留系统人设）\n"
        "  /save [文件名]     保存对话记录为 JSON 文件（默认 session_history.json）\n"
        "  /exit              退出助手"
    )

    def __init__(
        self,
        backend: Optional[BaseChatBackend] = None,
        memory: Optional[ConversationMemory] = None,
        save_dir: Optional[Path] = None,
    ) -> None:
        self.backend = backend or LocalSmartMockBackend()
        self.memory = memory or ConversationMemory()
        self.save_dir = save_dir or Path("sessions")

    def _handle_command(self, line: str) -> Tuple[bool, str]:
        """解析并执行以 / 开头的斜杠管理指令。"""
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in {"/exit", "/quit"}:
            return False, "再见！感谢使用星辰智脑命令行 AI 助手。"

        if cmd == "/help":
            return True, self.HELP_TEXT

        if cmd == "/clear":
            self.memory.clear()
            return True, "已清空当前多轮对话记忆（系统人设已保留）。"

        if cmd == "/stats":
            st = self.memory.get_stats()
            return True, (
                f"会话ID: {st['session_id']} | 对话轮数: {st['turns']} | "
                f"消息条数: {st['message_count']} | 估算Tokens: {st['estimated_tokens']}"
            )

        if cmd == "/history":
            if not self.memory.messages:
                return True, "当前暂无对话历史。"
            lines = [f"[{i}] {m.role}: {m.content}" for i, m in enumerate(self.memory.messages, 1)]
            return True, "\n".join(lines)

        if cmd == "/save":
            # 使用 Path(arg).name 防止路径穿越漏洞
            safe_name = Path(arg).name if arg else "session_history.json"
            if not safe_name.endswith(".json"):
                safe_name += ".json"
            target = self.save_dir / safe_name
            saved_path = self.memory.save_to_json(target)
            return True, f"对话历史已保存至：{saved_path.as_posix()}"

        return True, f"未知指令：{cmd}，输入 /help 查看所有支持的指令。"

    def handle_line(self, raw_line: str) -> Tuple[bool, str]:
        """
        处理单行用户输入，返回 (是否继续运行, 输出文本)。
        """
        text = raw_line.strip()
        if not text:
            return True, "提示：输入不能为空，请输入问题或 /help 查看指令。"

        if text.startswith("/"):
            return self._handle_command(text)

        self.memory.add_user_message(text)
        try:
            payload = self.memory.build_payload_messages()
            reply = self.backend.complete(payload)
        except Exception as exc:
            # 异常时回滚刚才塞进去的 user 消息，确保历史状态不被污染
            self.memory.rollback_last_user_message()
            return True, f"抱歉，模型调用出现异常（已自动回滚本轮输入）：{exc}"

        self.memory.add_assistant_message(reply)
        return True, f"星辰智脑 > {reply}"

    def run_repl(self, input_lines: Optional[List[str]] = None) -> List[str]:
        """
        运行多轮对话主循环。
        - 传入 input_lines 时非阻塞逐行回放（用于演示与自动化测试）；
        - 未传 input_lines 时进入终端交互式 input() 模式。
        """
        transcript: List[str] = []
        script_iter = iter(input_lines) if input_lines is not None else None

        while True:
            if script_iter is not None:
                try:
                    raw = next(script_iter)
                except StopIteration:
                    break
            else:
                try:
                    raw = input("你 > ")
                except (EOFError, KeyboardInterrupt):
                    transcript.append("检测到中断信号，已安全退出。")
                    break

            keep_going, out = self.handle_line(raw)
            transcript.append(out)
            if not keep_going:
                break

        return transcript


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        assistant = StarMindCLIAssistant(save_dir=Path(tmp))
        demo_script = [
            "你好，我叫林产品，在杭州研发中心工作。",
            "你还记得我叫什么吗？",
            "/stats",
            "/save milestone1_demo.json",
            "/clear",
            "你还记得我叫什么吗？",
            "/exit",
        ]
        for user_in, bot_out in zip(demo_script, assistant.run_repl(demo_script)):
            print(f"你 > {user_in}")
            print(bot_out)
            print("-" * 55)

