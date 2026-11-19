"""
StarMind Day 20 - 步骤二：Embedding 文本向量化、余弦相似度计算与 FAQ 相似问题语义匹配工具
纯 Python 零外部依赖实现，完美呈现语义向量检索与阈值拒答机制。
"""

import hashlib
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


def l2_normalize(vector: List[float]) -> List[float]:
    """对向量执行 L2 归一化，使其欧氏模长严格等于 1.0。"""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return [0.0 for _ in vector]
    return [x / norm for x in vector]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """计算两个等长向量的余弦相似度，返回值域 [-1.0, 1.0]。"""
    if len(vec_a) != len(vec_b):
        raise ValueError(f"向量维度不一致: {len(vec_a)} vs {len(vec_b)}")
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


class StarMindLocalEmbedder:
    """
    轻量级确定性语义嵌入模型（离线仿真 BGE / text-embedding-v3 行为）：
    - 前 16 维：企业领域语义概念投影（打通同义词鸿沟，如 住酒店 <-> 差旅住宿）
    - 后 48 维：字符 unigram + bigram 哈希投影（保留细粒度字面特征）
    总维度 = 64 维，输出自动 L2 归一化。
    """

    CONCEPT_GROUPS: List[Tuple[str, ...]] = [
        ("差旅", "出差", "酒店", "住宿", "报销", "旅费", "发票"),
        ("vpn", "内网", "远程", "连不上", "办公网", "网络权限"),
        ("请假", "年假", "病假", "调休", "考勤", "休假"),
        ("发票", "专票", "税号", "抬头", "开票", "财务"),
        ("密码", "重置", "登录", "账号", "锁定", "sso"),
        ("薪资", "工资", "发薪", "社保", "公积金", "个税"),
        ("合同", "法务", "盖章", "用印", "审批", "协议"),
        ("报障", "报错", "502", "超时", "故障", "崩溃", "bug"),
    ]

    def __init__(self, hash_dims: int = 48) -> None:
        self.concept_dims = len(self.CONCEPT_GROUPS)
        self.hash_dims = hash_dims
        self.dim = self.concept_dims + self.hash_dims

    def embed(self, text: str) -> List[float]:
        """将任意中英文文本编码为 L2 归一化的 64 维稠密语义向量。"""
        clean = text.strip().lower()
        vec = [0.0] * self.dim
        if not clean:
            return vec

        # 1. 语义概念槽加权投影（高权重，实现同义词语义对齐）
        for idx, group in enumerate(self.CONCEPT_GROUPS):
            hits = sum(1 for kw in group if kw in clean)
            if hits > 0:
                vec[idx] += 3.0 * hits

        # 2. 字符级 bigram 哈希投影（保留局部字面匹配能力）
        compact = "".join(clean.split())
        grams = [compact[i : i + 2] for i in range(max(1, len(compact) - 1))]
        for g in grams:
            digest = hashlib.md5(g.encode("utf-8")).digest()
            slot = self.concept_dims + (digest[0] % self.hash_dims)
            vec[slot] += 0.6

        return l2_normalize(vec)


@dataclass
class FAQEntry:
    faq_id: str
    question: str
    answer: str
    category: str


@dataclass
class MatchHit:
    faq_id: str
    question: str
    answer: str
    score: float


class SemanticFAQMatcher:
    """基于 Embedding + 余弦相似度的企业 FAQ 相似问题语义匹配器。"""

    def __init__(self, embedder: StarMindLocalEmbedder | None = None) -> None:
        self.embedder = embedder or StarMindLocalEmbedder()
        self._entries: List[FAQEntry] = []
        self._vectors: List[List[float]] = []

    def add_faqs(self, entries: List[FAQEntry]) -> None:
        """批量建立 FAQ 向量索引。"""
        for entry in entries:
            self._entries.append(entry)
            self._vectors.append(self.embedder.embed(entry.question))

    def search(self, query: str, top_k: int = 3, min_score: float = 0.35) -> List[MatchHit]:
        """执行 Top-K 语义检索并按 min_score 阈值过滤低相关噪声。"""
        q_vec = self.embedder.embed(query)
        scored: List[Tuple[float, FAQEntry]] = []
        for entry, doc_vec in zip(self._entries, self._vectors):
            sim = cosine_similarity(q_vec, doc_vec)
            if sim >= min_score:
                scored.append((sim, entry))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            MatchHit(
                faq_id=e.faq_id,
                question=e.question,
                answer=e.answer,
                score=round(s, 4),
            )
            for s, e in scored[:top_k]
        ]


if __name__ == "__main__":
    matcher = SemanticFAQMatcher()
    matcher.add_faqs([
        FAQEntry("FAQ-01", "杭州与一线城市差旅住宿报销标准是多少？", "北京/上海/深圳/杭州住宿上限 600 元/晚。", "finance"),
        FAQEntry("FAQ-02", "新员工如何申请公司内网 VPN 远程访问？", "请在 OA 发起 IT 权限申请，主管审批后 30 分钟开通。", "it"),
        FAQEntry("FAQ-03", "年假和病假怎么在考勤系统里提交请假？", "登录星辰 OA-考勤休假模块选择对应假别提交即可。", "hr"),
        FAQEntry("FAQ-04", "SSO 单点登录密码忘记了如何重置？", "访问门户登录页点击忘记密码并通过企业微信扫码验证。", "it"),
    ])

    for q in ["出差住酒店最多能报多少钱？", "在家连不上公司办公网怎么办？", "今晚杭州西湖附近吃什么火锅好？"]:
        hits = matcher.search(q, top_k=2, min_score=0.35)
        print(f"提问: {q}")
        if hits:
            for h in hits:
                print(f"  -> [{h.score:.4f}] {h.question} | 答: {h.answer}")
        else:
            print("  -> [低于阈值拒答] 未命中企业 FAQ，建议转人工或通用对话。")

