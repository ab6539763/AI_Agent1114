import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 51 单元测试：微调决策引擎与 GPU 显存估算器"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.day51_strategy_advisor import ScenarioProfile, advise_llm_strategy
from src.day51_vram_calculator import estimate_finetune_vram


def test_strategy_realtime_knowledge_prefers_rag():
    profile = ScenarioProfile("促销问答", "realtime", 2, 100, False, 3)
    rep = advise_llm_strategy(profile)
    assert "RAG" in rep.primary_strategy
    assert "微调" not in rep.primary_strategy


def test_strategy_hybrid_with_low_samples_warns():
    profile = ScenarioProfile("客服混合", "weekly", 5, 120, True, 5)
    rep = advise_llm_strategy(profile)
    assert "RAG + LoRA" in rep.primary_strategy
    assert len(rep.warnings) >= 1


def test_vram_ordering_full_gt_lora_gt_qlora():
    full = estimate_finetune_vram("Qwen2.5-7B", method="full")
    lora = estimate_finetune_vram("Qwen2.5-7B", method="lora")
    qlora = estimate_finetune_vram("Qwen2.5-7B", method="qlora")
    assert full.total_gb > 100.0
    assert 15.0 < lora.total_gb < 22.0
    assert qlora.total_gb < 12.0
    assert "4090" in lora.recommended_gpu


def test_gradient_checkpointing_reduces_activation_memory():
    with_gc = estimate_finetune_vram("Qwen2.5-7B", method="lora", gradient_checkpointing=True)
    no_gc = estimate_finetune_vram("Qwen2.5-7B", method="lora", gradient_checkpointing=False)
    assert with_gc.activations_gb < no_gc.activations_gb * 0.4


def test_invalid_model_raises():
    with pytest.raises(ValueError):
        estimate_finetune_vram("Unknown-999B", method="lora")

