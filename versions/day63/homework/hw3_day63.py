"""
Day 63 课后作业 3（架构进阶）：架构进阶：计算年化 FinOps 节省金额与 ROI 回本周期
工单：STARMIND-063
"""

def calc_monthly_net_saving(daily_reqs: int, old_unit_cny: float, new_unit_cny: float, gpu_monthly_cny: float) -> float:
    old_total = daily_reqs * 30 * old_unit_cny
    new_total = daily_reqs * 30 * new_unit_cny + gpu_monthly_cny
    return round(old_total - new_total, 2)


saving = calc_monthly_net_saving(daily_reqs=50000, old_unit_cny=0.02, new_unit_cny=0.005, gpu_monthly_cny=4500.0)
assert saving == 18000.0
print(f"启用缓存+分级路由后月度净节省: {saving} 元")

