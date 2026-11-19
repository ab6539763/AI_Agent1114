"""
Day 35 课后作业 2（企业实战）：作业二：实现 LlamaIndex 风格 MetadataPostprocessor（元数据过滤后处理器）
工单：STARMIND-035
"""

"""Day 35 作业二参考答案：基于部门权限的 NodePostprocessor"""
from typing import List, Sequence
from src.day35_llamaindex_core import NodeWithScore, TextNode


class DepartmentNodePostprocessor:
    def __init__(self, allowed_dept: str) -> None:
        self.allowed_dept = allowed_dept

    def postprocess_nodes(self, nodes: Sequence[NodeWithScore]) -> List[NodeWithScore]:
        return [
            n
            for n in nodes
            if n.node.metadata.get("department", "public") in (self.allowed_dept, "public")
        ]


if __name__ == "__main__":
    sample_nodes = [
        NodeWithScore(TextNode("公共差旅制度", "n1", {"department": "public"}), 0.9),
        NodeWithScore(TextNode("研发架构机密", "n2", {"department": "rd"}), 0.85),
        NodeWithScore(TextNode("财务薪酬明细", "n3", {"department": "finance"}), 0.88),
    ]
    filtered = DepartmentNodePostprocessor("rd").postprocess_nodes(sample_nodes)
    print("研发员工可见节点:", [n.node.node_id for n in filtered])
    assert [n.node.node_id for n in filtered] == ["n1", "n2"]

