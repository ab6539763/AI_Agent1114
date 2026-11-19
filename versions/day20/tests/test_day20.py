import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 20 自动化单元测试：验证多模态客户端、余弦相似度数学精度与 FAQ 语义匹配。"""

import math
import pytest
from src.day20_multimodal_client import MultimodalClient
from src.day20_semantic_matcher import (
    FAQEntry,
    SemanticFAQMatcher,
    StarMindLocalEmbedder,
    cosine_similarity,
    l2_normalize,
)


def test_multimodal_client_vision_and_validation():
    client = MultimodalClient(max_image_bytes=1024)
    png_bytes = b"\x89PNG\r\n\x1a\nfake-image"
    res = client.analyze_image("请分析这个 502 报错截图", png_bytes, mime_type="image/png", detail="high")
    assert "502" in res.summary
    content_blocks = res.request_payload["messages"][0]["content"]
    assert content_blocks[1]["type"] == "image_url"
    assert content_blocks[1]["image_url"]["url"].startswith("data:image/png;base64,")

    # 非法 MIME 与超体积应抛 ValueError
    with pytest.raises(ValueError):
        client.encode_image_to_data_uri(png_bytes, mime_type="application/exe")
    with pytest.raises(ValueError):
        client.encode_image_to_data_uri(b"x" * 2048, mime_type="image/png")

    gen = client.generate_image("星辰智脑科技蓝架构海报", size="1024x1024")
    assert gen.size == "1024x1024"
    assert gen.mock_image_url.startswith("https://")


def test_cosine_similarity_and_l2_normalization():
    v = l2_normalize([3.0, 4.0])
    assert math.isclose(math.sqrt(sum(x * x for x in v)), 1.0, rel_tol=1e-6)
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 2.0], [1.0])


def test_semantic_faq_matcher_synonym_hit_and_rejection():
    matcher = SemanticFAQMatcher(StarMindLocalEmbedder())
    matcher.add_faqs([
        FAQEntry("FAQ-01", "差旅住宿报销标准是多少？", "一线城市 600 元/晚。", "finance"),
        FAQEntry("FAQ-02", "如何申请公司内网 VPN 权限？", "OA 提交申请。", "it"),
        FAQEntry("FAQ-03", "考勤系统如何请年假？", "OA 考勤模块提交。", "hr"),
    ])

    # 同义词口语问法（不含"差旅"和"标准"）应精准命中 FAQ-01
    hits = matcher.search("出差住酒店能报多少钱", top_k=1, min_score=0.35)
    assert len(hits) == 1
    assert hits[0].faq_id == "FAQ-01"
    assert hits[0].score > 0.7

    # 完全无关的闲聊应被阈值过滤拒答
    irrelevant = matcher.search("今天西湖边的桂花开了吗", top_k=3, min_score=0.5)
    assert irrelevant == []

