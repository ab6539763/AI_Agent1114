"""
STARMIND-011 模块一：预编译正则实体抽取与关键词频次统计器。
演示 re.compile、re.findall、大小写不敏感匹配与边界词频统计。
"""

import re
from typing import Dict, List, Any

# 预编译高频业务正则表达式，批量扫描时避免重复编译开销
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
TICKET_PATTERN = re.compile(r"STARMIND-\d{3,4}", re.IGNORECASE)


def extract_entities(text: str) -> Dict[str, List[str]]:
    """从文档正文中抽取去重排序后的邮箱地址与星辰工单号。"""
    emails = sorted(set(EMAIL_PATTERN.findall(text)))
    # 工单号统一标准化为大写
    tickets = sorted({t.upper() for t in TICKET_PATTERN.findall(text)})
    return {"emails": emails, "tickets": tickets}


def count_keywords(text: str, keywords: List[str]) -> Dict[str, int]:
    """统计指定关键词列表在文本中出现的总次数（大小写不敏感）。"""
    lowered = text.lower()
    counts: Dict[str, int] = {}
    for kw in keywords:
        clean_kw = kw.strip()
        if not clean_kw:
            continue
        counts[clean_kw] = lowered.count(clean_kw.lower())
    return counts


def analyze_document_text(name: str, text: str, keywords: List[str]) -> Dict[str, Any]:
    """汇总单篇文档的字数、行数、实体及关键词命中明细。"""
    entities = extract_entities(text)
    kw_counts = count_keywords(text, keywords)
    return {
        "file_name": name,
        "char_count": len(text),
        "line_count": len(text.splitlines()),
        "emails": entities["emails"],
        "tickets": entities["tickets"],
        "keyword_counts": kw_counts,
        "total_keyword_hits": sum(kw_counts.values()),
    }


if __name__ == "__main__":
    sample = "需求 STARMIND-011 由 lin@starmind.cn 提出，关联 starmind-005，重点关注 RAG 与 Python 性能优化。"
    print(analyze_document_text("demo.md", sample, ["RAG", "Python", "Agent"]))

