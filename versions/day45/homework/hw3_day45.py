"""
Day 45 课后作业 3（架构进阶）：设计低代码向代码自研迁移的渐进式灰度策略
工单：STARMIND-045
"""

"""Day 45 作业 3 参考答案：基于一致性哈希的低代码->自研平滑灰度切流器。"""

import hashlib


class TrafficSplitter:
    def __init__(self, langgraph_ratio: float = 0.2) -> None:
        self.threshold = int(max(0.0, min(1.0, langgraph_ratio)) * 100)

    def route(self, user_id: str) -> str:
        bucket = int(hashlib.md5(user_id.encode("utf-8")).hexdigest()[:8], 16) % 100
        return "langgraph" if bucket < self.threshold else "dify"


if __name__ == "__main__":
    splitter = TrafficSplitter(langgraph_ratio=0.3)
    first = splitter.route("emp_10086")
    second = splitter.route("emp_10086")
    assert first == second
    print("用户 emp_10086 稳定命中:", first)

