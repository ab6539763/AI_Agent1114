"""
Day 43 课后作业 2（企业实战）：实现单角色最大返工次数限制器
工单：STARMIND-043
"""

"""Day 43 作业 2 参考答案：单角色连续返工熔断检测。"""

from typing import Any, Dict, List


def detect_excessive_rework(history: List[Dict[str, Any]], limit: int = 2) -> bool:
    last_agent = None
    streak = 0
    for item in history:
        agent = item["next_agent"]
        if agent == last_agent:
            streak += 1
        else:
            last_agent = agent
            streak = 1
        if streak > limit:
            return True
    return False


if __name__ == "__main__":
    ok_hist = [{"next_agent": "writer"}, {"next_agent": "writer"}]
    bad_hist = [{"next_agent": "writer"}, {"next_agent": "writer"}, {"next_agent": "writer"}]
    assert detect_excessive_rework(ok_hist, limit=2) is False
    assert detect_excessive_rework(bad_hist, limit=2) is True
    print("连续返工熔断检测通过")

