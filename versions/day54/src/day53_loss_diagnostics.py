"""
Day 53 - 模块二：微调 Loss 曲线模拟与过拟合/欠拟合自动诊断引擎
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class LossPoint:
    """单个评估检查点的训练/验证损失"""
    step: int
    train_loss: float
    eval_loss: float


@dataclass
class DiagnosisResult:
    """Loss 曲线诊断报告"""
    status: str                  # "healthy" | "overfitting" | "underfitting" | "diverging"
    best_step: Optional[int]
    best_eval_loss: Optional[float]
    overfit_gap: float
    advice: str


def diagnose_loss_curve(points: List[LossPoint]) -> DiagnosisResult:
    """分析训练与验证 Loss 序列，输出健康状态、最佳早停点与调参建议"""
    if len(points) < 3:
        raise ValueError("至少需要 3 个评估点才能进行趋势诊断")

    # 1. 检测梯度爆炸 / NaN / 剧烈反弹
    for p in points:
        if math.isnan(p.train_loss) or math.isnan(p.eval_loss) or p.train_loss > 10.0:
            return DiagnosisResult(
                status="diverging",
                best_step=None,
                best_eval_loss=None,
                overfit_gap=0.0,
                advice="检测到 Loss 出现 NaN 或剧烈发散！请将 learning_rate 减半(如 5e-5)、开启 bf16 并检查脏数据。",
            )

    if points[-1].train_loss > points[0].train_loss * 1.15:
        return DiagnosisResult(
            status="diverging",
            best_step=points[0].step,
            best_eval_loss=points[0].eval_loss,
            overfit_gap=round(points[-1].eval_loss - points[-1].train_loss, 4),
            advice="训练 Loss 不降反升，学习率过大或数据格式模板错位，请检查 template 与 lr。",
        )

    best_pt = min(points, key=lambda x: x.eval_loss)
    last_pt = points[-1]
    gap = round(last_pt.eval_loss - last_pt.train_loss, 4)

    # 2. 检测过拟合：eval_loss 在最低点之后明显反弹(>8%)且 train_loss 仍在下降
    rebound_ratio = (last_pt.eval_loss - best_pt.eval_loss) / max(best_pt.eval_loss, 1e-6)
    if best_pt.step < last_pt.step and rebound_ratio >= 0.08 and last_pt.train_loss < best_pt.train_loss:
        return DiagnosisResult(
            status="overfitting",
            best_step=best_pt.step,
            best_eval_loss=round(best_pt.eval_loss, 4),
            overfit_gap=gap,
            advice=(
                f"检测到过拟合（验证集 Loss 较最低点反弹 {rebound_ratio*100:.1f}%）。"
                f"建议直接回滚使用 checkpoint-{best_pt.step}，下轮减少 epoch 或增大 lora_dropout 至 0.1。"
            ),
        )

    # 3. 检测欠拟合：整体降幅过小且最终 Loss 仍偏高
    train_drop = (points[0].train_loss - last_pt.train_loss) / max(points[0].train_loss, 1e-6)
    if train_drop < 0.15 and last_pt.train_loss > 1.8:
        return DiagnosisResult(
            status="underfitting",
            best_step=best_pt.step,
            best_eval_loss=round(best_pt.eval_loss, 4),
            overfit_gap=gap,
            advice="检测到欠拟合（训练 Loss 降幅不足 15% 且仍高于 1.8）。建议调高学习率至 1e-4、增大 lora_rank 或增加 epoch。",
        )

    return DiagnosisResult(
        status="healthy",
        best_step=best_pt.step,
        best_eval_loss=round(best_pt.eval_loss, 4),
        overfit_gap=gap,
        advice=f"训练收敛健康！建议使用最优权重 checkpoint-{best_pt.step} 进入下一阶段自动评测。",
    )


if __name__ == "__main__":
    overfit_curve = [
        LossPoint(40, 2.15, 2.20),
        LossPoint(80, 1.35, 1.48),
        LossPoint(120, 0.85, 1.12),
        LossPoint(160, 0.42, 1.24),
        LossPoint(200, 0.18, 1.41),
    ]
    print("过拟合场景诊断:", diagnose_loss_curve(overfit_curve))

