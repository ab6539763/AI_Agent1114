"""
Day 07 课后作业 2（企业实战）：企业实战：批量导入通讯录冲突检测器
工单：STARMIND-007
"""

"""Day 7 课后题 2：批量导入通讯录工号冲突检测。"""

from typing import Dict, Any, List, Tuple


def detect_import_conflicts(
    book: Dict[str, Any], incoming: List[Dict[str, Any]]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """检测批量导入中的重复工号（含库内重复与批次内重复）。"""
    conflicts: List[str] = []
    safe_items: List[Dict[str, Any]] = []
    batch_seen = set()

    for item in incoming:
        eid = str(item.get("emp_id", "")).strip().upper()
        if eid in book or eid in batch_seen:
            conflicts.append(eid)
        else:
            batch_seen.add(eid)
            safe_items.append(item)
    return conflicts, safe_items


if __name__ == "__main__":
    existing = {"XM-001": {"name": "老陈"}}
    batch = [
        {"emp_id": "XM-001", "name": "重复老陈"},
        {"emp_id": "XM-002", "name": "新人A"},
        {"emp_id": "XM-002", "name": "批次内重复新人A"},
    ]
    print(detect_import_conflicts(existing, batch))

