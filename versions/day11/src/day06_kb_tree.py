"""
STARMIND-006 模块二：知识库嵌套目录树递归解析与 Top-N 排序器。
演示递归函数（基准条件 + 递归分解）、lambda 排序与深度安全控制。
"""

from typing import Dict, Any, List


def flatten_kb_tree(
    node: Dict[str, Any],
    prefix: str = "",
    max_depth: int = 20,
) -> List[Dict[str, Any]]:
    """
    递归遍历知识库嵌套目录树，提取所有文件节点及其完整逻辑路径。
    每个节点格式：
      - 文件: {"type": "file", "name": "faq.md", "size_kb": 12}
      - 目录: {"type": "dir", "name": "客服部", "children": [...]}
    """
    if max_depth < 0:
        raise RecursionError("知识库目录嵌套层级超过安全上限")

    name = str(node.get("name", ""))
    current_path = f"{prefix}/{name}" if prefix else name

    # 基准条件（Base Case）：到达文件叶节点，直接返回单元素列表
    if node.get("type") == "file":
        return [{"path": current_path, "size_kb": int(node.get("size_kb", 0))}]

    # 递归步骤：遍历目录的所有子节点并汇总结果
    results: List[Dict[str, Any]] = []
    for child in node.get("children", []):
        results.extend(flatten_kb_tree(child, prefix=current_path, max_depth=max_depth - 1))
    return results


def top_largest_docs(tree: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
    """找出知识库中体积最大的前 top_n 份文档（使用 lambda 多键排序）。"""
    all_files = flatten_kb_tree(tree)
    # 先按 size_kb 降序，体积相同时按 path 字母升序，保证排序稳定
    ranked = sorted(all_files, key=lambda doc: (-doc["size_kb"], doc["path"]))
    return ranked[:top_n]


if __name__ == "__main__":
    sample_kb = {
        "type": "dir",
        "name": "StarMind_KB",
        "children": [
            {"type": "file", "name": "readme.md", "size_kb": 5},
            {
                "type": "dir",
                "name": "研发部",
                "children": [
                    {"type": "file", "name": "api_spec.md", "size_kb": 48},
                    {
                        "type": "dir",
                        "name": "新人培训",
                        "children": [{"type": "file", "name": "python_guide.md", "size_kb": 120}],
                    },
                ],
            },
            {"type": "file", "name": "refund_policy.md", "size_kb": 32},
        ],
    }
    print("Top 2 最大文档:", top_largest_docs(sample_kb, top_n=2))

