import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 29 自动化单元测试：验证 Embedding、HNSW 索引、元数据过滤与磁盘持久化。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document
from src.day29_embeddings_hnsw import StarMindLocalEmbeddings, cosine_similarity
from src.day29_vector_store import StarMindVectorStore


def test_embedding_normalization_and_semantics():
    emb = StarMindLocalEmbeddings(dim=256)
    v_query = emb.embed_query("出差住酒店报销多少钱")
    v_rel = emb.embed_query("一线城市差旅住宿标准每晚600元")
    v_irrel = emb.embed_query("研发周五禁止上线发布代码")

    # 校验 L2 归一化长度接近 1.0
    assert abs(cosine_similarity(v_query, v_query) - 1.0) < 1e-6
    assert cosine_similarity(v_query, v_rel) > cosine_similarity(v_query, v_irrel)


def test_vector_store_persist_and_where_filter(tmp_path):
    store = StarMindVectorStore(collection_name="unit_kb", persist_directory=tmp_path)
    store.add_documents([
        Document("财务报销：住宿标准一线600元，新一线480元。", {"dept": "财务部", "year": 2026}),
        Document("研发规范：GitLab MR 需两人审批通过。", {"dept": "研发部", "year": 2026}),
        Document("旧版规定：2023年差旅报销标准为400元。", {"dept": "财务部", "year": 2023}),
    ])

    # 重启加载验证
    reloaded = StarMindVectorStore(collection_name="unit_kb", persist_directory=tmp_path)
    assert reloaded.count() == 3

    # 复合元数据过滤：只要财务部且年份 >= 2025
    hits = reloaded.similarity_search_with_score(
        "差旅住宿标准", k=3, where={"dept": "财务部", "year": {"$gte": 2025}}
    )
    assert len(hits) == 1
    assert hits[0][0].metadata["year"] == 2026
    assert "600元" in hits[0][0].page_content

