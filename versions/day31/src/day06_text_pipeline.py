"""
STARMIND-006 模块一：函数式文本处理管道与动态 API 请求构造器。
演示默认参数避坑（None 哨兵）、*args 管道组合、**kwargs 参数透传与 lambda 处理器。
"""

from typing import Callable, Dict, Any, List, Optional


def strip_and_collapse(text: str) -> str:
    """处理器 1：去除首尾空白并折叠连续空格与换行。"""
    return " ".join(text.replace("\u3000", " ").split())


def redact_secret_key(text: str) -> str:
    """处理器 2：对意外粘贴进提问中的 sk- 密钥片段做简单遮蔽。"""
    tokens = text.split(" ")
    safe_tokens = ["sk-***REDACTED***" if t.startswith("sk-") else t for t in tokens]
    return " ".join(safe_tokens)


def run_pipeline(text: str, *processors: Callable[[str], str]) -> str:
    """
    函数式管道调度器：将输入文本依次送入 *processors 中的每个函数处理。
    支持传入具名函数或 lambda 匿名函数。
    """
    result = text
    for fn in processors:
        result = fn(result)
    return result


def build_chat_request(
    model: str,
    *user_messages: str,
    system_prompt: Optional[str] = None,
    **extra_params: Any,
) -> Dict[str, Any]:
    """
    动态构建大模型 Chat Completions 请求体。
    - *user_messages 接收一条或多条用户消息
    - **extra_params 透传 temperature、max_tokens 等可选超参
    """
    # 安全初始化可变列表（绝不用 messages=[] 作为默认参数）
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for msg in user_messages:
        messages.append({"role": "user", "content": msg})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    # 过滤掉值为 None 的额外超参后合并
    for key, value in extra_params.items():
        if value is not None:
            payload[key] = value
    return payload


if __name__ == "__main__":
    raw = "  帮我查下  sk-secret123456  为什么报 401 错误？ \n "
    # 自由组合两个具名处理器 + 一个 lambda 截断处理器
    cleaned = run_pipeline(
        raw,
        strip_and_collapse,
        redact_secret_key,
        lambda s: s[:40],
    )
    req = build_chat_request(
        "deepseek-chat",
        cleaned,
        system_prompt="你是星辰智脑运维助手",
        temperature=0.2,
        max_tokens=512,
    )
    print("清洗结果:", cleaned)
    print("请求体  :", req)

