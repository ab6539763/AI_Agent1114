"""
Day 06 课后作业 2（企业实战）：企业实战：带关键词过滤的文档检索排序器
工单：STARMIND-006
"""

"""Day 6 课后题 2：关键词过滤与相关度排序检索器。"""

from typing import List, Dict, Any


def search_docs(
    docs: List[Dict[str, Any]], keyword: str, min_score: float = 0.5
) -> List[Dict[str, Any]]:
    """按关键词和最低分阈值过滤文档，并按相关度降序排列。"""
    kw = keyword.strip().lower()
    matched = [
        d for d in docs
        if kw in str(d.get("title", "")).lower() and float(d.get("score", 0.0)) >= min_score
    ]
    return sorted(matched, key=lambda d: d["score"], reverse=True)


if __name__ == "__main__":
    kb = [
        {"title": "Python 异步编程指南", "score": 0.92},
        {"title": "Python 安装手册", "score": 0.41},
        {"title": "FastAPI + Python 实战", "score": 0.85},
    ]
    print(search_docs(kb, "python", min_score=0.5))

