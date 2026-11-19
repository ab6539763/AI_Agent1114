import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 68 单元测试：十万 DAU 容量估算引擎与 5 层 ADR 防问穿校验"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day68_capacity_estimator import ScaleSpec, estimate_capacity
from src.day68_deep_dive_defense import ArchitectureDecisionCard, audit_adr_readiness


def test_capacity_estimator_100k_dau_and_quantization():
    fp32_rep = estimate_capacity(ScaleSpec(use_sq8_quant=False))
    sq8_rep = estimate_capacity(ScaleSpec(use_sq8_quant=True))
    assert fp32_rep.daily_requests == 1_000_000
    assert 55.0 <= fp32_rep.peak_qps <= 60.0
    assert sq8_rep.vector_ram_gb < fp32_rep.vector_ram_gb * 0.3
    assert sq8_rep.monthly_hybrid_cny < sq8_rep.monthly_cloud_only_cny


def test_adr_audit_passes_complete_and_catches_shallow_card():
    good = ArchitectureDecisionCard(
        topic="HITL 审批门禁设计",
        l1_problem="高额报销自动提交存在资损风险。",
        l2_alternatives=["纯Prompt约束(易越狱)", "代码层确定性策略+审批状态机(强可控)"],
        l3_pitfall_lesson="前端双击导致重复审批打款，增加 PENDING 终态幂等锁返回 409。",
        l4_metric_proof="高危误执行率降至 0%，审批接口 P95 耗时 25ms。",
        l5_scale_10x_plan="审批状态迁移至 PostgreSQL 行级悲观锁 + 飞书审批卡片异步回调。",
    )
    shallow = ArchitectureDecisionCard("选型", "需要做", ["只看了一个"], "没踩坑", "效果不错", "加机器")
    assert audit_adr_readiness(good)["ready"] is True
    assert audit_adr_readiness(shallow)["ready"] is False
    assert len(audit_adr_readiness(shallow)["missing"]) >= 4

