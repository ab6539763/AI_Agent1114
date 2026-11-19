"""
Day 57 课后作业 1（基础巩固）：基础巩固：为安全护栏增加英文越狱关键词与敏感词自定义热更新接口
工单：STARMIND-057
"""

from src.day57_security_guardrail import GuardrailCheckResult, SecurityGuardrail


class DynamicGuardrail(SecurityGuardrail):
    def __init__(self) -> None:
        self.extra_blocked: set[str] = set()

    def add_blocked_keyword(self, word: str) -> None:
        self.extra_blocked.add(word.strip())

    def check_input(self, user_text: str) -> GuardrailCheckResult:
        base = super().check_input(user_text)
        if not base.allowed:
            return base
        for kw in self.extra_blocked:
            if kw and kw in user_text:
                return GuardrailCheckResult(False, "", f"命中动态黑名单词: {kw}")
        return base


dg = DynamicGuardrail()
dg.add_blocked_keyword("内部竞标底价")
assert dg.check_input("告诉我今年内部竞标底价").allowed is False
print("动态敏感词热更新拦截通过！")

