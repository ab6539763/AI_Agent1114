"""
STARMIND-012 模块二：星辰智脑命令行 AI 问答小程序 v0.1。
演示单轮提问封装、控制台格式化输出与可测试的 CLI 交互循环。
"""

from typing import List, Optional

from day12_llm_http_client import LLMAPIError, LLMRequestConfig, LLMResponse, StarMindHTTPClient

DEFAULT_SYSTEM_PROMPT = "你是杭州星辰数科内部 AI 助手「星辰智脑」，请用简洁专业中文回答问题。"


def ask_once(
    client: StarMindHTTPClient,
    question: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> LLMResponse:
    """发起一次单轮 AI 问答。"""
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("提问内容不能为空")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": cleaned},
    ]
    return client.chat(messages)


def format_qa_panel(question: str, response: LLMResponse) -> str:
    """将问答结果格式化为清晰的终端展示文本。"""
    return (
        f"问：{question}\n"
        f"答：{response.content}\n"
        f"—— [来源: {response.source} | 模型: {response.model} | "
        f"Tokens: {response.total_tokens} | 耗时: {response.latency_ms}ms]"
    )


def run_cli_qa(
    client: StarMindHTTPClient,
    inputs: Optional[List[str]] = None,
) -> List[str]:
    """
    运行命令行问答循环。
    - 传入 inputs 列表时按脚本逐条执行（适合演示与自动化测试，不阻塞）；
    - inputs 为 None 时进入终端交互式 input() 模式。
    """
    outputs: List[str] = []
    script_iter = iter(inputs) if inputs is not None else None

    while True:
        if script_iter is not None:
            try:
                raw_q = next(script_iter)
            except StopIteration:
                break
        else:
            raw_q = input("请输入问题（输入 /exit 退出）> ")

        q = raw_q.strip()
        if q.lower() in {"/exit", "exit", "quit"}:
            outputs.append("已退出星辰智脑问答小程序。")
            break
        if not q:
            outputs.append("提示：问题不能为空，请重新输入。")
            continue

        try:
            resp = ask_once(client, q)
            outputs.append(format_qa_panel(q, resp))
        except (ValueError, LLMAPIError) as exc:
            outputs.append(f"调用失败：{exc}")

    return outputs


if __name__ == "__main__":
    # 使用预设问题脚本运行演示，无需手动按键输入
    demo_client = StarMindHTTPClient(LLMRequestConfig(model="deepseek-chat"))
    demo_questions = [
        "星辰数科差旅报销流程是什么？",
        "DeepSeek API 兼容什么协议格式？",
        "/exit",
    ]
    for block in run_cli_qa(demo_client, inputs=demo_questions):
        print(block)
        print("-" * 50)

