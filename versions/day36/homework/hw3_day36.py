"""
Day 36 课后作业 3（架构进阶）：作业三：实现多部门联合角色权限校验（RBAC 多标签过滤）
工单：STARMIND-036
"""

"""Day 36 作业三参考答案：RBAC 多角色权限交集过滤器"""
from typing import Dict, List, Sequence, Set


def filter_authorized_chunks(
    chunks: Sequence[Dict],
    user_roles: Sequence[str],
) -> List[Dict]:
    u_set: Set[str] = set(user_roles) | {"public"}
    return [ch for ch in chunks if u_set & set(ch.get("allowed_roles", ["public"]))]


if __name__ == "__main__":
    docs = [
        {"id": "c1", "allowed_roles": ["public"]},
        {"id": "c2", "allowed_roles": ["rd", "ops"]},
        {"id": "c3", "allowed_roles": ["finance", "exec"]},
    ]
    rd_only = filter_authorized_chunks(docs, ["rd"])
    vp_roles = filter_authorized_chunks(docs, ["rd", "exec"])
    print("普通研发可见:", [d["id"] for d in rd_only])
    print("技术VP可见:", [d["id"] for d in vp_roles])
    assert [d["id"] for d in rd_only] == ["c1", "c2"]
    assert [d["id"] for d in vp_roles] == ["c1", "c2", "c3"]

