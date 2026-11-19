"""
Day 29 课后作业 1（基础巩固）：作业一：实现按文档来源批量删除与增量更新（upsert）
工单：STARMIND-029
"""

"""Day 29 作业一参考答案：向量库按来源批量删除与索引重建"""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_embeddings_hnsw import MiniHNSWIndex
from src.day29_vector_store import StarMindVectorStore


class UpdatableVectorStore(StarMindVectorStore):
    def delete_by_source(self, source_name: str) -> int:
        to_delete = [
            doc_id for doc_id, doc in self._docs.items()
            if doc.metadata.get("source") == source_name
        ]
        if not to_delete:
            return 0
        for doc_id in to_delete:
            del self._docs[doc_id]
            del self._vectors[doc_id]
        # 重建 HNSW 索引保证无悬空边
        self._index = MiniHNSWIndex()
        for doc_id, vec in self._vectors.items():
            self._index.add(doc_id, vec)
        self.persist()
        return len(to_delete)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmpdir:
        vs = UpdatableVectorStore(persist_directory=tmpdir)
        vs.add_documents([
            Document("旧版年假3天", {"source": "hr_v1.pdf"}),
            Document("报销600元", {"source": "fin.md"}),
        ])
        deleted = vs.delete_by_source("hr_v1.pdf")
        print(f"删除 {deleted} 条，剩余 {vs.count()} 条")
        assert deleted == 1 and vs.count() == 1

