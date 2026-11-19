"""
Day 29 - 步骤二：类 Chroma 本地持久化向量库（支持 where 元数据过滤与磁盘恢复）
对应生产包：langchain_chroma.Chroma / chromadb.PersistentClient
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_embeddings_hnsw import MiniHNSWIndex, StarMindLocalEmbeddings


def _match_where(metadata: Dict[str, Any], where: Optional[Dict[str, Any]]) -> bool:
    """
    支持类 Chroma 元数据过滤语法：
    - 精确匹配：{"dept": "财务部"}
    - 运算符匹配：{"dept": {"$in": ["财务部", "HR"]}, "year": {"$gte": 2025}}
    """
    if not where:
        return True
    for key, cond in where.items():
        val = metadata.get(key)
        if isinstance(cond, dict):
            for op, target in cond.items():
                if op == "$eq" and val != target:
                    return False
                elif op == "$ne" and val == target:
                    return False
                elif op == "$in" and val not in target:
                    return False
                elif op == "$gte" and (val is None or val < target):
                    return False
                elif op == "$lte" and (val is None or val > target):
                    return False
        else:
            if val != cond:
                return False
    return True


class StarMindVectorStore:
    """
    星辰智脑本地持久化向量数据库（Chroma 兼容风格）：
    - 支持 add_documents / similarity_search / similarity_search_with_score / delete
    - 支持 persist_directory 自动落盘与重启热加载
    """

    def __init__(
        self,
        collection_name: str = "starmind_kb",
        embedding_function: Optional[StarMindLocalEmbeddings] = None,
        persist_directory: Optional[str | Path] = None,
    ) -> None:
        self.collection_name = collection_name
        self.embedding_function = embedding_function or StarMindLocalEmbeddings()
        self.persist_directory = Path(persist_directory) if persist_directory else None

        self._docs: Dict[str, Document] = {}
        self._vectors: Dict[str, List[float]] = {}
        self._index = MiniHNSWIndex()

        if self.persist_directory and self._store_file().exists():
            self._load_from_disk()

    def _store_file(self) -> Path:
        assert self.persist_directory is not None
        return self.persist_directory / f"{self.collection_name}.json"

    def count(self) -> int:
        return len(self._docs)

    def add_documents(
        self,
        documents: Sequence[Document],
        ids: Optional[Sequence[str]] = None,
    ) -> List[str]:
        if not documents:
            return []
        doc_ids = list(ids) if ids else [f"doc_{uuid.uuid4().hex[:10]}" for _ in documents]
        vectors = self.embedding_function.embed_documents([d.page_content for d in documents])

        for doc_id, doc, vec in zip(doc_ids, documents, vectors):
            self._docs[doc_id] = doc
            self._vectors[doc_id] = vec
            self._index.add(doc_id, vec)

        if self.persist_directory:
            self.persist()
        return doc_ids

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        if not self._docs:
            return []
        q_vec = self.embedding_function.embed_query(query)
        allowed_ids = None
        if where:
            allowed_ids = {
                doc_id for doc_id, doc in self._docs.items() if _match_where(doc.metadata, where)
            }
            if not allowed_ids:
                return []

        hits = self._index.search(q_vec, top_k=k, allowed_ids=allowed_ids)
        return [(self._docs[doc_id], score) for doc_id, score in hits]

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        return [doc for doc, _ in self.similarity_search_with_score(query, k=k, where=where)]

    def persist(self) -> None:
        if not self.persist_directory:
            return
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "collection_name": self.collection_name,
            "dim": self.embedding_function.dim,
            "records": [
                {
                    "id": doc_id,
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                    "vector": self._vectors[doc_id],
                }
                for doc_id, doc in self._docs.items()
            ],
        }
        self._store_file().write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def _load_from_disk(self) -> None:
        data = json.loads(self._store_file().read_text(encoding="utf-8"))
        self._docs.clear()
        self._vectors.clear()
        self._index = MiniHNSWIndex()
        for rec in data.get("records", []):
            doc_id = rec["id"]
            doc = Document(page_content=rec["page_content"], metadata=rec["metadata"])
            vec = rec["vector"]
            self._docs[doc_id] = doc
            self._vectors[doc_id] = vec
            self._index.add(doc_id, vec)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        store = StarMindVectorStore(collection_name="starmind_v1", persist_directory=tmpdir)
        store.add_documents([
            Document("一线城市出差住宿上限600元/晚，餐补100元/天。", {"dept": "财务部", "source": "报销制度.md", "year": 2026}),
            Document("代码合并main分支必须经过GitLab评审，严禁周五晚发布。", {"dept": "研发部", "source": "发布规范.md", "year": 2026}),
            Document("入职满一年享5天带薪年假，病假需三甲医院证明。", {"dept": "HR", "source": "员工手册.pdf", "year": 2025}),
        ])

        # 模拟进程重启，重新从磁盘加载向量库
        reloaded = StarMindVectorStore(collection_name="starmind_v1", persist_directory=tmpdir)
        print("重启恢复文档数:", reloaded.count())
        print("全库检索「出差酒店」:", [(d.metadata["source"], s) for d, s in reloaded.similarity_search_with_score("出差酒店标准", k=2)])
        print("仅限研发部检索「发布」:", [(d.metadata["source"], s) for d, s in reloaded.similarity_search_with_score("周五能发布吗", k=2, where={"dept": "研发部"})])

