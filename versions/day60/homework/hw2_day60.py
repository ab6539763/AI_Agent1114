"""
Day 60 课后作业 2（企业实战）：企业实战：按部门权限标签（RBAC）过滤检索结果
工单：STARMIND-060
"""

def filter_chunks_by_dept(docs: list[dict], user_dept: str) -> list[dict]:
    return [d for d in docs if "ALL" in d["allowed_depts"] or user_dept in d["allowed_depts"]]


docs = [
    {"id": "D1", "allowed_depts": {"ALL"}},
    {"id": "D2", "allowed_depts": {"HR_ADMIN"}},
]
print("普通研发可见文档:", [d["id"] for d in filter_chunks_by_dept(docs, "RD")])

