"""
StarMind Day 21 - 步骤一：多轮对话 + 安全过滤 + 工具调用 + 流式输出整合引擎
支持按 session_id 隔离会话、滑窗记忆裁剪、AST 安全计算与标准化流式事件输出。
"""

import ast
import operator
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List


_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_INJECTION_RE = re.compile(
    r"(忽略|无视|忘记).{0,8}(以上|前面|所有).{0,6}(指令|规则)|ignore\s+all\s+previous\s+instructions|输出.{0,6}系统提示词",
    re.I,
)
_MATH_RE = re.compile(r"[\d\.\(\)\+\-\*/\s]{3,}")


def _safe_calc(expr: str) -> float:
    """AST 白名单四则运算求值。"""
    tree = ast.parse(expr, mode="eval")

    def _ev(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left, right = _ev(node.left), _ev(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("除数不能为 0")
            return _BIN_OPS[type(node.op)](left, right)
        raise ValueError("不支持的算术表达")

    return round(_ev(tree), 4)


@dataclass
class StreamEvent:
    """标准化引擎流式事件：event_type in {'security_blocked', 'tool_call', 'tool_result', 'delta', 'done'}"""
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)


class StarMindIntegratedEngine:
    """星辰智脑第 3 周综合对话引擎（多轮记忆 + 安全防线 + 工具闭环 + 流式吐字）。"""

    WEATHER_DB = {
        "杭州": "多云 19°C，微风适宜出行",
        "北京": "晴 12°C，空气清新",
        "上海": "阴 20°C，湿度略高",
    }
    KB_DB = {
        "差旅": "一线及新一线城市住宿报销上限 600 元/晚，需附电子专票。",
        "vpn": "新员工在 OA 提交『IT权限申请』，主管审批后 30 分钟内开通 WireGuard VPN。",
    }

    def __init__(
        self,
        system_prompt: str = "你是杭州星辰数科企业 AI 助手星辰智脑，专业、严谨、乐于助人。",
        max_history_turns: int = 4,
    ) -> None:
        self.system_prompt = system_prompt
        self.max_history_turns = max_history_turns
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取指定会话的完整消息列表（首条固定为 system）。"""
        if session_id not in self._sessions:
            self._sessions[session_id] = [{"role": "system", "content": self.system_prompt}]
        return self._sessions[session_id]

    def _trim_history(self, session_id: str) -> None:
        """滑动窗口裁剪：始终保留 system，其余仅保留最近 max_history_turns 轮（每轮2条消息）。"""
        hist = self.get_history(session_id)
        max_non_system = self.max_history_turns * 2
        if len(hist) - 1 > max_non_system:
            self._sessions[session_id] = [hist[0]] + hist[-max_non_system:]

    def _extract_remembered_name(self, session_id: str) -> str | None:
        """从多轮对话历史中回忆用户曾告知的姓名（排除「我叫什么/谁」等疑问句）。"""
        for msg in reversed(self.get_history(session_id)):
            if msg["role"] == "user":
                m = re.search(r"我叫([\u4e00-\u9fffA-Za-z0-9]{1,8})", msg["content"])
                if m and not any(q in m.group(1) for q in ("什么", "啥", "谁", "哪")):
                    return m.group(1)
        return None

    def stream_turn(
        self,
        session_id: str,
        user_query: str,
        chunk_size: int = 8,
    ) -> Generator[StreamEvent, None, None]:
        """执行单轮完整对话：安全检查 -> 工具调用 -> 多轮记忆整合 -> 流式分片输出。"""
        # 1. 安全防注入检查
        if _INJECTION_RE.search(user_query):
            refusal = "【安全拦截】检测到疑似提示词注入或越权指令，星辰智脑已拒绝执行该请求。"
            yield StreamEvent("security_blocked", {"reason": "prompt_injection_detected"})
            yield StreamEvent("delta", {"text": refusal})
            yield StreamEvent("done", {"session_id": session_id, "blocked": True, "tools_used": []})
            return

        history = self.get_history(session_id)
        history.append({"role": "user", "content": user_query})

        # 2. 工具意图识别与执行
        tools_used: List[str] = []
        observations: List[str] = []

        for city, info in self.WEATHER_DB.items():
            if city in user_query and "天气" in user_query:
                yield StreamEvent("tool_call", {"name": "get_weather", "arguments": {"city": city}})
                obs = f"{city}当前天气：{info}"
                tools_used.append("get_weather")
                observations.append(obs)
                yield StreamEvent("tool_result", {"name": "get_weather", "output": obs})

        math_hits = [m.strip() for m in _MATH_RE.findall(user_query) if any(op in m for op in "+-*/")]
        if math_hits:
            expr = math_hits[0]
            yield StreamEvent("tool_call", {"name": "safe_calculator", "arguments": {"expression": expr}})
            try:
                val = _safe_calc(expr)
                obs = f"计算结果：{expr} = {val}"
            except Exception as exc:
                obs = f"计算异常：{exc}"
            tools_used.append("safe_calculator")
            observations.append(obs)
            yield StreamEvent("tool_result", {"name": "safe_calculator", "output": obs})

        for kw, doc in self.KB_DB.items():
            if kw in user_query.lower():
                yield StreamEvent("tool_call", {"name": "search_internal_kb", "arguments": {"keyword": kw}})
                tools_used.append("search_internal_kb")
                observations.append(f"内部制度参考：{doc}")
                yield StreamEvent("tool_result", {"name": "search_internal_kb", "output": doc})

        # 3. 结合多轮记忆与工具观察合成最终回答
        remembered_name = self._extract_remembered_name(session_id)
        if observations:
            prefix = f"{remembered_name}您好，" if remembered_name else "您好，"
            reply = prefix + "已为您通过工具核实以下信息：" + "；".join(observations) + "。"
        elif "我叫什么" in user_query or "我是谁" in user_query:
            if remembered_name:
                reply = f"我记得您！您刚才告诉我您叫{remembered_name}，请问还有什么可以帮您？"
            else:
                reply = "您还没有告诉我您的称呼呢，方便介绍一下自己吗？"
        elif "我叫" in user_query and remembered_name:
            reply = f"很高兴认识您，{remembered_name}！我是星辰智脑，随时为您提供办公与研发协助。"
        else:
            prefix = f"{remembered_name}，" if remembered_name else ""
            reply = f"{prefix}收到您的问题「{user_query}」，星辰智脑已为您记录并持续提供协助。"

        # 4. 写入记忆并执行滑窗裁剪
        history.append({"role": "assistant", "content": reply})
        self._trim_history(session_id)

        # 5. 流式分片推送正文
        for i in range(0, len(reply), max(1, chunk_size)):
            yield StreamEvent("delta", {"text": reply[i : i + max(1, chunk_size)]})

        yield StreamEvent(
            "done",
            {
                "session_id": session_id,
                "blocked": False,
                "tools_used": tools_used,
                "history_len": len(self.get_history(session_id)),
            },
        )


if __name__ == "__main__":
    eng = StarMindIntegratedEngine()
    for q in ["你好，我叫林晓明", "请问我叫什么？顺便查下杭州天气并算 600 * 2 + 80"]:
        print(">>> 用户:", q)
        for ev in eng.stream_turn("demo_sess", q, chunk_size=12):
            if ev.event_type == "delta":
                print(ev.data["text"], end="", flush=True)
            else:
                print(f"\n[{ev.event_type}] {ev.data}")
        print("\n")

