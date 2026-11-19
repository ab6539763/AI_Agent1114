import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 38 自动化单元测试：验证 Code Review 评分门禁、重构等价性、LRU 缓存失效与压测加速比。"""

from src.day38_code_review_and_perf import (
    CodeReviewScorer,
    NaiveSlowKBService,
    OptimizedFastKBService,
    build_benchmark_corpus,
)
from src.day38_load_test_runner import render_defense_report, run_benchmark


def test_code_review_scorer_grades_and_security_veto():
    scorer = CodeReviewScorer()

    s_rep = scorer.evaluate(
        "StarMind-KB-v2",
        {
            "architecture": 92,
            "retrieval_quality": 95,
            "security_reliability": 91,
            "test_coverage": 94,
            "performance": 90,
        },
    )
    assert s_rep.grade == "S"
    assert s_rep.approved is True

    # 安全分低于 70 应触发一票否决（即使总分超过 75）
    veto_rep = scorer.evaluate(
        "Unsafe-KB",
        {
            "architecture": 95,
            "retrieval_quality": 95,
            "security_reliability": 60,
            "test_coverage": 90,
            "performance": 90,
        },
    )
    assert veto_rep.approved is False
    assert len(veto_rep.blockers) == 1


def test_optimized_service_matches_naive_top1_and_uses_cache():
    corpus = build_benchmark_corpus(noise_count=120)
    slow = NaiveSlowKBService(corpus)
    fast = OptimizedFastKBService(corpus)

    test_queries = [
        "北京出差酒店住宿报销上限是多少？",
        "入职满一年年假需要提前几天OA审批？",
        "ERR-5042 网关超时排查步骤",
        "周五下午17:00能发布代码上线吗？",
    ]
    for q in test_queries:
        slow_hits = slow.search(q, department="rd", top_k=2)
        fast_hits = fast.search(q, department="rd", top_k=2)
        assert slow_hits[0][0] == fast_hits[0][0], f"重构前后 Top-1 不一致: {q}"

    # 二次查询应命中缓存
    prev_hits = fast.cache.hits
    fast.search(test_queries[0], department="rd", top_k=2)
    assert fast.cache.hits == prev_hits + 1

    # 文档变更时主动失效缓存
    fast.cache.invalidate()
    prev_misses = fast.cache.misses
    fast.search(test_queries[0], department="rd", top_k=2)
    assert fast.cache.misses == prev_misses + 1


def test_concurrent_benchmark_proves_significant_speedup():
    corpus = build_benchmark_corpus(noise_count=180)
    slow = NaiveSlowKBService(corpus)
    fast = OptimizedFastKBService(corpus)
    queries = [
        "北京出差住酒店上限是多少？",
        "ERR-5042 怎么排查？",
        "年假需要提前几天OA申请？",
    ]
    before = run_benchmark("NaiveSlow", slow, queries, concurrency=4, total_requests=36)
    after = run_benchmark("OptimizedFast", fast, queries, concurrency=4, total_requests=36)

    assert after.qps > before.qps * 2.0
    assert after.avg_ms < before.avg_ms
    assert after.cache_hit_rate > 0.5

    report = render_defense_report(before, after)
    assert "Speedup" in report

