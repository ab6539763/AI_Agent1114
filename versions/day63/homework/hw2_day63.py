"""
Day 63 课后作业 2（企业实战）：企业实战：给语义缓存增加敏感词/个人查询旁路（禁止缓存私人数据）
工单：STARMIND-063
"""

PRIVATE_HINTS = ("我的", "工资", "绩效", "报销单号", "身份证")


def is_cacheable_query(query: str) -> bool:
    return not any(h in query for h in PRIVATE_HINTS)


assert is_cacheable_query("差旅住宿标准是多少？") is True
assert is_cacheable_query("查一下我的报销单号进度") is False
print("隐私查询缓存旁路校验通过")

