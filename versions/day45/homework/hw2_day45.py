"""
Day 45 课后作业 2（企业实战）：将 Dify DSL 一键转换为 Mermaid 流程图
工单：STARMIND-045
"""

"""Day 45 作业 2 参考答案：Dify DSL 自动转 Mermaid 流程图。"""

from typing import Any, Dict, List


def dsl_to_mermaid(dsl: Dict[str, Any]) -> str:
    lines: List[str] = ["graph LR"]
    for n in dsl.get("nodes", []):
        lines.append(f'    {n["id"]}["{n["id"]} ({n["type"]})"]')
    for e in dsl.get("edges", []):
        handle = e.get("handle")
        if handle:
            lines.append(f'    {e["source"]} -->|{handle}| {e["target"]}')
        else:
            lines.append(f'    {e["source"]} --> {e["target"]}')
    return "\n".join(lines)


if __name__ == "__main__":
    demo = {
        "nodes": [{"id": "start", "type": "start"}, {"id": "end", "type": "end"}],
        "edges": [{"source": "start", "target": "end"}],
    }
    md = dsl_to_mermaid(demo)
    print(md)
    assert "start --> end" in md

