"""
Day 01 课后作业 3（架构进阶）：架构进阶：带环境变量检测的启动预检器
工单：STARMIND-001
"""

"""Day 1 课后题 3：可测试的服务启动预检器（依赖注入雏形）。"""

from typing import Dict, Tuple


def preflight_check(env_map: Dict[str, str]) -> Tuple[bool, str]:
    """检查运行环境配置是否满足星辰智脑启动条件。"""
    # 检查运行环境标识是否合法
    app_env = env_map.get("STARMIND_ENV", "dev").lower()
    valid_envs = ("dev", "staging", "prod")
    if app_env not in valid_envs:
        return False, f"非法环境标识: {app_env}，仅允许 {valid_envs}"

    # 生产环境强制要求配置 API 密钥
    if app_env == "prod" and not env_map.get("STARMIND_API_KEY"):
        return False, "生产环境缺少 STARMIND_API_KEY，拒绝启动！"

    return True, f"预检通过，当前模式: {app_env}"


if __name__ == "__main__":
    print(preflight_check({"STARMIND_ENV": "dev"}))
    print(preflight_check({"STARMIND_ENV": "prod"}))
    print(preflight_check({"STARMIND_ENV": "prod", "STARMIND_API_KEY": "sk-demo"}))

