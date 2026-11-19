"""
Day 12 课后作业 2（企业实战）：企业实战：国内多厂商 OpenAI 兼容配置工厂
工单：STARMIND-012
"""

"""Day 12 课后题 2：国内多厂商 OpenAI 兼容配置工厂。"""

from typing import Dict

PROVIDER_PRESETS: Dict[str, Dict[str, str]] = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
    },
}


def create_provider_config(provider: str, api_key: str) -> Dict[str, str]:
    """根据厂商名称生成标准 OpenAI 兼容客户端配置。"""
    key = provider.strip().lower()
    if key not in PROVIDER_PRESETS:
        supported = ", ".join(sorted(PROVIDER_PRESETS))
        raise ValueError(f"不支持的厂商 '{provider}'，当前仅支持: {supported}")
    preset = PROVIDER_PRESETS[key]
    return {
        "provider": key,
        "base_url": preset["base_url"],
        "model": preset["model"],
        "api_key": api_key,
    }


if __name__ == "__main__":
    print(create_provider_config("DeepSeek", "sk-demo"))
    print(create_provider_config("qwen", "sk-demo"))

