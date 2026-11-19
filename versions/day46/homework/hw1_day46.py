"""
Day 46 课后作业 1（基础巩固）：扩展 PII 脱敏支持企业邮箱与 API Key 掩码
工单：STARMIND-046
"""

"""Day 46 作业 1 参考答案：API Key 密钥日志脱敏器。"""

import re


def redact_secrets(text: str) -> str:
    return re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-***REDACTED***", text)


if __name__ == "__main__":
    raw = "调用失败，使用密钥 sk-AbCdEf1234567890 连接超时"
    safe = redact_secrets(raw)
    print(safe)
    assert "AbCdEf1234567890" not in safe and "sk-***REDACTED***" in safe

