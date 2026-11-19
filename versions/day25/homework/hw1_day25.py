"""
Day 25 课后作业 1（基础巩固）：作业一：实现多模型路由适配器（ModelRouter）
工单：STARMIND-025
"""

"""Day 25 作业一参考答案：轻量/旗舰双模型智能路由器"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import AIMessage, BaseMessage, HumanMessage, StarMindChatModel


class ModelRouter:
    COMPLEX_KEYWORDS = ("代码", "报错", "架构", "SQL", "并发", "性能")

    def __init__(self) -> None:
        self.fast_model = StarMindChatModel(model_name="qwen2.5-7b-fast", temperature=0.3)
        self.strong_model = StarMindChatModel(model_name="deepseek-v3-pro", temperature=0.1)

    def invoke(self, text: str) -> AIMessage:
        is_complex = len(text) > 20 or any(k in text for k in self.COMPLEX_KEYWORDS)
        tier = "strong" if is_complex else "fast"
        model = self.strong_model if is_complex else self.fast_model
        resp = model.invoke([HumanMessage(content=text)])
        resp.response_metadata["routed_tier"] = tier
        return resp


if __name__ == "__main__":
    router = ModelRouter()
    r1 = router.invoke("你好呀")
    r2 = router.invoke("帮我排查一下高并发下数据库死锁报错问题")
    print("简单请求 ->", r1.response_metadata["model_name"], r1.response_metadata["routed_tier"])
    print("复杂请求 ->", r2.response_metadata["model_name"], r2.response_metadata["routed_tier"])
    assert r1.response_metadata["routed_tier"] == "fast"
    assert r2.response_metadata["routed_tier"] == "strong"

