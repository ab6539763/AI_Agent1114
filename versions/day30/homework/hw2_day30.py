"""
Day 30 课后作业 2（企业实战）：作业二：实现基于拒答信号的工单自动转人工路由
工单：STARMIND-030
"""

"""Day 30 作业二参考答案：RAG 拒答自动转人工工单闭环"""
import sys
import uuid
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day30_kb_cli import build_starmind_kb


def ask_with_escalation(kb, question: str, emp_id: str) -> Dict[str, Any]:
    resp = kb.ask(question)
    if not resp.is_fallback:
        return {"mode": "rag_answered", "answer": resp.answer, "citations": len(resp.citations)}

    if any(k in question for k in ("工资", "薪资", "社保", "离职")):
        desk = "HRBP人工服务台"
    elif any(k in question for k in ("发票", "打款", "税率")):
        desk = "财务共享中心"
    elif any(k in question for k in ("电脑", "账号", "门禁")):
        desk = "IT运维台"
    else:
        desk = "行政综合服务台"

    return {
        "mode": "escalated_ticket",
        "answer": resp.answer,
        "ticket": {
            "ticket_id": f"TK-{uuid.uuid4().hex[:6].upper()}",
            "emp_id": emp_id,
            "question": question,
            "target_desk": desk,
        },
    }


if __name__ == "__main__":
    kb = build_starmind_kb()
    out = ask_with_escalation(kb, "请问公积金缴存比例今年调整了吗？我的社保明细在哪查？", emp_id="E1024")
    print("转人工结果:", out)
    assert out["mode"] == "escalated_ticket" and out["ticket"]["target_desk"] == "HRBP人工服务台"

