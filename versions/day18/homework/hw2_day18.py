"""
Day 18 课后作业 2（企业实战）：简易 ToT（Tree of Thoughts）多分支故障排查评分器
工单：STARMIND-018
"""

from typing import Dict, List


def select_best_tot_branch(branches: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """模拟 ToT 思维树评估剪枝：综合命中概率与排查耗时选出最优分支。"""
    enriched = []
    for b in branches:
        prob = float(b["probability"])
        cost = max(1.0, float(b["cost_minutes"]))
        score = round(prob / (cost ** 0.5), 4)
        enriched.append({**b, "tot_score": score})
    enriched.sort(key=lambda x: x["tot_score"], reverse=True)
    return enriched


if __name__ == "__main__":
    cands = [
        {"hypothesis": "检查Nginx网关502日志", "cost_minutes": 2, "probability": 0.65},
        {"hypothesis": "全量重建数据库索引", "cost_minutes": 45, "probability": 0.70},
        {"hypothesis": "检查Redis连接池是否打满", "cost_minutes": 3, "probability": 0.55},
    ]
    for item in select_best_tot_branch(cands):
        print(item)

