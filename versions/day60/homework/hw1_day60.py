"""
Day 60 课后作业 1（基础巩固）：基础巩固：为知识库增加带重叠窗口的滑动切片器
工单：STARMIND-060
"""

from src.day60_hybrid_retriever import KnowledgeChunk


def chunk_document(doc_id: str, title: str, text: str, chunk_size: int = 120, overlap: int = 20):
    step = max(1, chunk_size - overlap)
    chunks = []
    for idx, start in enumerate(range(0, len(text), step), start=1):
        piece = text[start : start + chunk_size].strip()
        if piece:
            chunks.append(KnowledgeChunk(f"{doc_id}#{idx}", title, piece))
    return chunks


res = chunk_document("DOC-99", "规章", "这是一段较长的企业制度文本。" * 15, chunk_size=50, overlap=10)
print(f"切分出 {len(res)} 个带重叠窗口切片，首片ID={res[0].doc_id}")

