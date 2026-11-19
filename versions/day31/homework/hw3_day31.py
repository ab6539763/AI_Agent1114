"""
Day 31 课后作业 3（架构进阶）：作业三：实现拒答阈值（score_threshold）精确率-召回率自动标定器
工单：STARMIND-031
"""

"""Day 31 作业三参考答案：防幻觉拒答阈值自动标定器"""
import sys
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day30_kb_cli import build_starmind_kb


def calibrate_threshold(
    positive_queries: List[str],
    negative_queries: List[str],
    candidates: List[float],
) -> Tuple[float, float]:
    kb = build_starmind_kb()
    pos_scores = [
        (kb.vector_store.similarity_search_with_score(q, k=1) or [(None, 0.0)])[0][1]
        for q in positive_queries
    ]
    neg_scores = [
        (kb.vector_store.similarity_search_with_score(q, k=1) or [(None, 0.0)])[0][1]
        for q in negative_queries
    ]

    best_th, best_f1 = candidates[0], -1.0
    for th in candidates:
        tp = sum(1 for s in pos_scores if s >= th)
        tn = sum(1 for s in neg_scores if s < th)
        recall = tp / max(1, len(pos_scores))
        spec = tn / max(1, len(neg_scores))
        f1 = (2 * recall * spec / (recall + spec)) if (recall + spec) > 0 else 0.0
        print(f"threshold={th:.2f} | 库内召回={recall:.2%} | 库外拒答={spec:.2%} | 综合F1={f1:.3f}")
        if f1 > best_f1:
            best_f1, best_th = f1, th
    return best_th, best_f1


if __name__ == "__main__":
    pos = ["北京出差住宿报销上限", "年假需要提前几天申请", "周五晚上可以发布代码吗"]
    neg = ["火星大气层成分", "红烧肉怎么做最好吃", "世界杯冠军是哪支球队"]
    th, f1 = calibrate_threshold(pos, neg, [0.10, 0.15, 0.20, 0.25, 0.30, 0.35])
    print(f"\n自动标定最佳拒答阈值: {th} (F1={f1:.3f})")
    assert f1 >= 0.9

