"""
STARMIND-001 模块一：开发环境健康自检工具。
检查 Python 运行时版本、操作系统信息，并输出推荐的国内 pip 镜像配置命令。
"""

import platform
import sys
from typing import Dict, Any

# 定义星辰智脑项目要求的最低 Python 主次版本
MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 10
TSINGHUA_PYPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"


def check_environment() -> Dict[str, Any]:
    """收集当前开发环境信息并判断是否满足项目基线要求。"""
    # 获取当前 Python 解释器的主版本、次版本、微版本号
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    # 判断是否达到 Python 3.10 及以上版本
    is_compatible = (version_info.major, version_info.minor) >= (
        MIN_PYTHON_MAJOR,
        MIN_PYTHON_MINOR,
    )

    # 组装结构化的诊断结果字典
    report: Dict[str, Any] = {
        "python_version": version_str,
        "os_name": platform.system(),
        "os_release": platform.release(),
        "is_compatible": is_compatible,
        "recommended_mirror": TSINGHUA_PYPI_MIRROR,
        "pip_config_cmd": f"pip config set global.index-url {TSINGHUA_PYPI_MIRROR}",
    }
    return report


def format_env_report(report: Dict[str, Any]) -> str:
    """将环境诊断结果格式化为易读的终端输出文本。"""
    status_badge = "[PASS] 满足星辰智脑运行要求" if report["is_compatible"] else "[WARN] 请升级至 Python 3.10+"
    lines = [
        "=== 星辰智脑 StarMind 开发环境自检报告 ===",
        f"Python 版本 : {report['python_version']}  {status_badge}",
        f"操作系统    : {report['os_name']} ({report['os_release']})",
        f"推荐镜像源  : {report['recommended_mirror']}",
        f"一键配置命令: {report['pip_config_cmd']}",
        "============================================",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # 执行环境自检并打印报告
    env_report = check_environment()
    print(format_env_report(env_report))

