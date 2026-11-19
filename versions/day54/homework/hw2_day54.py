"""
Day 54 课后作业 2（企业实战）：企业实战：多 LoRA 权重加权融合（Model Soup 简化版）
工单：STARMIND-054
"""

def blend_weights(w1, w2, ratio: float = 0.7):
    if len(w1) != len(w2) or len(w1[0]) != len(w2[0]):
        raise ValueError("矩阵维度不一致，无法融合")
    return [
        [round(ratio * w1[i][j] + (1.0 - ratio) * w2[i][j], 6) for j in range(len(w1[0]))]
        for i in range(len(w1))
    ]


print(blend_weights([[1.0, 2.0]], [[3.0, 4.0]], ratio=0.5))

