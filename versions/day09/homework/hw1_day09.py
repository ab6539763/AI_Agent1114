"""
Day 09 课后作业 1（基础巩固）：基础巩固：扩展 DeepSeekModel 子类
工单：STARMIND-009
"""

"""Day 9 课后题 1：扩展支持思考模式的 DeepSeekModel 子类。"""


class SimpleBaseLLM:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class DeepSeekModel(SimpleBaseLLM):
    def __init__(self, model_name: str = "deepseek-reasoner", enable_thinking: bool = True) -> None:
        super().__init__(model_name)
        self.enable_thinking = enable_thinking

    def generate(self, prompt: str) -> str:
        prefix = "<think>正在拆解问题逻辑...</think> " if self.enable_thinking else ""
        return f"{prefix}[{self.model_name}] 回答: {prompt}"


if __name__ == "__main__":
    ds = DeepSeekModel(enable_thinking=True)
    print(ds.generate("解释什么是多态"))

