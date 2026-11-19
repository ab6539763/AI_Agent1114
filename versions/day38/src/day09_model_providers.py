"""
STARMIND-009 模块二：OpenAIModel / QwenModel 多态实现与多模型路由器。
演示继承、super() 调用、方法重写、多态分发以及 __len__ / __contains__ 魔术方法。
"""

from typing import Dict, Any
from day09_base_model import BaseModel


class OpenAIModel(BaseModel):
    """OpenAI / DeepSeek 兼容协议适配器（本地离线模拟版）。"""

    provider: str = "openai"

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7, api_key: str = "mock-openai-key") -> None:
        super().__init__(model_name=model_name, temperature=temperature)
        self._api_key = api_key

    def build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _do_generate(self, prompt: str) -> str:
        return f"[OpenAI:{self.model_name}|t={self.temperature}] 已收到指令「{prompt}」，建议采用结构化分步解答。"


class QwenModel(BaseModel):
    """阿里云通义千问（DashScope）适配器（本地离线模拟版）。"""

    provider: str = "qwen"

    def __init__(self, model_name: str = "qwen-plus", temperature: float = 0.5, api_key: str = "mock-qwen-key") -> None:
        super().__init__(model_name=model_name, temperature=temperature)
        self._api_key = api_key

    def build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "X-DashScope-SSE": "disable",
            "Content-Type": "application/json",
        }

    def _do_generate(self, prompt: str) -> str:
        return f"[通义千问:{self.model_name}|t={self.temperature}] 您好！针对「{prompt}」，星辰智脑中文知识库已为您整理完毕。"


class ModelRouter:
    """多模型统一路由器：面向 BaseModel 抽象接口编程，屏蔽厂商差异。"""

    def __init__(self) -> None:
        self._registry: Dict[str, BaseModel] = {}

    def register(self, alias: str, model: BaseModel) -> None:
        if not isinstance(model, BaseModel):
            raise TypeError("注册对象必须是 BaseModel 的子类实例")
        self._registry[alias] = model

    def ask(self, alias: str, prompt: str) -> Dict[str, Any]:
        if alias not in self._registry:
            raise KeyError(f"未注册的模型别名: {alias}")
        model = self._registry[alias]
        # 多态调用：触发 BaseModel.__call__ -> 具体子类的 _do_generate
        return model(prompt)

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, alias: str) -> bool:
        return alias in self._registry


if __name__ == "__main__":
    router = ModelRouter()
    router.register("fast", OpenAIModel("gpt-4o-mini", temperature=0.3))
    router.register("cn_pro", QwenModel("qwen-plus", temperature=0.5))

    print(f"已注册模型数量: {len(router)} | 包含 cn_pro: {'cn_pro' in router}")
    for alias in ("fast", "cn_pro"):
        res = router.ask(alias, "总结一下杭州星辰数科的核心优势")
        print(f"-> {alias}: {res['reply']}")

