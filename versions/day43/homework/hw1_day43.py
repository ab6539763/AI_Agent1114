"""
Day 43 课后作业 1（基础巩固）：为研究团队新增法务合规审核员（ReviewerAgent）
工单：STARMIND-043
"""

"""Day 43 作业 1 参考答案：法务合规审核员 Agent。"""

from typing import Any, Dict, List


class ComplianceReviewerAgent:
    name = "compliance_reviewer"
    BANNED_WORDS = ["绝对第一", "稳赚不赔", "100%保本"]

    def run(self, state: Dict[str, Any], feedback: str = "") -> Dict[str, Any]:
        draft = state.get("draft", "")
        hits: List[str] = [w for w in self.BANNED_WORDS if w in draft]
        return {"compliance_passed": len(hits) == 0, "violations": hits}


if __name__ == "__main__":
    agent = ComplianceReviewerAgent()
    r1 = agent.run({"draft": "本方案行业绝对第一，建议采纳。"})
    r2 = agent.run({"draft": "本方案在基准测试中表现优异，附风险提示。"})
    print("违规检测:", r1, "| 合规检测:", r2)
    assert r1["compliance_passed"] is False and r1["violations"] == ["绝对第一"]
    assert r2["compliance_passed"] is True

