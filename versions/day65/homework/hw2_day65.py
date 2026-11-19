"""
Day 65 课后作业 2（企业实战）：企业实战：计算 3 分钟电梯演讲（Elevator Pitch）字数合规校验
工单：STARMIND-065
"""

def check_pitch_length(text: str, minutes: int = 3) -> bool:
    n = len("".join(text.split()))
    return minutes * 180 <= n <= minutes * 250


sample = "星辰智脑是面向企业内部知识问答与办公自动化的多智能体平台。" * 22
assert check_pitch_length(sample, minutes=3) is True
print("3分钟电梯演讲字数校验通过")

