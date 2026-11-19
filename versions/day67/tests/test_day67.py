import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 67 单元测试：手撕 Attention/Top-P 与令牌桶/TTL-LRU"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day67_handwritten_transformer import scaled_dot_product_attention, stable_softmax, top_p_filter
from src.day67_engineering_interview import TTLLRUCache, TokenBucketLimiter


def test_stable_softmax_handles_large_logits():
    probs = stable_softmax([1000.0, 1001.0, 1000.0])
    assert math.isclose(sum(probs), 1.0, rel_tol=1e-6)
    assert probs[1] > probs[0]


def test_causal_attention_blocks_future_tokens():
    Q = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    out, w = scaled_dot_product_attention(Q, Q, Q, causal_mask=True)
    assert w[0][1] == 0.0 and w[0][2] == 0.0
    assert w[1][2] == 0.0
    for row in w:
        assert math.isclose(sum(row), 1.0, rel_tol=1e-6)
    assert len(out) == 3


def test_top_p_truncates_tail_and_renormalizes():
    filtered = top_p_filter({"A": 4.0, "B": 1.0, "C": -5.0}, top_p=0.95)
    assert "A" in filtered and "C" not in filtered
    assert math.isclose(sum(filtered.values()), 1.0, rel_tol=1e-5)
    assert top_p_filter({"A": 1.0, "B": 2.0}, temperature=0.0) == {"B": 1.0}


def test_token_bucket_and_ttl_lru_cache():
    now = [100.0]
    tb = TokenBucketLimiter(capacity=2, refill_rate=0.5, clock_fn=lambda: now[0])
    assert tb.allow() is True and tb.allow() is True and tb.allow() is False
    now[0] += 2.0
    assert tb.allow() is True

    cache = TTLLRUCache(maxsize=2, ttl_seconds=5.0, clock_fn=lambda: now[0])
    cache.set("a", 1)
    cache.set("b", 2)
    assert cache.get("a") == 1
    cache.set("c", 3)
    assert cache.get("b") is None and cache.get("c") == 3
    now[0] += 6.0
    assert cache.get("a") is None and cache.get("c") is None

