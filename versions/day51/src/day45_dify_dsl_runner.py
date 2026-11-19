"""Day 45 - 步骤一：类 Dify 声明式工作流 DSL 解析与离线执行引擎。"""

from __future__ import annotations

import re
from collections import defaultdict, deque
from typing import Any, Dict, List, Tuple

VAR_PATTERN = re.compile(r"\{\{#([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)#\}\}")


class DifyDSLRunner:
    """
    解析并执行类 Dify 声明式工作流 DSL：
    支持节点类型：start | knowledge_retrieval | if_else | llm | end
    """

    def __init__(self, dsl: Dict[str, Any], kb_docs: Dict[str, str] | None = None) -> None:
        self.dsl = dsl
        self.nodes: Dict[str, Dict[str, Any]] = {n["id"]: n for n in dsl.get("nodes", [])}
        self.edges: List[Dict[str, Any]] = dsl.get("edges", [])
        self.kb_docs = kb_docs or {
            "P0": "【P0 紧急工单 SLA】15 分钟内响应，自动抄送值班架构师与运维组。",
            "P2": "【P2 普通工单 SLA】4 个工作小时内响应，优先走知识库自助排查。",
        }

    def validate_dsl(self) -> None:
        """使用 Kahn 拓扑排序检测 DSL 是否存在非法环路或未定义节点引用。"""
        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = defaultdict(list)

        for edge in self.edges:
            src, dst = edge["source"], edge["target"]
            if src not in self.nodes or dst not in self.nodes:
                raise ValueError(f"DSL 边引用了不存在的节点: {src} -> {dst}")
            adj[src].append(dst)
            in_degree[dst] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        visited = 0
        while queue:
            cur = queue.popleft()
            visited += 1
            for nxt in adj[cur]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if visited != len(self.nodes):
            raise ValueError("DSL 校验失败：检测到循环依赖（非 DAG 工作流）")

    def _render_template(self, template: str, var_pool: Dict[str, Dict[str, Any]]) -> str:
        """将 {{#node_id.field#}} 替换为变量池中的真实值。"""
        def _replace(match: re.Match[str]) -> str:
            node_id, field_name = match.group(1), match.group(2)
            return str(var_pool.get(node_id, {}).get(field_name, ""))

        return VAR_PATTERN.sub(_replace, template)

    def _find_next_node(self, current_id: str, branch_handle: str = "default") -> str | None:
        for edge in self.edges:
            if edge["source"] == current_id and edge.get("handle", "default") == branch_handle:
                return edge["target"]
        return None

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_dsl()
        start_nodes = [n["id"] for n in self.nodes.values() if n["type"] == "start"]
        if len(start_nodes) != 1:
            raise ValueError("DSL 必须且只能包含一个 start 节点")

        var_pool: Dict[str, Dict[str, Any]] = {}
        trace: List[Dict[str, Any]] = []
        current_id: str | None = start_nodes[0]

        while current_id is not None:
            node = self.nodes[current_id]
            ntype = node["type"]
            branch_handle = "default"

            if ntype == "start":
                var_pool[current_id] = dict(inputs)
            elif ntype == "knowledge_retrieval":
                key_expr = self._render_template(node["query_template"], var_pool)
                matched = self.kb_docs.get(key_expr, "未命中专项 SLA，按常规工单流程处理。")
                var_pool[current_id] = {"context": matched}
            elif ntype == "if_else":
                left = self._render_template(node["left_template"], var_pool)
                right = str(node["equals"])
                passed = left == right
                branch_handle = "true" if passed else "false"
                var_pool[current_id] = {"branch": branch_handle, "matched": passed}
            elif ntype == "llm":
                rendered = self._render_template(node["prompt_template"], var_pool)
                var_pool[current_id] = {"text": f"[{node.get('model', 'qwen-plus')}] {rendered}"}
            elif ntype == "end":
                outputs = {
                    k: self._render_template(v, var_pool)
                    for k, v in node.get("outputs", {}).items()
                }
                var_pool[current_id] = outputs
                trace.append({"node_id": current_id, "type": ntype, "output": outputs})
                return {"outputs": outputs, "trace": trace, "var_pool": var_pool}
            else:
                raise ValueError(f"不支持的 DSL 节点类型: {ntype}")

            trace.append({"node_id": current_id, "type": ntype, "output": var_pool[current_id]})
            current_id = self._find_next_node(current_id, branch_handle)

        raise RuntimeError("DSL 执行意外结束：未到达 end 节点")


def sample_ticket_triage_dsl() -> Dict[str, Any]:
    """星辰数科运营部导出的工单分流演示 DSL。"""
    return {
        "name": "starmind-ticket-triage",
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "kb", "type": "knowledge_retrieval", "query_template": "{{#start.priority#}}"},
            {"id": "cond", "type": "if_else", "left_template": "{{#start.priority#}}", "equals": "P0"},
            {
                "id": "llm_urgent",
                "type": "llm",
                "model": "qwen-max",
                "prompt_template": "【紧急升级】工单: {{#start.query#}} | 依据: {{#kb.context#}}",
            },
            {
                "id": "llm_normal",
                "type": "llm",
                "model": "qwen-turbo",
                "prompt_template": "【标准处理】工单: {{#start.query#}} | 依据: {{#kb.context#}}",
            },
            {
                "id": "end_urgent",
                "type": "end",
                "outputs": {"reply": "{{#llm_urgent.text#}}", "level": "URGENT"},
            },
            {
                "id": "end_normal",
                "type": "end",
                "outputs": {"reply": "{{#llm_normal.text#}}", "level": "NORMAL"},
            },
        ],
        "edges": [
            {"source": "start", "target": "kb"},
            {"source": "kb", "target": "cond"},
            {"source": "cond", "target": "llm_urgent", "handle": "true"},
            {"source": "cond", "target": "llm_normal", "handle": "false"},
            {"source": "llm_urgent", "target": "end_urgent"},
            {"source": "llm_normal", "target": "end_normal"},
        ],
    }


if __name__ == "__main__":
    runner = DifyDSLRunner(sample_ticket_triage_dsl())
    res = runner.run({"priority": "P0", "query": "核心支付网关 502 超时"})
    print("输出:", res["outputs"])
    print("执行路径:", [t["node_id"] for t in res["trace"]])

