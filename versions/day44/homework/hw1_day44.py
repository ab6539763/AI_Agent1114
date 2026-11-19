"""
Day 44 课后作业 1（基础巩固）：为 MCP Server 增加 prompts/list 与 prompts/get 原语
工单：STARMIND-044
"""

"""Day 44 作业 1 参考答案：MCP Prompts 原语处理器。"""

from typing import Dict

PROMPTS = {
    "weekly_report": "请以【{dept}】负责人视角，按“本周成果/风险阻塞/下周计划”三段式输出周报。"
}


def get_prompt(name: str, arguments: Dict[str, str]) -> Dict[str, object]:
    if name not in PROMPTS:
        raise KeyError(f"未找到提示词模板: {name}")
    text = PROMPTS[name].format(**arguments)
    return {"messages": [{"role": "user", "content": {"type": "text", "text": text}}]}


if __name__ == "__main__":
    res = get_prompt("weekly_report", {"dept": "AI 平台部"})
    print(res)
    assert "AI 平台部" in res["messages"][0]["content"]["text"]

