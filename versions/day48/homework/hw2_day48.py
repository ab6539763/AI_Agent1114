"""
Day 48 课后作业 2（企业实战）：为邮件工具增加外部域名告警检测
工单：STARMIND-048
"""

"""Day 48 作业 2 参考答案：企业外发邮件外部域名检测器。"""


def is_external_email(email: str, internal_domain: str = "starmind.cn") -> bool:
    domain = email.strip().lower().split("@")[-1]
    return domain != internal_domain.lower()


if __name__ == "__main__":
    assert is_external_email("chen@starmind.cn") is False
    assert is_external_email("ceo@partner.com") is True
    print("外部域名检测通过")

