"""
STARMIND-007 模块二：星辰数科企业通讯录管理系统（含 JSON 持久化）。
综合运用 dict 主键索引、字符串清洗脱敏、list/set 标签、函数封装与 JSON 文件持久化。
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# 通讯录内存数据结构：{emp_id: {"emp_id": ..., "name": ..., "dept": ..., "phone": ..., "skills": [...]}}
ContactBook = Dict[str, Dict[str, Any]]


def load_contacts(db_path: Path) -> ContactBook:
    """从 JSON 文件加载通讯录；文件不存在时返回空字典。"""
    if not db_path.exists():
        return {}
    with db_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def save_contacts(db_path: Path, book: ContactBook) -> Path:
    """将通讯录持久化写入 UTF-8 JSON 文件。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with db_path.open("w", encoding="utf-8") as f:
        json.dump(book, f, ensure_ascii=False, indent=2)
    return db_path


def mask_phone(phone: str) -> str:
    """手机号中间四位脱敏，便于展示层安全输出。"""
    p = phone.strip()
    return f"{p[:3]}****{p[-4:]}" if len(p) == 11 and p.isdigit() else "已隐藏"


def upsert_contact(
    book: ContactBook,
    emp_id: str,
    name: str,
    dept: str,
    phone: str,
    skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """新增或更新员工联系人记录，并自动对技能标签去重排序。"""
    eid = emp_id.strip().upper()
    if not eid or not name.strip():
        raise ValueError("工号与姓名不能为空")

    clean_skills = sorted({s.strip().lower() for s in (skills or []) if s.strip()})
    record: Dict[str, Any] = {
        "emp_id": eid,
        "name": name.strip(),
        "dept": dept.strip(),
        "phone": phone.strip(),
        "masked_phone": mask_phone(phone),
        "skills": clean_skills,
    }
    book[eid] = record
    return record


def delete_contact(book: ContactBook, emp_id: str) -> bool:
    """按工号删除联系人，存在并删除返回 True，否则返回 False。"""
    eid = emp_id.strip().upper()
    return book.pop(eid, None) is not None


def search_contacts(book: ContactBook, keyword: str) -> List[Dict[str, Any]]:
    """按姓名、部门、工号或技能标签执行大小写不敏感模糊搜索。"""
    kw = keyword.strip().lower()
    if not kw:
        return sorted(book.values(), key=lambda c: c["emp_id"])

    matched: List[Dict[str, Any]] = []
    for contact in book.values():
        haystack = " ".join(
            [
                contact["emp_id"],
                contact["name"],
                contact["dept"],
                " ".join(contact.get("skills", [])),
            ]
        ).lower()
        if kw in haystack:
            matched.append(contact)
    return sorted(matched, key=lambda c: c["emp_id"])


def summarize_by_dept(book: ContactBook) -> Dict[str, int]:
    """按部门统计通讯录人数。"""
    summary: Dict[str, int] = {}
    for contact in book.values():
        dept = contact["dept"]
        summary[dept] = summary.get(dept, 0) + 1
    return summary


if __name__ == "__main__":
    book: ContactBook = {}
    upsert_contact(book, "XM-0001", "老陈", "AI研发部", "13800001111", ["Python", "架构", "LLM"])
    upsert_contact(book, "XM-0002", "林产品", "产品部", "13900002222", ["PRD", "Prompt"])
    upsert_contact(book, "XM-0003", "阿杰", "测试部", "13700003333", ["Pytest", "Python"])
    print("搜索 'python' 命中:", [c["name"] for c in search_contacts(book, "python")])
    print("部门人数统计:", summarize_by_dept(book))

