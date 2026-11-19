"""
Day 38 - 步骤一：GitLab Code Review 量化评分器 & 性能瓶颈重构实战
对比：
- NaiveSlowKBService：全表扫描 BM25 + 无查询缓存 + 粗粒度全局锁（典型初版瓶颈）
- OptimizedFastKBService：倒排索引剪枝 + 线程安全 TTL LRU 缓存 + 无锁只读路径（重构版）
"""

from __future__ import annotations

import math
import re
import threading
import time
from collections import Counter, OrderedDict, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass
class ReviewScoreReport:
    project_name: str
    weighted_score: float
    grade: str
    approved: bool
    blockers: List[str]


class CodeReviewScorer:
    """星辰数科 GitLab Merge Request 五维量化评分器。"""

    WEIGHTS: Dict[str, float] = {
        "architecture": 0.20,
        "retrieval_quality": 0.25,
        "security_reliability": 0.20,
        "test_coverage": 0.15,
        "performance": 0.20,
    }

    def evaluate(self, project_name: str, scores: Dict[str, float]) -> ReviewScoreReport:
        total = 0.0
        blockers: List[str] = []
        for dim, weight in self.WEIGHTS.items():
            val = float(scores.get(dim, 0.0))
            if not (0.0 <= val <= 100.0):
                raise ValueError(f"维度 {dim} 分数必须在 0~100 之间")
            total += val * weight
            if dim == "security_reliability" and val < 70.0:
                blockers.append(f"安全与可靠性得分 {val} < 70（一票否决项，需修复ACL/XSS隐患）")
            elif val < 60.0:
                blockers.append(f"维度 {dim} 不及格 ({val} < 60)")

        weighted = round(total, 2)
        if weighted >= 90.0:
            grade = "S"
        elif weighted >= 80.0:
            grade = "A"
        elif weighted >= 70.0:
            grade = "B"
        else:
            grade = "C"

        approved = (weighted >= 75.0) and (len(blockers) == 0)
        return ReviewScoreReport(
            project_name=project_name,
            weighted_score=weighted,
            grade=grade,
            approved=approved,
            blockers=blockers,
        )


def tokenize(text: str) -> List[str]:
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", lowered)
    for chunk in re.findall(r"[\u4e00-\u9fff]+", lowered):
        for i in range(len(chunk) - 1):
            tokens.append(chunk[i : i + 2])
    return tokens


@dataclass(frozen=True)
class ChunkDoc:
    chunk_id: str
    content: str
    department: str = "public"


