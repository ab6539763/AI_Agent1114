"""
星辰智脑 (StarMind) 70 天 Jupyter Notebook 实操手册生成器。
将每一天的课程讲义、老陈旁白、步步可运行代码、单元测试与课后作业标准答案
组装为标准 nbformat v4 `.ipynb` 文件，支持在 Jupyter Lab / VS Code 中一键逐格运行。
"""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from pathlib import Path
from typing import Dict


def render_day_notebook(day_spec: Dict, output_path: Path) -> None:
    day = day_spec["day"]
    cells = []

    # 1. 封面与老陈旁白
    cells.append(new_markdown_cell(
        f"# Day {day:02d}：{day_spec['title']}（Jupyter Notebook 实战手册）\n\n"
        f"> **所属阶段**：第 {day_spec['stage']} 阶段 · {day_spec['stage_name']} ｜ **第 {day_spec['week']} 周**：{day_spec['week_name']}  \n"
        f"> **GitLab 工单**：`{day_spec['gitlab_ticket']}` ｜ **开发分支**：`{day_spec['git_branch']}`  \n"
        f"> **配套 HTML5 课件**：`courseware/day{day:02d}/index.html` ｜ **独立版本快照**：`versions/day{day:02d}/`\n\n"
        f"---\n\n"
        f"## 🎙️ 老陈开场旁白\n\n"
        f"{day_spec['narrator_opening']}\n\n"
        f"### 承上启下\n"
        f"- **昨日基线**：{day_spec['prev_recap']}\n"
        f"- **明日预告**：{day_spec['next_preview']}\n"
    ))

    # 2. 环境自检 Cell（确保 Notebook 定位到当日版本目录，支持 asyncio.run 与 src 模块导入）
    cells.append(new_code_cell(
        f"# 环境自检与路径初始化：确保可以无缝导入当日版本模块并支持异步协程运行\n"
        f"import os\n"
        f"import sys\n"
        f"from pathlib import Path\n\n"
        f"# 允许在 Jupyter 已有事件循环内安全调用 asyncio.run()\n"
        f"try:\n"
        f"    import nest_asyncio\n"
        f"    nest_asyncio.apply()\n"
        f"except ImportError:\n"
        f"    pass\n\n"
        f"PROJECT_ROOT = Path.cwd()\n"
        f"while PROJECT_ROOT != PROJECT_ROOT.parent and not (PROJECT_ROOT / 'versions').exists():\n"
        f"    PROJECT_ROOT = PROJECT_ROOT.parent\n\n"
        f"DAY_DIR = PROJECT_ROOT / 'versions' / 'day{day:02d}'\n"
        f"for _p in (DAY_DIR, DAY_DIR / 'src', PROJECT_ROOT):\n"
        f"    if _p.exists() and str(_p) not in sys.path:\n"
        f"        sys.path.insert(0, str(_p))\n"
        f"os.chdir(DAY_DIR)\n"
        f"__file__ = str(DAY_DIR / 'src' / 'notebook_entry.py')\n\n"
        f"print(f'✅ Python 版本: {{sys.version.split()[0]}}')\n"
        f"print(f'✅ 项目根目录: {{PROJECT_ROOT}}')\n"
        f"print(f'✅ 当日版本目录: {{DAY_DIR}}')\n"
    ))

    # 3. 企业 PRD 与课堂核心笔记
    prd = day_spec["business_prd"]
    goals_md = "\n".join(f"- {g}" for g in prd.get("goals", []))
    ac_md = "\n".join(f"- {a}" for a in prd.get("acceptance_criteria", []))
    notes_md = "\n\n".join(
        f"### {i}. {n['heading']}\n\n{n['content']}\n\n> **⚠️ 老陈避坑**：{n.get('pitfalls', '')}"
        for i, n in enumerate(day_spec["knowledge_notes"], 1)
    )
    cells.append(new_markdown_cell(
        f"## 📋 企业需求背景与验收目标（{day_spec['gitlab_ticket']}）\n\n"
        f"{prd.get('background', '')}\n\n"
        f"**今日迭代目标：**\n{goals_md}\n\n"
        f"**验收标准：**\n{ac_md}\n\n"
        f"---\n\n"
        f"## 📚 课堂核心技术笔记\n\n{notes_md}\n"
    ))

    # 4. 逐个代码实操步骤（Markdown 旁白 + 可运行 Code Cell + 深度解析）
    for idx, step in enumerate(day_spec["code_steps"], 1):
        cells.append(new_markdown_cell(
            f"## 💻 实操步骤 {idx}：{step['step_title']}\n\n"
            f"- **目标文件**：`versions/day{day:02d}/{step['file_path']}`\n"
            f"- **老陈代码旁白**：{step['narration']}\n"
        ))
        cells.append(new_code_cell(step["code"]))
        cells.append(new_markdown_cell(
            f"### 🔍 步骤 {idx} 代码深度解析\n\n"
            f"{step['explanation']}\n\n"
            f"**预期运行输出参考：**\n```text\n{step['expected_output']}\n```\n"
        ))

    # 5. 单元测试验证说明
    cells.append(new_markdown_cell(
        f"## 🧪 当日自动化单元测试\n\n"
        f"在终端运行 `pytest versions/day{day:02d}/tests/test_day{day:02d}.py -v` 即可验收全部测试断言。"
        f"下面展示完整测试脚本源码，供对照学习测试写法：\n\n"
        f"```python\n{day_spec['unit_test_code']}\n```\n"
    ))

    # 6. 课后作业与参考答案（可独立运行）
    cells.append(new_markdown_cell(
        f"## 📝 课后梯度实战作业与标准答案\n\n"
        f"建议先在下方新建空白单元格独立完成编码，运行通过后再核对参考答案。\n"
    ))
    for idx, hw in enumerate(day_spec["homeworks"], 1):
        cells.append(new_markdown_cell(
            f"### 作业 {idx}（{hw['difficulty']}）：{hw['title']}\n\n"
            f"**题目要求：**\n{hw['requirement']}\n\n"
            f"**思路提示：** {hw['hint']}\n"
        ))
        cells.append(new_code_cell(hw["solution_code"]))
        cells.append(new_markdown_cell(
            f"**答案解析与评分标准：**\n\n{hw['solution_analysis']}\n"
        ))

    # 7. 老陈收尾旁白
    cells.append(new_markdown_cell(
        f"---\n\n## 🎯 老陈收尾复盘\n\n{day_spec['narrator_closing']}\n"
    ))

    nb = new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11",
            },
        },
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        nbformat.write(nb, f)
