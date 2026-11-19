"""
Day 57 课后作业 2（企业实战）：企业实战：实现可逆 PII 脱敏映射表（发往云端前打码，返回用户前还原）
工单：STARMIND-057
"""

import re


class ReversiblePIIMasker:
    PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")

    def __init__(self) -> None:
        self.mapping: dict[str, str] = {}

    def mask(self, text: str) -> str:
        def _repl(match: re.Match[str]) -> str:
            token = f"<PHONE_{len(self.mapping) + 1}>"
            self.mapping[token] = match.group(0)
            return token
        return self.PHONE_RE.sub(_repl, text)

    def restore(self, text: str) -> str:
        for token, raw in self.mapping.items():
            text = text.replace(token, raw)
        return text


m = ReversiblePIIMasker()
masked = m.mask("联系人13800138000，备用13900139000")
print("脱敏:", masked)
print("还原:", m.restore(f"已向 {masked} 发送通知"))

