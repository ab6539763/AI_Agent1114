"""
Day 13 课后作业 2（企业实战）：企业实战：基于 yield 的流式错误日志过滤生成器
工单：STARMIND-013
"""

"""Day 13 课后题 2：低内存流式错误日志过滤生成器。"""

from typing import Generator, Iterable


def iter_error_lines(
    lines: Iterable[str],
    level: str = "ERROR",
) -> Generator[str, None, None]:
    """惰性过滤包含指定日志级别的日志行，适合处理 GB 级大日志文件。"""
    tag = f"[{level.upper()}]"
    for line in lines:
        if tag in line:
            yield line.strip()


if __name__ == "__main__":
    sample_logs = [
        "2026-05-13 10:00:01 [INFO] 服务启动完成\n",
        "2026-05-13 10:00:05 [ERROR] 模型接口返回 429 限流\n",
        "2026-05-13 10:00:08 [WARN] 响应延迟偏高\n",
        "2026-05-13 10:00:12 [ERROR] 数据库连接超时\n",
    ]
    for err in iter_error_lines(sample_logs):
        print("捕获告警:", err)

