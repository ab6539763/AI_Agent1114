"""
Day 03 课后作业 1（基础巩固）：基础巩固：API 限流退避重试模拟器
工单：STARMIND-003
"""

"""Day 3 课后题 1：API 限流重试策略模拟器。"""

from typing import List, Tuple


def simulate_retry(statuses: List[int], max_retries: int = 4) -> Tuple[bool, int]:
    """模拟接口重试：200 成功，429 继续，401 鉴权失败直接放弃。"""
    attempts = 0
    for code in statuses[:max_retries]:
        attempts += 1
        if code == 200:
            return True, attempts
        if code == 401:
            # 密钥错误重试多少次都没用，直接 break 止损
            break
    return False, attempts


if __name__ == "__main__":
    print("场景1(重试成功):", simulate_retry([429, 429, 200]))
    print("场景2(鉴权熔断):", simulate_retry([429, 401, 200]))

