"""
企业级安全护栏（Enterprise Guardrails）模块。

覆盖国内政企落地最核心的三道防线：
1. 提示词注入防御（Prompt Injection Detection）：
   拦截“忽略以上所有指令”“输出你的系统提示词”“DAN 越狱”等中英文攻击模式。
2. 个人敏感信息自动脱敏（PII Masking）：
   基于高精度正则识别并脱敏中国大陆 11 位手机号、18 位居民身份证号、
   16~19 位银行卡号以及企业/个人电子邮箱，防止机密泄露给外部大模型或写入明文日志。
3. 涉政/暴恐/违法违规内容审核拦截（Compliance Filter）：
   命中高危违规关键词时触发 `GuardrailBlockedError` 熔断保护。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern, Tuple

from starmind_platform.app.core.exceptions import GuardrailBlockedError


@dataclass
class GuardrailResult:
    """安全护栏检测与脱敏处理结果。"""

    allowed: bool
    sanitized_text: str
    original_text: str
    blocked_reason: str = ""
    risk_category: str = "safe"
    masked_entities: Dict[str, int] = field(default_factory=dict)


class EnterpriseGuardrails:
    """星辰智脑企业级输入/输出安全护栏引擎。"""

    # 1. 提示词注入攻击特征正则（中英文混合）
    PROMPT_INJECTION_PATTERNS: List[Tuple[str, Pattern[str]]] = [
        ("忽略系统指令", re.compile(r"忽略(以上|前面|之前|所有|全部)(的)?(系统)?(指令|规则|提示|要求)", re.I)),
        ("套取系统提示词", re.compile(r"(输出|打印|泄露|告诉我|展示)(你的)?(系统提示词|system\s*prompt|初始指令)", re.I)),
        ("英文指令覆盖", re.compile(r"ignore\s+(all\s+)?(previous|above)\s+(instructions|prompts|rules)", re.I)),
        ("越狱角色扮演", re.compile(r"(进入\s*DAN\s*模式|do\s+anything\s+now|jailbreak|解除一切安全限制)", re.I)),
        ("越权命令执行", re.compile(r"(执行\s*rm\s*-rf|读取\s*/etc/passwd|DROP\s+TABLE\s+)", re.I)),
    ]

    # 2. 涉政/暴恐/违法违规高危敏感词（演示用安全合规拦截词库，生产可对接内容安全 API）
    FORBIDDEN_CONTENT_PATTERNS: List[Tuple[str, Pattern[str]]] = [
        ("违法违禁制爆", re.compile(r"(制作炸药|制造炸弹|合成剧毒|制毒教程)", re.I)),
        ("网络黑产攻击", re.compile(r"(编写勒索病毒|DDoS\s*攻击工具|窃取他人银行卡密码)", re.I)),
        ("涉政敏感违规", re.compile(r"(颠覆国家政权|煽动分裂国家|暴恐袭击教程)", re.I)),
    ]

    # 3. 个人敏感信息（PII）正则：按“身份证 -> 银行卡 -> 手机号 -> 邮箱”顺序匹配，避免号段冲突
    ID_CARD_RE = re.compile(r"(?<!\d)([1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx])(?!\d)")
    BANK_CARD_RE = re.compile(r"(?<!\d)([3-6]\d{15,18})(?!\d)")
    PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")
    EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")

    def __init__(self, enable_pii_masking: bool = True, strict_mode: bool = True) -> None:
        self.enable_pii_masking = enable_pii_masking
        self.strict_mode = strict_mode

    def mask_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        对文本中的敏感个人信息进行脱敏替换，并返回脱敏后文本及各类型命中次数。
        - 身份证号：保留前 6 位与后 4 位 -> `330106********1234`
        - 银行卡号：保留前 4 位与后 4 位 -> `6222********8899`
        - 手机号：保留前 3 位与后 4 位 -> `138****5678`
        - 邮箱：保留首字符与域名 -> `z***@starmind.cn`
        """
        counts: Dict[str, int] = {}
        sanitized = text

        def _mask_id(match: re.Match[str]) -> str:
            val = match.group(1)
            counts["id_card"] = counts.get("id_card", 0) + 1
            return f"{val[:6]}********{val[-4:]}"

        def _mask_bank(match: re.Match[str]) -> str:
            val = match.group(1)
            counts["bank_card"] = counts.get("bank_card", 0) + 1
            return f"{val[:4]}{'*' * (len(val) - 8)}{val[-4:]}"

        def _mask_phone(match: re.Match[str]) -> str:
            val = match.group(1)
            counts["phone"] = counts.get("phone", 0) + 1
            return f"{val[:3]}****{val[-4:]}"

        def _mask_email(match: re.Match[str]) -> str:
            val = match.group(1)
            counts["email"] = counts.get("email", 0) + 1
            user, domain = val.split("@", 1)
            prefix = user[0] if user else "*"
            return f"{prefix}***@{domain}"

        sanitized = self.ID_CARD_RE.sub(_mask_id, sanitized)
        sanitized = self.BANK_CARD_RE.sub(_mask_bank, sanitized)
        sanitized = self.PHONE_RE.sub(_mask_phone, sanitized)
        sanitized = self.EMAIL_RE.sub(_mask_email, sanitized)
        return sanitized, counts

    def check_input(self, text: str, *, raise_on_block: bool = True) -> GuardrailResult:
        """
        执行输入侧全量安全审查：
        1. 提示词注入检测；
        2. 涉政/违法违规内容审核；
        3. 个人敏感信息自动脱敏。
        """
        if not text:
            return GuardrailResult(allowed=True, sanitized_text="", original_text="")

        for label, pattern in self.PROMPT_INJECTION_PATTERNS:
            if pattern.search(text):
                reason = f"触发提示词注入安全拦截规则：{label}"
                result = GuardrailResult(
                    allowed=False,
                    sanitized_text="",
                    original_text=text,
                    blocked_reason=reason,
                    risk_category="prompt_injection",
                )
                if raise_on_block:
                    raise GuardrailBlockedError(reason, details={"risk_category": "prompt_injection", "rule": label})
                return result

        for label, pattern in self.FORBIDDEN_CONTENT_PATTERNS:
            if pattern.search(text):
                reason = f"触发企业内容合规拦截规则：{label}"
                result = GuardrailResult(
                    allowed=False,
                    sanitized_text="",
                    original_text=text,
                    blocked_reason=reason,
                    risk_category="compliance_violation",
                )
                if raise_on_block:
                    raise GuardrailBlockedError(
                        reason, details={"risk_category": "compliance_violation", "rule": label}
                    )
                return result

        sanitized = text
        masked_entities: Dict[str, int] = {}
        if self.enable_pii_masking:
            sanitized, masked_entities = self.mask_pii(text)

        return GuardrailResult(
            allowed=True,
            sanitized_text=sanitized,
            original_text=text,
            risk_category="safe",
            masked_entities=masked_entities,
        )

    def sanitize_output(self, text: str) -> str:
        """对模型输出做二次 PII 脱敏兜底，防止上下文意外回显明文敏感信息。"""
        if not self.enable_pii_masking or not text:
            return text
        sanitized, _ = self.mask_pii(text)
        return sanitized
