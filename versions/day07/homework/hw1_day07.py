"""
Day 07 课后作业 1（基础巩固）：基础巩固：通讯录导出 CSV 文本行
工单：STARMIND-007
"""

"""Day 7 课后题 1：通讯录导出 CSV 文本。"""

from typing import Dict, Any, List


def export_contacts_csv_text(book: Dict[str, Dict[str, Any]]) -> str:
    """将通讯录导出为标准 CSV 字符串（含表头）。"""
    lines: List[str] = ["emp_id,name,dept,masked_phone"]
    for eid in sorted(book.keys()):
        c = book[eid]
        lines.append(f"{c['emp_id']},{c['name']},{c['dept']},{c['masked_phone']}")
    return "\n".join(lines)


if __name__ == "__main__":
    sample = {
        "XM-001": {"emp_id": "XM-001", "name": "老陈", "dept": "AI研发部", "masked_phone": "138****1111"}
    }
    print(export_contacts_csv_text(sample))

