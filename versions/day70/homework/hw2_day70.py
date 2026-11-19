"""
Day 70 课后作业 2（企业实战）：企业实战：编写语义化版本号（SemVer）自动递增工具
工单：STARMIND-070
"""

def bump_semver(version: str, part: str = "patch") -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


assert bump_semver("1.0.0", "patch") == "1.0.1"
assert bump_semver("1.0.1", "minor") == "1.1.0"
assert bump_semver("1.1.0", "major") == "2.0.0"
print("SemVer 版本号递增通过")

