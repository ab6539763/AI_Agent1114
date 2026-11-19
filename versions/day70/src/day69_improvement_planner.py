"""
Day 69 - 模块二：基于模拟面试弱项的 7 天靶向改进清单生成器
"""
from __future__ import annotations

from typing import Dict, List

from src.day69_mock_interview_scorer import MockInterviewResult

REMEDIATION_PLAYBOOK: Dict[str, str] = {
    "coding_algo": "闭眼手撕 Attention/Top-P/令牌桶/TTL-LRU 与 5 道高频异步并发题，计时 25 分钟/题。",
    "llm_rag_theory": "复盘混合检索 RRF、Rerank、KV Cache、LoRA/QLoRA 数学直觉与防幻觉门禁。",
    "project_depth": "为星辰智脑补齐 4 张 5 层 ADR 防问穿卡片（含真实故障定位与量化对比）。",
    "system_design": "白板限时 30 分钟独立推导 10 万 DAU 知识库 Peak QPS、SQ8 向量内存与 GPU 算力账单。",
    "hr_culture_fit": "打磨 3 分钟自我介绍、动机一致性故事、缺点改进公式及 3 个高情商反问问题。",
}


def generate_7day_plan(result: MockInterviewResult) -> str:
    lines: List[str] = [
        f"# {result.candidate} 模拟面试 7 天靶向冲刺改进清单",
        f"- 当前综合分: **{result.weighted_score}** | 评估结论: **{result.decision}**",
        f"- 红线项(<60): {result.red_flags or '无'}",
        "",
        "## 每日靶向整改任务",
    ]
    targets = result.weak_areas or ["project_depth", "system_design"]
    for day_idx in range(1, 6):
        dim = targets[(day_idx - 1) % len(targets)]
        priority = "P0-红线攻坚" if dim in result.red_flags else "P1-专项拔高"
        lines.append(f"- **Day {day_idx} [{priority} - {dim}]**: {REMEDIATION_PLAYBOOK[dim]}")

    lines.append("- **Day 6 [全真二轮复测]**: 完整模拟 45m 技术面 + 20m HR 面，录屏回看语速与逻辑。")
    lines.append("- **Day 7 [投递冲刺启动]**: 按目标岗位 JD 微调简历关键词，开始首批重点投递。")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    from src.day69_mock_interview_scorer import evaluate_mock_interview

    r = evaluate_mock_interview(
        "林同学",
        {
            "coding_algo": 55,
            "llm_rag_theory": 86,
            "project_depth": 88,
            "system_design": 74,
            "hr_culture_fit": 82,
        },
    )
    print(generate_7day_plan(r))

