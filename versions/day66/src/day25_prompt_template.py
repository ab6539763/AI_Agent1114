"""
Day 25 - 步骤二：PromptTemplate 与 ChatPromptTemplate 工程化实现
对应生产包：langchain_core.prompts
"""

from __future__ import annotations

import string
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

# 确保无论是直接运行本脚本还是通过 pytest 导入都能找到 src 模块
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    StarMindChatModel,
    SystemMessage,
)


def extract_template_variables(template: str) -> List[str]:
    """使用标准库 string.Formatter 精确提取模板中的 {var} 变量名（自动忽略转义 {{}}）。"""
    formatter = string.Formatter()
    vars_found: List[str] = []
    for _, field_name, _, _ in formatter.parse(template):
        if field_name is not None and field_name not in vars_found:
            # 去掉可能存在的属性或下标访问，如 user.name -> user
            root_name = field_name.split(".")[0].split("[")[0]
            if root_name and root_name not in vars_found:
                vars_found.append(root_name)
    return vars_found


class PromptTemplate:
    """单段文本提示词模板，支持变量自动校验与 partial 局部固化。"""

    def __init__(
        self,
        template: str,
        partial_variables: Dict[str, Any] | None = None,
    ) -> None:
        self.template = template
        self.partial_variables: Dict[str, Any] = dict(partial_variables or {})
        all_vars = extract_template_variables(template)
        self.input_variables: List[str] = [
            v for v in all_vars if v not in self.partial_variables
        ]

    @classmethod
    def from_template(cls, template: str) -> "PromptTemplate":
        return cls(template=template)

    def partial(self, **kwargs: Any) -> "PromptTemplate":
        """返回一个新模板实例，预先固化部分固定上下文（如公司名称、当前年份）。"""
        merged = {**self.partial_variables, **kwargs}
        return PromptTemplate(template=self.template, partial_variables=merged)

    def format(self, **kwargs: Any) -> str:
        merged = {**self.partial_variables, **kwargs}
        missing = [v for v in self.input_variables if v not in merged]
        if missing:
            raise ValueError(f"Prompt 渲染失败，缺少必填变量: {missing}")
        return self.template.format(**merged)


class ChatPromptTemplate:
    """
    多角色对话提示词模板，完全对齐 LangChain ChatPromptTemplate.from_messages 用法。
    支持 ('system', ...), ('human', ...), ('ai', ...) 三元组/二元组定义。
    """

    ROLE_MAP = {
        "system": SystemMessage,
        "human": HumanMessage,
        "user": HumanMessage,
        "ai": AIMessage,
        "assistant": AIMessage,
    }

    def __init__(
        self,
        messages: Sequence[Tuple[str, str]],
        partial_variables: Dict[str, Any] | None = None,
    ) -> None:
        self._raw_messages: List[Tuple[str, PromptTemplate]] = []
        self.partial_variables: Dict[str, Any] = dict(partial_variables or {})
        input_vars: List[str] = []

        for role, tpl_str in messages:
            role_key = role.lower()
            if role_key not in self.ROLE_MAP:
                raise ValueError(f"不支持的消息角色: {role}")
            pt = PromptTemplate(tpl_str, partial_variables=self.partial_variables)
            self._raw_messages.append((role_key, pt))
            for v in pt.input_variables:
                if v not in input_vars:
                    input_vars.append(v)

        self.input_variables = input_vars

    @classmethod
    def from_messages(
        cls,
        messages: Sequence[Tuple[str, str]],
        partial_variables: Dict[str, Any] | None = None,
    ) -> "ChatPromptTemplate":
        return cls(messages=messages, partial_variables=partial_variables)

    def partial(self, **kwargs: Any) -> "ChatPromptTemplate":
        merged = {**self.partial_variables, **kwargs}
        raw_pairs = [(r, pt.template) for r, pt in self._raw_messages]
        return ChatPromptTemplate(messages=raw_pairs, partial_variables=merged)

    def format_messages(self, **kwargs: Any) -> List[BaseMessage]:
        merged = {**self.partial_variables, **kwargs}
        missing = [v for v in self.input_variables if v not in merged]
        if missing:
            raise ValueError(f"ChatPromptTemplate 缺少必填变量: {missing}")

        rendered: List[BaseMessage] = []
        for role_key, pt in self._raw_messages:
            msg_cls = self.ROLE_MAP[role_key]
            rendered.append(msg_cls(content=pt.format(**merged)))
        return rendered


def build_it_ticket_prompt() -> ChatPromptTemplate:
    """构建星辰数科 IT 工单分类 Few-Shot 模板，演示 partial 与少样本引导。"""
    base_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是{company}的IT服务台专家。请根据员工工单输出分类与首响建议，禁止编造不存在的流程。",
            ),
            ("human", "工单示例：我的MacBook屏幕闪烁黑屏了"),
            ("ai", "【工单分类】硬件设备类 | 【优先级】P2 | 【建议】请携带资产编号前往B座3楼IT运维台检测。"),
            ("human", "部门：{dept}\n员工反馈：{issue}"),
        ]
    )
    # 预先固化公司名称，业务调用方只需传 dept 和 issue
    return base_prompt.partial(company="杭州星辰数科")


if __name__ == "__main__":
    prompt = build_it_ticket_prompt()
    print("待填充变量:", prompt.input_variables)
    msgs = prompt.format_messages(dept="AI平台部", issue="我的SSO账号提示密码过期登不进去了")
    for m in msgs:
        print(f"  [{m.role}] {m.content}")

    llm = StarMindChatModel()
    reply = llm.invoke(msgs)
    print("\nAI 响应:", reply.content)

