"""
星辰智脑 (StarMind) 70 天实战课程数据结构规范。
所有 6 个阶段的课程数据模块 (stage1_days01_14.py ~ stage6_days58_70.py) 均遵循本模块定义的字典结构，
以确保 HTML5 课件、Jupyter Notebook、每日版本迭代代码和 Markdown 辅助文档 100% 环环相扣、无缝生成。
"""

from typing import TypedDict, List, Dict, Any


class CodeStep(TypedDict):
    step_title: str            # 步骤标题，如 "步骤一：定义企业员工信息结构体与脱敏输出"
    file_path: str             # 该代码在当日版本中的相对路径，如 "src/day01_profile.py"
    narration: str             # 老陈针对这一段代码的上下文旁白与设计意图
    code: str                  # 完整可运行、带详细中文逐行注释的 Python/JS/YAML/SQL 代码
    explanation: str           # 逐行代码深度解析、常见坑点与工程最佳实践
    expected_output: str       # 运行该代码后的预期控制台输出示例


class HomeworkItem(TypedDict):
    title: str                 # 题目名称
    difficulty: str            # "基础巩固" | "企业实战" | "架构进阶"
    requirement: str           # 详细题目需求描述（贴合星辰智脑企业业务场景）
    hint: str                  # 思路提示
    solution_code: str         # 完整可运行的标准参考代码（带详细注释）
    solution_analysis: str     # 答案解析与评分标准


class DiagramSpec(TypedDict):
    title: str                 # 图表标题
    kind: str                  # "flowchart" | "architecture" | "sequence" | "schematic"
    caption: str               # 图表文字解读
    nodes: List[Dict[str, str]]  # 节点列表: [{"id": "n1", "label": "...", "sub": "...", "color": "..."}]
    edges: List[Dict[str, str]]  # 连线列表: [{"from": "n1", "to": "n2", "label": "..."}]


class DaySpec(TypedDict):
    day: int                   # 1 ~ 70
    stage: int                 # 1 ~ 6
    stage_name: str            # 阶段名称
    week: int                  # 1 ~ 10
    week_name: str             # 周主题
    title: str                 # 当天课程标题
    subtitle: str              # 当天企业实战副标题
    gitlab_ticket: str         # 如 "STARMIND-001"
    git_branch: str            # 如 "feat/day01-dev-env-profile"
    git_commit: str            # 如 "feat(day01): 初始化开发环境并完成员工数字名片CLI工具"
    prev_recap: str            # 承上：昨日进度回顾与遗留问题
    next_preview: str          # 启下：明日迭代预告与技术铺垫
    narrator_opening: str      # 老陈开场旁白（真实国内研发团队口吻，无AI味）
    narrator_closing: str      # 老陈收尾复盘旁白
    business_prd: Dict[str, Any]  # 真实企业需求文档: background, pain_points, goals, acceptance_criteria, non_functional
    schedule: List[Dict[str, str]]  # 当日日程安排: [{"slot": "上午 09:00-12:00", "topic": "...", "detail": "..."}]
    architecture_design: str   # 架构设计与技术选型深度剖析（大段工程实战论述）
    diagrams: List[DiagramSpec]  # 至少3张图：流程图 + 架构设计图 + 原理示意图
    knowledge_notes: List[Dict[str, str]]  # 课堂核心笔记章节: [{"heading": "...", "content": "...", "pitfalls": "..."}]
    code_steps: List[CodeStep]  # 一步一步可粘贴运行的完整代码实操（至少2-3个递进模块）
    unit_test_code: str        # 当日版本自动化单元测试代码（pytest 可直接运行通过）
    gitlab_review_log: List[Dict[str, str]]  # 模拟 GitLab MR Code Review 评论记录（老陈/阿杰/林产品）
    homeworks: List[HomeworkItem]  # 课后作业与完整答案（至少3道梯度题：基础+实战+进阶）
    extra_deep_dive: str       # 生产级踩坑实录 / 源码级原理拓展 / 国内企业落地经验谈
