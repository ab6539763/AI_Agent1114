"""Day 40 - 步骤一：@tool 装饰器、JSON Schema 自动提取与安全工具三件套。"""

from __future__ import annotations

import ast
import inspect
import operator
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints

from pydantic import BaseModel, Field, ValidationError, create_model


class StructuredTool:
    """对齐 LangChain StructuredTool 核心设计：封装函数、Schema 与运行时校验。"""

    def __init__(
        self,
        name: str,
        description: str,
        func: Callable[..., Any],
        args_schema: Type[BaseModel],
    ) -> None:
        self.name = name
        self.description = description
        self.func = func
        self.args_schema = args_schema

    def to_openai_schema(self) -> Dict[str, Any]:
        """导出符合 OpenAI / Qwen Function Calling 规范的 JSON Schema。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_schema.model_json_schema(),
            },
        }

    def invoke(self, raw_args: Dict[str, Any]) -> str:
        """先经 Pydantic 校验并转换参数类型，再安全执行底层函数。"""
        try:
            validated = self.args_schema(**raw_args)
        except ValidationError as exc:
            details = "; ".join(
                f"参数 {'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()
            )
            return f"参数校验失败：{details}"
        try:
            result = self.func(**validated.model_dump())
            return str(result)
        except Exception as exc:
            return f"工具执行异常：{exc}"


def tool(func: Callable[..., Any]) -> StructuredTool:
    """
    极简 @tool 装饰器：自动提取函数名、docstring、类型注解与默认值，
    构建 Pydantic 校验模型并包装为 StructuredTool。
    """
    doc = (inspect.getdoc(func) or "").strip()
    if not doc:
        raise ValueError(f"工具函数 '{func.__name__}' 必须编写 docstring 作为工具说明")

    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    fields: Dict[str, Any] = {}

    for param_name, param in sig.parameters.items():
        annotation = type_hints.get(param_name, str)
        if param.default is inspect.Parameter.empty:
            fields[param_name] = (annotation, Field(..., description=f"参数 {param_name}"))
        else:
            fields[param_name] = (annotation, Field(default=param.default, description=f"参数 {param_name}"))

    args_model = create_model(f"{func.__name__.title()}Args", **fields)
    return StructuredTool(
        name=func.__name__,
        description=doc,
        func=func,
        args_schema=args_model,
    )


# ----------------- 企业级安全工具三件套 -----------------

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def _safe_eval_expr(expression: str) -> float:
    def _walk(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            left, right = _walk(node.left), _walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 50:
                raise ValueError("指数超过安全上限 50")
            return _SAFE_OPS[type(node.op)](left, right)
        raise ValueError(f"禁止执行的语法节点: {type(node).__name__}")

    return _walk(ast.parse(expression.strip(), mode="eval"))


def build_enterprise_tools(workspace_dir: Path) -> List[StructuredTool]:
    """构建绑定到指定安全沙箱目录的企业工具集。"""
    base_dir = workspace_dir.resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    docs_db = [
        {"id": "DOC-01", "topic": "星辰数科Q3研发目标", "content": "Q3目标：星辰智脑日活突破5000，平均响应延迟低于1.8秒。"},
        {"id": "DOC-02", "topic": "发布上线审批规范", "content": "生产环境发布需至少1名架构师Approved且单测覆盖率不低于80%。"},
    ]

    @tool
    def knowledge_search(keyword: str, top_k: int = 2) -> str:
        """检索星辰数科内部研发文档与规范，支持指定返回条数 top_k。"""
        hits = [d for d in docs_db if keyword in d["topic"] or keyword in d["content"]]
        if not hits:
            return f"未检索到包含 '{keyword}' 的文档。"
        return "\n".join(f"[{d['id']}] {d['topic']}: {d['content']}" for d in hits[:top_k])

    @tool
    def sandbox_python_calc(expression: str) -> str:
        """在 AST 安全沙箱中执行数学表达式计算，严禁函数调用与系统命令。"""
        val = _safe_eval_expr(expression)
        return str(int(val)) if val.is_integer() else f"{val:.2f}"

    @tool
    def safe_write_file(filename: str, content: str) -> str:
        """在受限工作区目录内写入文本文件，自动防御路径穿越攻击。"""
        target = (base_dir / filename).resolve()
        if not target.is_relative_to(base_dir):
            raise PermissionError(f"安全拦截：禁止访问工作区外路径 '{filename}'")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"已安全写入文件: {target.relative_to(base_dir)} ({len(content)} 字符)"

    @tool
    def safe_read_file(filename: str) -> str:
        """在受限工作区目录内读取文本文件内容，自动防御路径穿越攻击。"""
        target = (base_dir / filename).resolve()
        if not target.is_relative_to(base_dir):
            raise PermissionError(f"安全拦截：禁止读取工作区外路径 '{filename}'")
        if not target.exists():
            return f"文件不存在: {filename}"
        return target.read_text(encoding="utf-8")

    return [knowledge_search, sandbox_python_calc, safe_write_file, safe_read_file]


if __name__ == "__main__":
    import tempfile
    import json

    with tempfile.TemporaryDirectory() as tmp:
        tools = build_enterprise_tools(Path(tmp))
        print("=== 自动提取的 JSON Schema 示例 ===")
        print(json.dumps(tools[0].to_openai_schema(), ensure_ascii=False, indent=2))
        print("安全写入:", tools[2].invoke({"filename": "weekly.md", "content": "# 本周进展\n完成工具体系"}))
        print("路径穿越拦截:", tools[3].invoke({"filename": "../../etc/passwd"}))

