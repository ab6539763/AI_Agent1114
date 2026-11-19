"""
Day 03 课后作业 3（架构进阶）：架构进阶：二分查找自动猜数字求解器
工单：STARMIND-003
"""

"""Day 3 课后题 3：二分查找自动猜数求解器。"""

from typing import List


def binary_search_guess(secret: int, low: int = 1, high: int = 100) -> List[int]:
    """使用二分法定位目标值，返回完整猜测序列。"""
    path: List[int] = []
    while low <= high:
        mid = (low + high) // 2
        path.append(mid)
        if mid == secret:
            break
        elif mid < secret:
            low = mid + 1
        else:
            high = mid - 1
    return path


if __name__ == "__main__":
    trace = binary_search_guess(73)
    print(f"猜测路径: {trace}，仅用 {len(trace)} 步命中！")

