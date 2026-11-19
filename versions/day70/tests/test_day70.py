import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 70 单元测试：多模态路由、成长路线图与 StarMind v1.0.0 结业发布门禁"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day70_frontier_and_roadmap import MultimodalRequest, build_12month_roadmap, route_multimodal_agent
from src.day70_v1_release_gate import REQUIRED_STAGES, ReleaseGateInput, evaluate_v1_release


def test_multimodal_router_and_roadmap():
    img_plan = route_multimodal_agent(MultimodalRequest("image", "invoice_ocr", "专票"))
    aud_plan = route_multimodal_agent(MultimodalRequest("audio", "voice_assistant", "语音查询"))
    assert "vlm_vision_parse" in img_plan.pipeline_steps
    assert "streaming_asr" in aud_plan.pipeline_steps
    rm = build_12month_roadmap("林同学")
    assert len(rm["quarters"]) == 4


def test_v1_release_gate_releases_when_all_green():
    receipt = evaluate_v1_release(
        ReleaseGateInput(
            graduate_name="张明",
            version="1.0.0",
            completed_stages=list(REQUIRED_STAGES),
            ragas_faithfulness=0.91,
            p95_latency_ms=180.0,
            unit_tests_passed=True,
            security_audit_passed=True,
        )
    )
    assert receipt.status == "RELEASED"
    assert receipt.blockers == []
    assert len(receipt.manifest_sha256) == 64
    assert "StarMind v1.0.0 (RELEASED)" in receipt.certificate_md


def test_v1_release_gate_blocks_incomplete_release():
    receipt = evaluate_v1_release(
        ReleaseGateInput(
            graduate_name="张明",
            version="1.0.0",
            completed_stages=REQUIRED_STAGES[:-1],
            ragas_faithfulness=0.60,
            p95_latency_ms=800.0,
            unit_tests_passed=False,
            security_audit_passed=True,
        )
    )
    assert receipt.status == "BLOCKED"
    assert len(receipt.blockers) == 4

