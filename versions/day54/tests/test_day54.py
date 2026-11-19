import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 54 单元测试：微调评测门禁与 LoRA 合并量化配置"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day54_eval_gate import EvalCase, run_ab_eval_gate
from src.day54_merge_and_quant import build_export_and_quant_plan, verify_merge_equivalence


def test_eval_gate_passes_on_domain_gain_and_stable_general():
    cases = [
        EvalCase("D1", "domain", ["OCR", "工单"], True),
        EvalCase("G1", "general", ["Python"], False),
    ]
    base = {"D1": "请重试。", "G1": "Python 很适合写后端。"}
    ft = {"D1": "1. 开启OCR开关。\n2. 异常提交工单。", "G1": "Python 很适合写后端。"}
    rep = run_ab_eval_gate(cases, base, ft)
    assert rep.passed is True
    assert rep.domain_gain >= 0.9


def test_eval_gate_blocks_catastrophic_forgetting():
    cases = [
        EvalCase("D1", "domain", ["工单"], False),
        EvalCase("G1", "general", ["北京", "首都"], False),
    ]
    base = {"D1": "不知道", "G1": "北京是中国首都。"}
    ft = {"D1": "请提交工单处理。", "G1": "请携带工单号联系客服。"}
    rep = run_ab_eval_gate(cases, base, ft)
    assert rep.passed is False
    assert "灾难性遗忘" in rep.reason


def test_lora_merge_mathematical_equivalence():
    w0 = [[0.5, -0.3, 0.2], [0.1, 0.7, -0.4], [0.6, 0.2, 0.9]]
    a = [[0.1, -0.2, 0.3], [0.4, 0.1, -0.1]]
    b = [[0.2, 0.5], [-0.3, 0.1], [0.4, -0.2]]
    x = [[1.5], [-0.5], [2.0]]
    err = verify_merge_equivalence(x, w0, a, b, lora_alpha=16.0, lora_rank=8)
    assert err < 1e-12


def test_quant_plan_routes_vllm_to_awq_and_ollama_to_gguf():
    p_vllm = build_export_and_quant_plan("Qwen/Qwen2.5-7B-Instruct", "adp", "exp", "vllm")
    p_ollama = build_export_and_quant_plan("Qwen/Qwen2.5-7B-Instruct", "adp", "exp", "ollama")
    assert p_vllm.quant_format == "AWQ-INT4"
    assert p_ollama.quant_format == "GGUF-Q4_K_M"
    assert "quantization_bit" not in p_vllm.export_yaml

