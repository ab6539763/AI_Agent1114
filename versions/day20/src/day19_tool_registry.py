"""
StarMind Day 19 - 步骤一：OpenAI 规范 Tool Schema 注册中心与企业三大基础工具
包含：get_weather（天气查询）、safe_calculator（AST安全计算器）、search_internal_kb（内部知识库）。
"""

import ast
import json
import operator
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


# AST 安全算术白名单映射
_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_eval_math(expression: str) -> float:
    """
    基于 AST 抽象语法树白名单的安全数学表达式求值器。
    彻底拒绝函数调用、属性访问、变量注入，并对超大幂运算做防 DoS 拦截。
    """
    if not expression or len(expression) > 120:
        raise ValueError("数学表达式为空或过长（上限 120 字符）")

    tree = ast.parse(expression, mode="eval")

    def _eval_node(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](_eval_node(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 20:
                raise ValueError("安全拦截：幂运算指数绝对值不允许超过 20")
            if isinstance(node.op, ast.Div) and right == 0:
                raise ZeroDivisionError("除数不能为 0")
            return _BIN_OPS[type(node.op)](left, right)
        raise ValueError(f"安全拦截：不允许的表达式节点 {type(node).__name__}")

    return round(_eval_node(tree), 6)


def get_weather(city: str) -> Dict[str, Any]:
    """查询指定城市实时天气（离线仿真企业气象网关数据）。"""
    weather_db = {
        "杭州": {"city": "杭州", "weather": "多云转小雨", "temp_c": 18, "advice": "建议携带折叠伞"},
        "北京": {"city": "北京", "weather": "晴朗微风", "temp_c": 11, "advice": "早晚温差大注意保暖"},
        "上海": {"city": "上海", "weather": "阴天", "temp_c": 19, "advice": "体感舒适"},
        "深圳": {"city": "深圳", "weather": "晴间多云", "temp_c": 26, "advice": "适合短袖出行"},
    }
    clean_city = city.strip().replace("市", "")
    if clean_city in weather_db:
        return {"status": "ok", **weather_db[clean_city]}
    return {"status": "not_found", "city": city, "message": f"暂未收录城市 {city} 的实时气象数据"}


def safe_calculator(expression: str) -> Dict[str, Any]:
    """执行精确数学计算。"""
    result = safe_eval_math(expression)
    return {"status": "ok", "expression": expression, "result": result}


def search_internal_kb(keyword: str) -> Dict[str, Any]:
    """检索杭州星辰数科内部规章制度知识库。"""
    kb_docs = [
        {"id": "HR-001", "title": "差旅住宿报销标准", "content": "一线及新一线城市（北京/上海/深圳/杭州）住宿上限 600 元/晚，其余城市 400 元/晚，需提供增值税电子专票。"},
        {"id": "IT-002", "title": "内网 VPN 申请流程", "content": "新员工入职后在 OA 发起『IT权限申请』，直属主管审批后 30 分钟内自动开通 WireGuard VPN。"},
        {"id": "FIN-003", "title": "研发云资源预算规范", "content": "单项目调用大模型 API 月度预算超过 2000 元需提交架构委员会评审并开启 Prompt 缓存。"},
    ]
    kw = keyword.strip().lower()
    hits = [
        doc for doc in kb_docs
        if kw in doc["title"].lower() or kw in doc["content"].lower() or any(ch in doc["content"] for ch in kw.split() if len(ch) >= 2)
    ]
    return {"status": "ok", "keyword": keyword, "hits": hits, "count": len(hits)}


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Dict[str, Any]]

    def to_openai_schema(self) -> Dict[str, Any]:
        """导出 100% 符合 OpenAI Chat Completions tools 规范的 Schema 字典。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """星辰智脑统一工具注册与安全调度中心。"""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def export_openai_tools(self) -> List[Dict[str, Any]]:
        return [spec.to_openai_schema() for spec in self._tools.values()]

    def execute(self, name: str, raw_arguments: str | Dict[str, Any]) -> str:
        """
        安全执行指定工具：
        - 自动反序列化 JSON 字符串参数
        - 校验必填参数
        - 捕获一切执行异常并包装为结构化错误 JSON，绝不中断主循环
        """
        if name not in self._tools:
            return json.dumps({"status": "error", "error": f"未注册的工具: {name}"}, ensure_ascii=False)

        spec = self._tools[name]
        try:
            args = json.loads(raw_arguments) if isinstance(raw_arguments, str) else dict(raw_arguments)
            required = spec.parameters.get("required", [])
            missing = [r for r in required if r not in args]
            if missing:
                return json.dumps({"status": "error", "error": f"缺少必填参数: {missing}"}, ensure_ascii=False)
            result = spec.handler(**args)
            return json.dumps(result, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False)


def build_default_registry() -> ToolRegistry:
    """装配星辰智脑默认三大业务工具。"""
    reg = ToolRegistry()
    reg.register(
        ToolSpec(
            name="get_weather",
            description="查询指定中国城市的实时天气与出行建议。",
            parameters={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市中文名，例如：杭州、北京、上海、深圳"},
                },
                "required": ["city"],
            },
            handler=get_weather,
        )
    )
    reg.register(
        ToolSpec(
            name="safe_calculator",
            description="执行高精度四则运算与括号表达式计算（适用于金额、税率、折扣核算）。",
            parameters={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "纯数学表达式，例如：(12800 / 1.06) * 0.06"},
                },
                "required": ["expression"],
            },
            handler=safe_calculator,
        )
    )
    reg.register(
        ToolSpec(
            name="search_internal_kb",
            description="检索杭州星辰数科内部规章制度（差旅报销、VPN申请、预算规范）。",
            parameters={
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "检索关键词，例如：差旅、VPN、预算"},
                },
                "required": ["keyword"],
            },
            handler=search_internal_kb,
        )
    )
    return reg


if __name__ == "__main__":
    registry = build_default_registry()
    print("导出的 OpenAI Tools Schema 数量:", len(registry.export_openai_tools()))
    print("天气测试:", registry.execute("get_weather", '{"city": "杭州"}'))
    print("计算测试:", registry.execute("safe_calculator", '{"expression": "600 * 3 + 120"}'))
    print("知识库测试:", registry.execute("search_internal_kb", '{"keyword": "差旅"}'))

