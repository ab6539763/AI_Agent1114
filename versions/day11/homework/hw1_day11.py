"""
Day 11 课后作业 1（基础巩固）：基础巩固：正则表达式批量脱敏手机号
工单：STARMIND-011
"""

"""Day 11 课后题 1：正则捕获组批量脱敏文本中的手机号。"""

import re

PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)")


def mask_phones_in_text(text: str) -> str:
    """将文本中所有独立的 11 位手机号替换为中间四位掩码。"""
    return PHONE_RE.sub(r"\1****\2", text)


if __name__ == "__main__":
    raw = "客户手机 13857108899，备用 18612345678，订单号 13857108899001 不应误伤。"
    print(mask_phones_in_text(raw))

