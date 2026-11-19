"""
STARMIND-003 模块一：工单三级智能路由与批处理熔断引擎。
演示 if/elif/else、卫语句、for 循环、continue 跳过、break 熔断与 for-else 语法。
"""

from typing import List, Dict, Any


def route_single_ticket(text: str, amount: float, is_vip: bool) -> str:
    """
    根据工单内容、涉及金额与客户等级，决定分发通道：
    - L3_HUMAN: 投诉/法律风险 或 涉案金额 >= 5000 元
    - L2_FLAGSHIP_LLM: VIP 客户 或 金额 >= 500 元
    - L1_FAST_LLM: 普通日常咨询
    """
    cleaned = text.strip()
    # 卫语句 1：空工单直接返回无效标记
    if not cleaned:
        return "INVALID"

    # 卫语句 2：高风险关键词或大额纠纷直接转人工专家
    if "投诉" in cleaned or "起诉" in cleaned or amount >= 5000:
        return "L3_HUMAN"

    # VIP 客户或中等金额由旗舰大模型处理
    if is_vip or amount >= 500:
        return "L2_FLAGSHIP_LLM"

    # 其余走低成本轻量大模型
    return "L1_FAST_LLM"


def process_ticket_batch(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量扫描工单队列：
    - 空文本工单：continue 跳过并计入 skipped
    - 包含 'ATTACK_PAYLOAD' 的恶意攻击单：立即 break 触发全队列熔断
    """
    stats: Dict[str, Any] = {
        "L1_FAST_LLM": 0,
        "L2_FLAGSHIP_LLM": 0,
        "L3_HUMAN": 0,
        "skipped": 0,
        "circuit_broken": False,
    }

    for ticket in tickets:
        text = str(ticket.get("text", "")).strip()
        # 空工单使用 continue 跳过，不消耗路由资源
        if not text:
            stats["skipped"] += 1
            continue

        # 检测到批量注入攻击特征，立即 break 熔断保护下游
        if "ATTACK_PAYLOAD" in text:
            stats["circuit_broken"] = True
            break

        channel = route_single_ticket(
            text=text,
            amount=float(ticket.get("amount", 0.0)),
            is_vip=bool(ticket.get("is_vip", False)),
        )
        stats[channel] += 1
    else:
        # 仅当循环未被 break 打断时执行，确认批次完整扫描
        stats["completed_cleanly"] = True

    stats.setdefault("completed_cleanly", False)
    return stats


if __name__ == "__main__":
    sample_batch = [
        {"text": "请问怎么修改发票抬头？", "amount": 0, "is_vip": False},
        {"text": "   ", "amount": 0, "is_vip": False},
        {"text": "订单延迟发货我要投诉！", "amount": 200, "is_vip": False},
        {"text": "VIP 专属套餐续费咨询", "amount": 1200, "is_vip": True},
    ]
    print("批次处理统计:", process_ticket_batch(sample_batch))

