"""
Day 35 课后作业 1（基础巩固）：作业一：实现双向邻域扩展器（同时拉取 PREVIOUS + CURRENT + NEXT）
工单：STARMIND-035
"""

"""Day 35 作业一参考答案：TextNode 双向邻域扩展器"""
from typing import Dict
from src.day35_llamaindex_core import Document, SentenceNodeParser, TextNode


def expand_bidirectional(node_map: Dict[str, TextNode], hit_node: TextNode) -> str:
    parts = []
    prev_id = hit_node.relationships.get("PREVIOUS")
    next_id = hit_node.relationships.get("NEXT")
    if prev_id and prev_id in node_map:
        parts.append(node_map[prev_id].text)
    parts.append(hit_node.text)
    if next_id and next_id in node_map:
        parts.append(node_map[next_id].text)
    return "".join(parts)


if __name__ == "__main__":
    doc = Document("一线城市住宿上限600元。上述标准适用于实习生。超标需经VP审批。", doc_id="d1")
    nodes = SentenceNodeParser(1).get_nodes_from_documents([doc])
    nmap = {n.node_id: n for n in nodes}
    merged = expand_bidirectional(nmap, nodes[1])
    print("双向扩展上下文:", merged)
    assert "600元" in merged and "VP审批" in merged