class TTLLRUCache:
    """线程安全的 TTL LRU 缓存，支持文档变更时 O(1) 清空失效。"""

    def __init__(self, max_size: int = 256, ttl_seconds: float = 300.0) -> None:
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._store: OrderedDict[str, Tuple[float, List[Tuple[str, float]]]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[List[Tuple[str, float]]]:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.misses += 1
                return None
            ts, value = entry
            if now - ts > self.ttl_seconds:
                self._store.pop(key, None)
                self.misses += 1
                return None
            self._store.move_to_end(key)
            self.hits += 1
            return value

    def put(self, key: str, value: List[Tuple[str, float]]) -> None:
        now = time.monotonic()
        with self._lock:
            self._store[key] = (now, value)
            self._store.move_to_end(key)
            while len(self._store) > self.max_size:
                self._store.popitem(last=False)

    def invalidate(self) -> None:
        with self._lock:
            self._store.clear()

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total > 0 else 0.0


class NaiveSlowKBService:
    """
    初版存在三大经典性能瓶颈的检索服务：
    1. 每次查询现场重新分词统计全库文档（重复计算）；
    2. 全表扫描所有切片计算 BM25（无倒排索引剪枝）；
    3. 整个检索过程被一把粗粒度全局互斥锁串行化（高并发锁竞争）。
    """

    def __init__(self, docs: Sequence[ChunkDoc]) -> None:
        self.docs = list(docs)
        self._global_lock = threading.Lock()

    def search(self, query: str, department: str = "public", top_k: int = 3) -> List[Tuple[str, float]]:
        with self._global_lock:
            allowed = {"public", department}
            q_tokens = tokenize(query)
            pool = [d for d in self.docs if d.department in allowed]
            if not pool or not q_tokens:
                return []

            # 瓶颈：每次请求都全库重新分词与计算 DF
            tfs = [Counter(tokenize(d.content)) for d in pool]
            lengths = [sum(tf.values()) for tf in tfs]
            avgdl = sum(lengths) / max(1, len(pool))
            df: Counter[str] = Counter()
            for tf in tfs:
                for t in tf.keys():
                    df[t] += 1

            n = len(pool)
            scored: List[Tuple[str, float]] = []
            for d, tf, dl in zip(pool, tfs, lengths):
                s = 0.0
                for t in q_tokens:
                    freq = tf.get(t, 0)
                    if freq == 0:
                        continue
                    idf = math.log(1.0 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    s += idf * (freq * 2.5) / (freq + 1.5 * (0.25 + 0.75 * dl / max(1e-9, avgdl)))
                if s > 0:
                    scored.append((d.chunk_id, round(s, 4)))

            scored.sort(key=lambda x: (-x[1], x[0]))
            return scored[:top_k]


class OptimizedFastKBService:
    """
    重构优化版高性能检索服务：
    1. 入库阶段预计算分词、词频、文档长度与倒排表（Posting Lists）；
    2. 查询时仅遍历倒排表命中的候选文档（倒排剪枝），跳过 90%+ 无关切片；
    3. 引入线程安全 TTL LRU 缓存，高频问题 O(1) 返回；
    4. 只读索引彻底无锁，释放多线程并发吞吐。
    """

    def __init__(self, docs: Sequence[ChunkDoc], cache_size: int = 256, ttl_seconds: float = 300.0) -> None:
        self.docs: Dict[str, ChunkDoc] = {}
        self.doc_lengths: Dict[str, int] = {}
        self.postings: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.df: Dict[str, int] = {}
        self.avgdl: float = 0.0
        self.cache = TTLLRUCache(max_size=cache_size, ttl_seconds=ttl_seconds)
        self._build_index(docs)

    def _build_index(self, docs: Sequence[ChunkDoc]) -> None:
        total_len = 0
        for d in docs:
            self.docs[d.chunk_id] = d
            tf = Counter(tokenize(d.content))
            dl = sum(tf.values())
            self.doc_lengths[d.chunk_id] = dl
            total_len += dl
            for term, freq in tf.items():
                self.postings[term].append((d.chunk_id, freq))
        self.avgdl = total_len / max(1, len(self.docs))
        self.df = {term: len(plist) for term, plist in self.postings.items()}

    def search(self, query: str, department: str = "public", top_k: int = 3) -> List[Tuple[str, float]]:
        cache_key = f"{department}:{top_k}:{query}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        allowed = {"public", department}
        q_tokens = tokenize(query)
        if not q_tokens or not self.docs:
            return []

        n = len(self.docs)
        scores: Dict[str, float] = defaultdict(float)

        # 倒排索引剪枝：只触碰包含查询词元的候选文档
        for t in q_tokens:
            plist = self.postings.get(t)
            if not plist:
                continue
            df_t = self.df[t]
            idf = math.log(1.0 + (n - df_t + 0.5) / (df_t + 0.5))
            for cid, freq in plist:
                if self.docs[cid].department not in allowed:
                    continue
                dl = self.doc_lengths[cid]
                scores[cid] += idf * (freq * 2.5) / (freq + 1.5 * (0.25 + 0.75 * dl / max(1e-9, self.avgdl)))

        ranked = sorted(((cid, round(sc, 4)) for cid, sc in scores.items()), key=lambda x: (-x[1], x[0]))
        result = ranked[:top_k]
        self.cache.put(cache_key, result)
        return result


def build_benchmark_corpus(noise_count: int = 240) -> List[ChunkDoc]:
    """构造 240+ 切片的企业知识库压测语料（含核心制度 + 大量行政/业务背景切片）。"""
    core = [
        ChunkDoc("fin-hotel", "一线城市（北京、上海、深圳、广州）出差酒店住宿报销上限每晚600元，需提前3天OA申请。", "public"),
        ChunkDoc("hr-leave", "入职满1年员工享有5天带薪年假，年假需提前3个工作日提交OA审批；病假超2天须医院证明。", "public"),
        ChunkDoc("ops-5042", "错误码ERR-5042表示统一网关调用上游推理服务超时（默认15秒），请检查显存并调大超时。", "rd"),
        ChunkDoc("dev-win", "生产环境日常发布窗口为周一至周四10:00-18:00，严禁周五17:00之后非紧急变更上线。", "public"),
    ]
    noise = [
        ChunkDoc(
            f"bg-{i:03d}",
            f"杭州星辰数科园区日常运营公告第{i}号：食堂餐饮供应、班车发车时刻表、会议室预约与绿植维护通知。",
            "public",
        )
        for i in range(noise_count)
    ]
    return core + noise


if __name__ == "__main__":
    scorer = CodeReviewScorer()
    rep = scorer.evaluate(
        "StarMind-KB v2.0",
        {
            "architecture": 92,
            "retrieval_quality": 94,
            "security_reliability": 90,
            "test_coverage": 95,
            "performance": 93,
        },
    )
    print("Code Review 评审结论:", rep)

