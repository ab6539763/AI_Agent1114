"""Day 39 - 步骤一：企业工具注册表、内网知识搜索与 AST 安全计算器。"""

from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from typing import Callable, Dict, List


# AST 允许的安全二元运算与一元运算白名单
_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# 模拟星辰数科企业内网知识库条目
INTERNAL_KB: List[Dict[str, str]] = [
    {
        "title": "杭州星辰数科2026差旅报销标准",
        "keywords": "上海 北京 深圳 一线 差旅 住宿 餐补 报销 标准",
        "content": "一线城市（北京、上海、深圳、广州）住宿标准上限 600 元/晚，餐补 120 元/天，市内交通实报实销上限 80 元/天。",
    },
    {
        "title": "杭州星辰数科二线城市差旅标准",
        "keywords": "杭州 南京 成都 武汉 二线 差旅 住宿 餐补 报销",
        "content": "二线城市（杭州、南京、成都、武汉等）住宿标准上限 450 元/晚，餐补 100 元/天。",
    },
    {
        "title": "星辰数科年假与加班调休管理办法",
        "keywords": "年假 调休 请假 工龄 天数",
        "content": "入职满 1 年享 5 天带薪年假，满 3 年享 10 天；法定节假日加班按日薪 300% 核算。",
    },
]


def _eval_ast_node(node: ast.AST) -> float:
    """递归安全求值 AST 节点，严禁函数调用、属性访问与变量读取。"""
    if isinstance(node, ast.Expression):
        return _eval_ast_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_ast_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left = _eval_ast_node(node.left)
        right = _eval_ast_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("指数绝对值不能超过 100，已拦截潜在资源耗尽攻击")
        if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)) and right == 0:
            raise ValueError("除数不能为 0")
        return _BINARY_OPS[type(node.op)](left, right)
    raise ValueError(f"不允许的表达式节点: {type(node).__name__}")


def safe_calculator(expression: str) -> str:
    """安全数学计算器：仅支持数字和 + - * / // % ** 括号运算。"""
    cleaned = expression.strip()
    if not cleaned:
        return "错误：表达式不能为空"
    try:
        tree = ast.parse(cleaned, mode="eval")
        value = _eval_ast_node(tree)
        # 整数结果去除多余的 .0，保留清晰可读性
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}"
    except Exception as exc:
        return f"计算失败：{exc}"


def internal_search(query: str) -> str:
    """检索星辰数科企业内网规章制度，按关键词命中数排序返回最相关条文。"""
    tokens = [t.strip() for t in query.replace("，", " ").replace(",", " ").split() if t.strip()]
    if not tokens:
        return "未提供检索关键词。"
    scored: List[tuple[int, Dict[str, str]]] = []
    for doc in INTERNAL_KB:
        haystack = f"{doc['title']} {doc['keywords']} {doc['content']}"
        score = sum(1 for tok in tokens if tok in haystack)
        if score > 0:
            scored.append((score, doc))
    if not scored:
        return f"未在内网知识库中找到与“{query}”相关的制度条文。"
    scored.sort(key=lambda item: item[0], reverse=True)
    top_doc = scored[0][1]
    return f"《{top_doc['title']}》：{top_doc['content']}"


@dataclass
class SimpleTool:
    """极简工具元数据包装类。"""

    name: str
    description: str
    func: Callable[[str], str]


class ToolRegistry:
    """工具注册中心：统一管理工具注册、Prompt 文档渲染与安全调用。"""

    def __init__(self) -> None:
        self._tools: Dict[str, SimpleTool] = {}

    def register(self, name: str, description: str, func: Callable[[str], str]) -> None:
        self._tools[name] = SimpleTool(name=name, description=description, func=func)

    def get(self, name: str) -> SimpleTool | None:
        return self._tools.get(name)

    def list_names(self) -> List[str]:
        return list(self._tools.keys())

    def render_prompt_docs(self) -> str:
        """渲染给大模型阅读的工具说明书。"""
        lines = [f"- {t.name}: {t.description}" for t in self._tools.values()]
        return "\\n".join(lines)

    def execute(self, name: str, action_input: str) -> str:
        tool = self._tools.get(name)
        if tool is None:
            available = ", ".join(self.list_names())
            return f"工具调用失败：未知工具 '{name}'。当前可用工具仅包括：[{available}]。"
        try:
            return tool.func(action_input)
        except Exception as exc:
            return f"工具 '{name}' 执行异常：{exc}"


def build_default_registry() -> ToolRegistry:
    """构建星辰数科默认工具集。"""
    registry = ToolRegistry()
    registry.register(
        name="internal_search",
        description="搜索星辰数科内网制度（差旅标准、年假规定等），输入空格分隔的关键词。",
        func=internal_search,
    )
    registry.register(
        name="safe_calculator",
        description="精确计算数学表达式（支持加减乘除与括号），例如 '(600 + 120) * 3'。",
        func=safe_calculator,
    )
    return registry


if __name__ == "__main__":
    reg = build_default_registry()
    print("=== 已注册工具说明书 ===")
    print(reg.render_prompt_docs())
    print("搜索测试:", reg.execute("internal_search", "上海 差旅 住宿"))
    print("计算测试:", reg.execute("safe_calculator", "(600 + 120) * 3"))
    print("恶意注入拦截:", reg.execute("safe_calculator", "__import__('os').system('ls')"))

