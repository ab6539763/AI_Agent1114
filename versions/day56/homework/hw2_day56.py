"""
Day 56 课后作业 2（企业实战）：企业实战：编写 `.dockerignore` 生成器防止敏感文件泄露
工单：STARMIND-056
"""

REQUIRED_IGNORES = {".env", ".git", ".venv", "__pycache__", "*.key"}


def check_dockerignore(content: str) -> list[str]:
    lines = {line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")}
    return sorted(REQUIRED_IGNORES - lines)


print("缺失项:", check_dockerignore(".env\n.git\n.venv\n__pycache__\n*.key\n"))

