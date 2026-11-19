"""
Day 64 课后作业 1（基础巩固）：基础巩固：编写 .env 必填生产环境变量校验器
工单：STARMIND-064
"""

def check_required_env(env_map: dict, required_keys: list[str]) -> list[str]:
    return [k for k in required_keys if not str(env_map.get(k, "")).strip()]


missing = check_required_env({"LLM_API_KEY": "sk-xxx", "JWT_SECRET": ""}, ["LLM_API_KEY", "JWT_SECRET", "DB_URL"])
assert missing == ["JWT_SECRET", "DB_URL"]
print("生产环境变量缺失检测通过:", missing)

