"""
Day 58 课后作业 1（基础巩固）：基础巩固：为选题矩阵补充个人背景加权偏好（后端转AI / 算法转AI）
工单：STARMIND-058
"""

from src.day58_topic_matrix import TOPICS_8

recommended = [t.name for t in TOPICS_8 if t.engineering_depth >= 9 and t.six_day_feasibility >= 8]
print("后端转AI高匹配选题:", recommended)

