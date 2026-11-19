"""
Day 29 - 步骤一：中文稠密 Embedding 模型（离线确定性版）与轻量 HNSW 分层近邻图索引
生产对照：BAAI/bge-large-zh-v1.5 + hnswlib / Milvus HNSW
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from typing import Dict, List, Sequence, Set, Tuple


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """计算两个已归一化向量的余弦相似度（等价于点积）。"""
    return sum(a * b for a, b in zip(vec_a, vec_b))


class StarMindLocalEmbeddings:
    """
    轻量确定性中文稠密 Embedding 模型（L2 归一化）：
    - 结合中文单字/双字 N-gram、英文词干与企业同义词归一化特征哈希映射到固定维度。
    - 离线零依赖、跨平台 100% 可复现；生产环境可无缝替换为 BGE / OpenAI Embeddings。
    """

    # 企业常见同义词概念槽，模拟稠密向量的语义泛化能力
    SYNONYM_GROUPS = [
        ("报销", "差旅", "住宿", "酒店", "发票", "补贴", "餐补", "出差"),
        ("年假", "休假", "请假", "病假", "调休", "考勤", "打卡"),
        ("发布", "上线", "部署", "合并", "分支", "GitLab", "MR", "CI", "代码"),
        ("VPN", "内网", "网络", "证书", "零信任", "权限", "SSO", "密码"),
        ("加密", "保密", "安全", "脱敏", "审计", "合规", "权限"),
    ]

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _extract_features(self, text: str) -> List[Tuple[str, float]]:
        clean = re.sub(r"\s+", "", text.lower())
        features: List[Tuple[str, float]] = []

        # 1. 英文单词 / 数字词元
        for tok in re.findall(r"[a-z0-9_]+", text.lower()):
            features.append((f"en:{tok}", 2.0))

        # 2. 中文字符 1-gram 与 2-gram（核心区分度）
        zh_only = "".join(re.findall(r"[\u4e00-\u9fff]", clean))
        for ch in zh_only:
            features.append((f"c1:{ch}", 1.0))
        for i in range(len(zh_only) - 1):
            features.append((f"c2:{zh_only[i : i + 2]}", 2.5))

        # 3. 语义概念槽增强（让“住酒店”与“住宿标准”在向量空间靠近）
        for gid, group in enumerate(self.SYNONYM_GROUPS):
            hits = sum(1 for kw in group if kw.lower() in text.lower())
            if hits > 0:
                features.append((f"concept:{gid}", 2.2 * math.log1p(hits)))

        return features

    def embed_query(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        for feat, weight in self._extract_features(text):
            digest = hashlib.md5(feat.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if (digest[4] & 1) == 0 else -1.0
            vec[idx] += sign * weight

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]


class MiniHNSWIndex:
    """
    教学级 HNSW（Hierarchical Navigable Small World）分层导航小世界图索引：
    - 通过指数衰减随机分配节点层级。
    - 检索时从最高层入口点贪心下降至第 0 层，再执行广度近邻搜索返回 Top-K。
    """

    def __init__(self, max_neighbors: int = 8, ef_search: int = 24, seed: int = 42) -> None:
        self.max_neighbors = max_neighbors
        self.ef_search = ef_search
        self._rng = random.Random(seed)
        self._vectors: Dict[str, List[float]] = {}
        self._layers: List[Dict[str, List[str]]] = []  # layer -> {node_id: [neighbor_ids]}
        self._entry_point: str | None = None

    def _sample_level(self) -> int:
        level = 0
        while self._rng.random() < 0.35 and level < 4:
            level += 1
        return level

    def add(self, doc_id: str, vector: List[float]) -> None:
        self._vectors[doc_id] = vector
        level = self._sample_level()
        while len(self._layers) <= level:
            self._layers.append({})

        if self._entry_point is None:
            self._entry_point = doc_id
            for lv in range(level + 1):
                self._layers[lv][doc_id] = []
            return

        # 逐层建立双向近邻边
        for lv in range(level + 1):
            layer_graph = self._layers[lv]
            existing = list(layer_graph.keys())
            layer_graph[doc_id] = []
            if not existing:
                continue
            scored = sorted(
                ((cosine_similarity(vector, self._vectors[nid]), nid) for nid in existing),
                reverse=True,
            )
            neighbors = [nid for _, nid in scored[: self.max_neighbors]]
            layer_graph[doc_id] = neighbors
            for nid in neighbors:
                nbrs = layer_graph[nid]
                if doc_id not in nbrs:
                    nbrs.append(doc_id)
                    if len(nbrs) > self.max_neighbors:
                        nbrs.sort(key=lambda x: cosine_similarity(self._vectors[nid], self._vectors[x]), reverse=True)
                        del nbrs[self.max_neighbors :]

        if level >= len(self._layers) - 1:
            self._entry_point = doc_id

    def search(
        self,
        query_vec: List[float],
        top_k: int = 5,
        allowed_ids: Set[str] | None = None,
    ) -> List[Tuple[str, float]]:
        if not self._vectors or self._entry_point is None:
            return []

        curr = self._entry_point
        curr_sim = cosine_similarity(query_vec, self._vectors[curr])

        # 1. 从最高层贪心下降到第 1 层（高速层 -> 主干层）
        for lv in range(len(self._layers) - 1, 0, -1):
            layer_graph = self._layers[lv]
            improved = True
            while improved:
                improved = False
                for nbr in layer_graph.get(curr, []):
                    sim = cosine_similarity(query_vec, self._vectors[nbr])
                    if sim > curr_sim:
                        curr, curr_sim = nbr, sim
                        improved = True

        # 2. 在底层 Layer 0 展开候选集探索（保证高召回）
        layer0 = self._layers[0]
        visited: Set[str] = {curr}
        candidates: List[Tuple[float, str]] = [(curr_sim, curr)]
        idx = 0
        while idx < len(candidates) and len(visited) < max(self.ef_search, top_k * 4):
            _, node = candidates[idx]
            idx += 1
            for nbr in layer0.get(node, []):
                if nbr not in visited:
                    visited.add(nbr)
                    candidates.append((cosine_similarity(query_vec, self._vectors[nbr]), nbr))
            candidates.sort(reverse=True)

        # 若启用了元数据预过滤且图探索命中不足，则对 allowed_ids 精确补齐，防止后过滤空结果陷阱
        if allowed_ids is not None:
            filtered = [(nid, score) for score, nid in candidates if nid in allowed_ids]
            if len(filtered) < top_k:
                all_allowed = sorted(
                    ((cosine_similarity(query_vec, self._vectors[nid]), nid) for nid in allowed_ids if nid in self._vectors),
                    reverse=True,
                )
                return [(nid, round(score, 4)) for score, nid in all_allowed[:top_k]]
            return [(nid, round(score, 4)) for nid, score in filtered[:top_k]]

        return [(nid, round(score, 4)) for score, nid in candidates[:top_k]]


if __name__ == "__main__":
    emb = StarMindLocalEmbeddings(dim=256)
    hnsw = MiniHNSWIndex(max_neighbors=6)
    samples = {
        "d1": "一线城市出差酒店住宿报销上限为每晚600元，餐补每天100元。",
        "d2": "研发代码发布前必须通过GitLab MR代码评审且严禁周五晚发布。",
        "d3": "员工入职满1年享受5天带薪年假，请假需提前3个工作日申请。",
    }
    for doc_id, text in samples.items():
        hnsw.add(doc_id, emb.embed_query(text))

    q_vec = emb.embed_query("去上海出差住酒店能报多少钱？")
    print("HNSW Top-2 检索结果:", hnsw.search(q_vec, top_k=2))

