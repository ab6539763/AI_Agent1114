"""
StarMind Day 20 - 步骤一：多模态图像理解（Vision）与文生图（Image Generation）API 客户端封装
支持 MIME 白名单、体积限制、Base64 Data URI 构造与离线确定性推理桩。
"""

import base64
from dataclasses import dataclass
from typing import Any, Dict, List


ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_IMAGE_SIZES = {"512x512", "1024x1024", "1024x1792", "1792x1024"}


@dataclass
class VisionResult:
    """图像理解分析结果。"""
    model: str
    summary: str
    detected_tags: List[str]
    request_payload: Dict[str, Any]


@dataclass
class ImageGenResult:
    """文生图结果。"""
    model: str
    prompt: str
    size: str
    revised_prompt: str
    mock_image_url: str


class MultimodalClient:
    """星辰智脑多模态 API 统一客户端。"""

    def __init__(self, max_image_bytes: int = 5 * 1024 * 1024) -> None:
        self.max_image_bytes = max_image_bytes

    def encode_image_to_data_uri(self, image_bytes: bytes, mime_type: str = "image/png") -> str:
        """校验图片格式与大小上限，编码为标准 Base64 Data URI。"""
        if mime_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"不支持的图片 MIME 类型: {mime_type}，仅允许 {ALLOWED_MIME_TYPES}")
        if not image_bytes:
            raise ValueError("图片字节内容不能为空")
        if len(image_bytes) > self.max_image_bytes:
            raise ValueError(f"图片体积 {len(image_bytes)} 字节超出上限 {self.max_image_bytes} 字节")

        b64 = base64.b64encode(image_bytes).decode("ascii")
        return f"data:{mime_type};base64,{b64}"

    def build_vision_payload(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/png",
        detail: str = "high",
        model: str = "qwen-vl-max",
    ) -> Dict[str, Any]:
        """构造 100% 符合 OpenAI Vision 协议标准的请求 JSON 体。"""
        if detail not in {"low", "high", "auto"}:
            raise ValueError(f"非法的 detail 参数: {detail}")
        data_uri = self.encode_image_to_data_uri(image_bytes, mime_type=mime_type)
        return {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri, "detail": detail}},
                    ],
                }
            ],
        }

    def analyze_image(
        self,
        prompt: str,
        image_bytes: bytes,
        mime_type: str = "image/png",
        detail: str = "high",
        model: str = "qwen-vl-max",
    ) -> VisionResult:
        """执行多模态图像理解（离线仿真分析，返回标准结构与完整请求体）。"""
        payload = self.build_vision_payload(prompt, image_bytes, mime_type, detail, model)
        tags = ["enterprise_screenshot"]
        if "报错" in prompt or "错误" in prompt or "502" in prompt:
            tags.extend(["error_dialog", "sre_diagnostic"])
            summary = "已识别界面报错截图：检测到网关 502 Bad Gateway 提示，建议优先检查上游服务健康检查与超时配置。"
        elif "发票" in prompt:
            tags.extend(["invoice_ocr", "finance"])
            summary = "已提取电子发票关键字段：抬头为杭州星辰数科有限公司，税率 6%，状态核验正常。"
        else:
            tags.append("general_vision")
            summary = f"已完成图像理解（清晰度={detail}，大小={len(image_bytes)}B）：画面主体清晰，符合业务提交规范。"

        return VisionResult(model=model, summary=summary, detected_tags=tags, request_payload=payload)

    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "corporate_flat",
        model: str = "wanx-v2",
    ) -> ImageGenResult:
        """封装文生图 API 调用与企业提示词增强。"""
        if not prompt.strip():
            raise ValueError("文生图 prompt 不能为空")
        if size not in ALLOWED_IMAGE_SIZES:
            raise ValueError(f"不支持的图片分辨率: {size}，可选 {ALLOWED_IMAGE_SIZES}")

        revised = f"{prompt.strip()}，风格：{style}，高清无水印，企业级科技蓝配色"
        slug = abs(hash(revised)) % 100000
        return ImageGenResult(
            model=model,
            prompt=prompt,
            size=size,
            revised_prompt=revised,
            mock_image_url=f"https://assets.starmind.local/generated/{model}_{size}_{slug}.png",
        )


if __name__ == "__main__":
    client = MultimodalClient()
    fake_png = b"\x89PNG\r\n\x1a\n" + b"starmind-demo-image-payload"
    v_res = client.analyze_image("请帮我分析这张 502 报错截图的原因", fake_png, mime_type="image/png")
    print("视觉理解结果:", v_res.summary, "| 标签:", v_res.detected_tags)
    g_res = client.generate_image("星辰智脑 AI 平台发布会主视觉海报", size="1024x1024")
    print("文生图结果:", g_res.mock_image_url)

