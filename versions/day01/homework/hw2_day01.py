"""
Day 01 课后作业 2（企业实战）：企业实战：多字段员工隐私脱敏工具
工单：STARMIND-001
"""

"""Day 1 课后题 2：企业员工邮箱与身份信息脱敏工具。"""


def mask_email(email: str) -> str:
    """对企业邮箱执行脱敏：保留前缀首字母与完整域名。"""
    cleaned = email.strip()
    if "@" not in cleaned:
        return "无效邮箱"
    local_part, domain = cleaned.split("@", 1)
    if not local_part or not domain:
        return "无效邮箱"
    # 保留用户名第一个字符，其余用 *** 掩码
    return f"{local_part[0]}***@{domain}"


if __name__ == "__main__":
    for sample in ["chenxiaoxin@starmind.cn", "a@corp.com", "invalid-mail"]:
        print(f"{sample:25s} -> {mask_email(sample)}")

