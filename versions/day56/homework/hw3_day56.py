"""
Day 56 课后作业 3（架构进阶）：架构进阶：实现零停机蓝绿发布流量切换校验器
工单：STARMIND-056
"""

def switch_traffic(active_slot: str, blue_healthy: bool, green_healthy: bool) -> dict:
    target = "green" if active_slot == "blue" else "blue"
    target_ok = green_healthy if target == "green" else blue_healthy
    if not target_ok:
        return {"switched": False, "active": active_slot, "reason": f"目标槽位 {target} 未通过健康检查，拒绝切流"}
    return {"switched": True, "active": target, "reason": f"已平滑将 100% 流量从 {active_slot} 切至 {target}"}


print(switch_traffic("blue", True, True))
print(switch_traffic("blue", True, False))

