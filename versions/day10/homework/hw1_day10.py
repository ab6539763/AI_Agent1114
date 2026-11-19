"""
Day 10 课后作业 1（基础巩固）：基础巩固：安全数值解析器
工单：STARMIND-010
"""

"""Day 10 课后题 1：精准异常捕获的安全整数解析器。"""


def safe_parse_int(value: object, default: int = 0) -> int:
    """将任意输入安全解析为整数，失败时返回 default。"""
    try:
        return int(value)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


if __name__ == "__main__":
    for sample in ["42", "3.14", "abc", None]:
        print(f"{sample!r:8s} -> {safe_parse_int(sample, default=-1)}")

