"""
Day 52 课后作业 1（基础巩固）：基础巩固：为清洗管道增加身份证号与银行卡号脱敏规则
工单：STARMIND-052
"""

import re
from src.day52_dataset_cleaner import mask_pii

ID_CARD_RE = re.compile(
    r"(?<!\d)[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[0-9Xx](?!\d)"
)


def mask_pii_extended(text: str) -> str:
    text, _ = mask_pii(text)
    return ID_CARD_RE.sub("<ID_CARD_MASKED>", text)


assert "<ID_CARD_MASKED>" in mask_pii_extended("客户证件号33010619950512123X，手机13800138000")
print("身份证与手机号联合脱敏通过！")

