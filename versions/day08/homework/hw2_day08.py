"""
Day 08 课后作业 2（企业实战）：企业实战：带过期标记的提示词模板类
工单：STARMIND-008
"""

"""Day 8 课后题 2：带实例计数的提示词资产类。"""


class PromptAsset:
    """企业级 Prompt 资产管理对象。"""

    total_created: int = 0

    def __init__(self, name: str, version: str, template: str) -> None:
        self.name = name
        self.version = version
        self.template = template
        type(self).total_created += 1

    def render(self, **kwargs) -> str:
        return self.template.format(**kwargs)

    @classmethod
    def get_total_created(cls) -> int:
        return cls.total_created


if __name__ == "__main__":
    p1 = PromptAsset("客服问候", "v1.0", "你好 {user}，请问有什么可以帮您？")
    p2 = PromptAsset("工单总结", "v1.2", "请用一句话总结：{text}")
    print(p1.render(user="林产品"))
    print("累计创建模板数:", PromptAsset.get_total_created())

