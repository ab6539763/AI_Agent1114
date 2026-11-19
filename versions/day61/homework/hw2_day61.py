"""
Day 61 课后作业 2（企业实战）：企业实战：给审批单增加超时自动过期机制（TTL）
工单：STARMIND-061
"""

def is_ticket_expired(created_ts: float, now_ts: float, ttl_seconds: float = 86400.0) -> bool:
    return (now_ts - created_ts) > ttl_seconds


assert is_ticket_expired(1000.0, 90000.0) is True
assert is_ticket_expired(1000.0, 2000.0) is False
print("审批单 TTL 过期检查通过")

