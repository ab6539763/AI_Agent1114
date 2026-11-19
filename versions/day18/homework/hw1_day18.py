"""
Day 18 课后作业 1（基础巩固）：敏感信息输出脱敏过滤器（Output PII Redactor）
工单：STARMIND-018
"""

import re


def redact_pii(text: str) -> str:
    """对大模型输出文本中的手机号和身份证号执行合规脱敏。"""
    text = re.sub(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)", r"\1****\2", text)
    text = re.sub(r"(?<!\d)(\d{6})\d{8}(\d{3}[\dXx])(?!\d)", r"\1********\2", text)
    return text


if __name__ == "__main__":
    sample = "客户联系电话 13987654321，身份证 33010619950101123X，请核实。"
    print(redact_pii(sample))

