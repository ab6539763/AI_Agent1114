"""
Day 51 课后作业 3（架构进阶）：架构进阶：微调 ROI 成本回本周期计算器
工单：STARMIND-051
"""

def calculate_finetune_roi(
    daily_tokens_million: float,
    api_price_per_million: float,
    one_time_ft_cost: float,
    monthly_gpu_hosting_cost: float,
) -> dict:
    """计算私有化微调相对闭源 API 的回本周期与年化收益"""
    daily_api_cost = daily_tokens_million * api_price_per_million
    daily_self_host_cost = monthly_gpu_hosting_cost / 30.0
    daily_saving = daily_api_cost - daily_self_host_cost

    if daily_saving <= 0:
        return {"worth_it": False, "reason": "当前调用量过低，直接调 API 更划算"}

    payback_days = round(one_time_ft_cost / daily_saving, 1)
    annual_saving = round(daily_saving * 365 - one_time_ft_cost, 2)
    return {
        "worth_it": True,
        "daily_api_cost": round(daily_api_cost, 2),
        "daily_self_host_cost": round(daily_self_host_cost, 2),
        "payback_days": payback_days,
        "annual_net_saving_cny": annual_saving,
    }


if __name__ == "__main__":
    print(calculate_finetune_roi(5.0, 8.0, 3000.0, 1800.0))

