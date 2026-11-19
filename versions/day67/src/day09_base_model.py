"""
STARMIND-009 模块一：大模型统一抽象基类 BaseModel。
演示 abc.ABC 抽象基类、@property 范围校验、模板方法与 __call__ / __str__ 魔术方法。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseModel(ABC):
    """星辰智脑所有大模型适配器的抽象基类。"""

    provider: str = "base"

    def __init__(self, model_name: str, temperature: float = 0.7) -> None:
        self.model_name: str = model_name
        # 通过 @temperature.setter 触发构造期范围校验
        self.temperature = temperature
        self._call_count: int = 0

    @property
    def temperature(self) -> float:
        """读取采样温度（只通过受控接口暴露私有字段 _temperature）。"""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """拦截写入：强制限制温度必须在 [0.0, 2.0] 合法区间内。"""
        val = float(value)
        if not (0.0 <= val <= 2.0):
            raise ValueError(f"temperature 必须在 [0.0, 2.0] 之间，当前传入: {val}")
        self._temperature = val

    @property
    def call_count(self) -> int:
        """只读属性：返回当前模型实例累计被调用的次数。"""
        return self._call_count

    @abstractmethod
    def build_headers(self) -> Dict[str, str]:
        """抽象方法：子类必须实现各自厂商的 HTTP 鉴权请求头。"""

    @abstractmethod
    def _do_generate(self, prompt: str) -> str:
        """抽象方法：子类实现具体的文本生成逻辑（本地模拟或真实 API）。"""

    def generate(self, prompt: str) -> Dict[str, Any]:
        """模板方法：统一完成空值检查、计数统计并委托子类生成回复。"""
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("提示词 prompt 不能为空")
        self._call_count += 1
        reply_text = self._do_generate(cleaned)
        return {
            "provider": self.provider,
            "model": self.model_name,
            "temperature": self.temperature,
            "reply": reply_text,
            "call_index": self._call_count,
        }

    def __call__(self, prompt: str) -> Dict[str, Any]:
        """魔术方法：支持直接将模型实例当作函数调用 model('你好')。"""
        return self.generate(prompt)

    def __str__(self) -> str:
        return f"[{self.provider}] {self.model_name} (temp={self.temperature}, calls={self._call_count})"


if __name__ == "__main__":
    print("BaseModel 抽象基类定义完成，禁止直接实例化，请继承后使用。")

