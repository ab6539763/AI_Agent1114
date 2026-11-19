"""
Day 68 课后作业 3（架构进阶）：架构进阶：评估系统设计的单点故障（SPOF）风险检测
工单：STARMIND-068
"""

def find_spof(replicas: dict[str, int]) -> list[str]:
    return [k for k, v in replicas.items() if v < 2]


spofs = find_spof({"nginx": 2, "api": 4, "redis": 1, "postgres": 1})
assert spofs == ["redis", "postgres"]
print("高可用 SPOF 风险项检测通过:", spofs)

