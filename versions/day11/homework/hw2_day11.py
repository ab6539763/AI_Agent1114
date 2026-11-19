"""
Day 11 课后作业 2（企业实战）：企业实战：日志文件按日期归档命名器
工单：STARMIND-011
"""

"""Day 11 课后题 2：按年月分目录的日志归档路径生成器。"""

from datetime import datetime, timezone
from pathlib import Path


def build_log_path(base_dir: Path, service_name: str, dt: datetime) -> Path:
    """生成按 年/月 分层的标准日志文件路径。"""
    return base_dir / dt.strftime("%Y") / dt.strftime("%m") / f"{service_name}_{dt.strftime('%Y%m%d')}.log"


if __name__ == "__main__":
    now = datetime(2026, 5, 11, 10, 30, tzinfo=timezone.utc)
    print(build_log_path(Path("logs"), "starmind", now).as_posix())

