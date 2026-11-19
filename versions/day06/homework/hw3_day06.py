"""
Day 06 课后作业 3（架构进阶）：架构进阶：递归统计嵌套 JSON 中所有数值型 Token 总和
工单：STARMIND-006
"""

"""Day 6 课后题 3：递归汇总嵌套多 Agent 日志中的总 Token 消耗。"""

from typing import Any


def sum_nested_tokens(data: Any) -> int:
    """递归遍历任意深度 dict/list，汇总所有键名为 'tokens' 的整数值。"""
    total = 0
    if isinstance(data, dict):
        for k, v in data.items():
            # 注意：Python 中 bool 是 int 的子类，需排除 True/False
            if k == "tokens" and isinstance(v, int) and not isinstance(v, bool):
                total += v
            else:
                total += sum_nested_tokens(v)
    elif isinstance(data, list):
        for item in data:
            total += sum_nested_tokens(item)
    return total


if __name__ == "__main__":
    trace = {
        "agent": "planner",
        "tokens": 150,
        "subtasks": [
            {"agent": "search", "tokens": 300},
            {"agent": "writer", "tokens": 450, "retries": [{"tokens": 100}]},
        ],
    }
    print("多 Agent 总消耗 Token:", sum_nested_tokens(trace))

