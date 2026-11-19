"""
Day 70 - 模块二：星辰智脑 (StarMind) v1.0.0 正式发布验收门禁与结业证书签发器
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List


REQUIRED_STAGES = [
    "stage1_python_foundation",
    "stage2_llm_prompt_engineering",
    "stage3_hybrid_rag_rerank",
    "stage4_multi_agent_mcp_hitl",
    "stage5_finetune_vllm_security",
    "stage6_capstone_defense_release",
]


@dataclass
class ReleaseGateInput:
    graduate_name: str
    version: str
    completed_stages: List[str]
    ragas_faithfulness: float
    p95_latency_ms: float
    unit_tests_passed: bool
    security_audit_passed: bool


@dataclass
class ReleaseReceipt:
    version: str
    status: str  # RELEASED | BLOCKED
    blockers: List[str]
    manifest_sha256: str
    certificate_md: str


def evaluate_v1_release(inp: ReleaseGateInput) -> ReleaseReceipt:
    blockers: List[str] = []
    missing_stages = [s for s in REQUIRED_STAGES if s not in inp.completed_stages]
    if missing_stages:
        blockers.append(f"缺少未验收阶段: {missing_stages}")
    if inp.ragas_faithfulness < 0.80:
        blockers.append(f"Ragas 忠实度 {inp.ragas_faithfulness:.2f} 低于 v1.0.0 红线 0.80")
    if inp.p95_latency_ms > 500.0:
        blockers.append(f"压测 P95 延迟 {inp.p95_latency_ms}ms 超过 500ms 红线")
    if not inp.unit_tests_passed:
        blockers.append("自动化单元测试未全部通过")
    if not inp.security_audit_passed:
        blockers.append("安全合规与容器审计未通过")

    status = "RELEASED" if not blockers else "BLOCKED"
    payload = json.dumps(
        {
            "graduate": inp.graduate_name,
            "version": inp.version,
            "status": status,
            "stages": sorted(inp.completed_stages),
            "faithfulness": inp.ragas_faithfulness,
            "p95_ms": inp.p95_latency_ms,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    if status == "RELEASED":
        cert = (
            "====================================================\n"
            "      星辰智脑 (StarMind) 70天企业级AI实战 结业证书\n"
            "====================================================\n"
            f"学员姓名: {inp.graduate_name}\n"
            f"正式版本: StarMind v{inp.version} (RELEASED)\n"
            f"验收指标: Faithfulness={inp.ragas_faithfulness:.1%}, P95={inp.p95_latency_ms}ms\n"
            f"发布指纹: {digest[:16]}...\n"
            "签发寄语: 敬畏生产、量化迭代，祝前程似锦，顶峰相见！\n"
        )
    else:
        cert = f"发布拦截 ({status})，请先修复以下阻塞项: {blockers}\n"

    return ReleaseReceipt(inp.version, status, blockers, digest, cert)


if __name__ == "__main__":
    receipt = evaluate_v1_release(
        ReleaseGateInput(
            graduate_name="星辰全栈工程师",
            version="1.0.0",
            completed_stages=list(REQUIRED_STAGES),
            ragas_faithfulness=0.92,
            p95_latency_ms=185.0,
            unit_tests_passed=True,
            security_audit_passed=True,
        )
    )
    print(receipt.certificate_md)

