"""
Day 36 课后作业 2（企业实战）：作业二：实现基于文档内容 SHA-256 的重复上传短路跳过（Deduplication）
工单：STARMIND-036
"""

"""Day 36 作业二参考答案：SHA-256 文档入库幂等去重器"""
import hashlib
from typing import Dict


def should_skip_ingest(doc_hashes: Dict[str, str], doc_id: str, content: str) -> bool:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if doc_hashes.get(doc_id) == digest:
        return True
    doc_hashes[doc_id] = digest
    return False


if __name__ == "__main__":
    hashes: Dict[str, str] = {}
    assert should_skip_ingest(hashes, "d1", "版本1内容") is False
    assert should_skip_ingest(hashes, "d1", "版本1内容") is True   # 内容未变，短路跳过
    assert should_skip_ingest(hashes, "d1", "版本2内容") is False  # 内容更新，触发重建
    print("SHA-256 增量去重验证通过!")

