"""
Day 48 课后作业 1（基础巩固）：为日程工具增加空闲时段自动推荐功能
工单：STARMIND-048
"""

"""Day 48 作业 1 参考答案：工作日空闲会议时段自动推荐器。"""

from typing import Dict, List, Tuple


def suggest_free_slots(meetings: List[Dict[str, int]], duration: int = 1) -> List[Tuple[int, int]]:
    free: List[Tuple[int, int]] = []
    for h in range(9, 18 - duration + 1):
        end = h + duration
        conflict = any(h < m["end_hour"] and m["start_hour"] < end for m in meetings)
        if not conflict:
            free.append((h, end))
    return free


if __name__ == "__main__":
    booked = [{"start_hour": 10, "end_hour": 11}, {"start_hour": 14, "end_hour": 16}]
    slots = suggest_free_slots(booked, duration=1)
    print("推荐空闲时段:", slots)
    assert (10, 11) not in slots and (11, 12) in slots and (14, 15) not in slots

