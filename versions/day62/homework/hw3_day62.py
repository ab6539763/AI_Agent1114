"""
Day 62 课后作业 3（架构进阶）：架构进阶：实现接口级 CORS 白名单校验器
工单：STARMIND-062
"""

def is_allowed_origin(origin: str, allowlist: list[str]) -> bool:
    if "*" in allowlist:
        raise ValueError("生产环境禁止配置通配符 CORS='*'")
    return origin in allowlist


assert is_allowed_origin("https://starmind.corp.cn", ["https://starmind.corp.cn"]) is True
assert is_allowed_origin("https://evil.site", ["https://starmind.corp.cn"]) is False
print("生产 CORS 白名单安全校验通过")

