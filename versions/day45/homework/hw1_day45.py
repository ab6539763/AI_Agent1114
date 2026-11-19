"""
Day 45 课后作业 1（基础巩固）：为 Dify DSL 增加悬空变量引用静态检查
工单：STARMIND-045
"""

"""Day 45 作业 1 参考答案：DSL 悬空变量引用静态检查器。"""

import re
from typing import Any, Dict, List

VAR_RE = re.compile(r"\{\{#([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)#\}\}")


def find_broken_var_refs(dsl: Dict[str, Any]) -> List[str]:
    valid_ids = {n["id"] for n in dsl.get("nodes", [])}
    broken: List[str] = []
    for node in dsl.get("nodes", []):
        for key in ("prompt_template", "query_template", "left_template"):
            text = node.get(key, "")
            for ref_node, ref_field in VAR_RE.findall(text):
                if ref_node not in valid_ids:
                    broken.append(f"{node['id']}->{ref_node}.{ref_field}")
    return broken


if __name__ == "__main__":
    bad_dsl = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "llm1", "type": "llm", "prompt_template": "你好 {{#deleted_node.text#}}"},
        ]
    }
    issues = find_broken_var_refs(bad_dsl)
    print("发现悬空变量引用:", issues)
    assert issues == ["llm1->deleted_node.text"]

