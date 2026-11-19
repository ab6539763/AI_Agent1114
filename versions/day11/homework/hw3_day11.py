"""
Day 11 课后作业 3（架构进阶）：架构进阶：从大模型回复中提取所有 Markdown 代码块
工单：STARMIND-011
"""

"""Day 11 课后题 3：大模型 Markdown 回复代码块提取器。"""

import re
from typing import List, Dict

CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)


def extract_code_blocks(markdown_text: str) -> List[Dict[str, str]]:
    """提取 Markdown 中所有围栏代码块及其语言类型。"""
    blocks: List[Dict[str, str]] = []
    for lang, code in CODE_BLOCK_RE.findall(markdown_text):
        blocks.append({"lang": lang.lower() or "text", "code": code.strip()})
    return blocks


if __name__ == "__main__":
    reply = "示例如下：\n```python\nprint('hello')\n```\n配置：\n```json\n{\"ok\": true}\n```"
    print(extract_code_blocks(reply))

