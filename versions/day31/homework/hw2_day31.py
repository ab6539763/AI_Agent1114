"""
Day 31 课后作业 2（企业实战）：作业二：实现自动化 Bad Case 诊断报告生成器
工单：STARMIND-031
"""

"""Day 31 作业二参考答案：RAG 检索 Bad Case 诊断报告生成器"""
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_text_splitter import RecursiveCharacterTextSplitter
from src.day29_vector_store import StarMindVectorStore
from src.day31_rag_ablation import BaselineCharEmbeddings, GOLDEN_EVAL_SET, load_base_corpus


def diagnose_bad_cases(store: StarMindVectorStore, top_k: int = 3) -> List[Dict[str, str]]:
    bad_cases: List[Dict[str, str]] = []
    for case in GOLDEN_EVAL_SET:
        hits = store.similarity_search_with_score(case.question, k=top_k)
        top1_doc, top1_score = hits[0] if hits else (None, 0.0)
        is_top1_ok = (
            top1_doc is not None
            and top1_doc.metadata.get("source") == case.expected_source
            and case.expected_keyword in top1_doc.page_content
        )
        if not is_top1_ok:
            bad_cases.append({
                "question": case.question,
                "expected": f"{case.expected_source} ({case.expected_keyword})",
                "actual_top1": f"{top1_doc.metadata.get('source')} (score={top1_score})" if top1_doc else "NONE",
            })
    return bad_cases


if __name__ == "__main__":
    chunks = RecursiveCharacterTextSplitter(chunk_size=140, chunk_overlap=20).split_documents(load_base_corpus())
    weak_store = StarMindVectorStore(embedding_function=BaselineCharEmbeddings(dim=64))
    weak_store.add_documents(chunks)
    bads = diagnose_bad_cases(weak_store)
    print(f"弱基线共发现 {len(bads)} 个 Top-1 Bad Case:")
    for b in bads:
        print(" ", b)

