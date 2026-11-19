import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 53 单元测试：LLaMA-Factory YAML 生成与 Loss 曲线诊断"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.day53_llamafactory_config import LoRATrainPlan, validate_and_render_yaml
from src.day53_loss_diagnostics import LossPoint, diagnose_loss_curve


def test_yaml_generation_contains_qwen_template_and_qlora():
    yaml_str = validate_and_render_yaml(LoRATrainPlan(use_qlora_4bit=True))
    assert "template: qwen" in yaml_str
    assert "quantization_bit: 4" in yaml_str
    assert "lora_target: all" in yaml_str


def test_yaml_rejects_dangerous_learning_rate():
    with pytest.raises(ValueError):
        validate_and_render_yaml(LoRATrainPlan(learning_rate=5e-3))


def test_diagnose_healthy_curve():
    pts = [LossPoint(30, 2.2, 2.3), LossPoint(60, 1.4, 1.5), LossPoint(90, 0.9, 1.05)]
    res = diagnose_loss_curve(pts)
    assert res.status == "healthy"
    assert res.best_step == 90


def test_diagnose_overfitting_finds_best_checkpoint():
    pts = [
        LossPoint(40, 2.0, 2.1),
        LossPoint(80, 1.1, 1.25),
        LossPoint(120, 0.6, 1.10),
        LossPoint(160, 0.25, 1.35),
    ]
    res = diagnose_loss_curve(pts)
    assert res.status == "overfitting"
    assert res.best_step == 120


def test_diagnose_diverging_nan():
    pts = [LossPoint(10, 2.0, 2.1), LossPoint(20, float("nan"), 2.5), LossPoint(30, 5.0, 6.0)]
    res = diagnose_loss_curve(pts)
    assert res.status == "diverging"

