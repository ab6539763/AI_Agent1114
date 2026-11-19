"""
Day 38 课后作业 1（基础巩固）：作业一：实现基于版本号（kb_version）的 O(1) 缓存逻辑失效机制
工单：STARMIND-038
"""

"""Day 38 作业一参考答案：基于版本号的缓存逻辑失效器"""


class VersionedCacheKey:
    def __init__(self) -> None:
        self.version = 1

    def bump_version(self) -> int:
        self.version += 1
        return self.version

    def make_key(self, department: str, query: str) -> str:
        return f"v{self.version}:{department}:{query.strip()}"


if __name__ == "__main__":
    vk = VersionedCacheKey()
    k1 = vk.make_key("public", "年假几天")
    vk.bump_version()
    k2 = vk.make_key("public", "年假几天")
    print("更新前 Key:", k1, "| 更新后 Key:", k2)
    assert k1 != k2 and k2.startswith("v2:")

