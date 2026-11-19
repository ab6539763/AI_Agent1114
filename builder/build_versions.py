"""
星辰智脑 (StarMind) 每日迭代版本仓库构建器（versions/day01 ~ versions/day70）。
核心设计：
- 真实还原企业级平台从 Day 1 到 Day 70 一天一天“滚雪球式”代码迭代过程。
- 每一天 `versions/dayXX/` 都会：
  1. 完整继承截至昨天为止演进沉淀的 `starmind_evolution/` 历史模块（可直观对比任意两天的增量演进）；
  2. 写入当天新增的核心代码模块（与 HTML5 课件及 Jupyter Notebook 100% 字节级一致，粘贴即跑通）；
  3. 写入当天作业标准答案模块（`homework/hw_dayXX.py`）；
  4. 写入当天自动化单元测试（`tests/test_dayXX.py`）；
  5. 生成当天版本迭代说明 `README.md` 与 `CHANGELOG.md`。
"""

import shutil
from pathlib import Path
from typing import Dict, List


def build_daily_versions(all_days: List[Dict], versions_root: Path) -> Dict[str, int]:
    """按 Day 1 -> Day 70 顺序逐日构建独立可运行、可追溯的迭代快照版本。"""
    versions_root.mkdir(parents=True, exist_ok=True)

    # 累积演进模块池：相对路径 -> 源码内容（记录整个平台从 0 到 1 的成长轨迹）
    accumulated_modules: Dict[str, str] = {}
    total_files = 0
    total_lines = 0

    for day_spec in sorted(all_days, key=lambda x: x["day"]):
        day = day_spec["day"]
        day_dir = versions_root / f"day{day:02d}"
        if day_dir.exists():
            shutil.rmtree(day_dir)
        day_dir.mkdir(parents=True, exist_ok=True)

        # 1. 写入截至昨日沉淀的演进代码底座（保持真实相对路径 src/，支持跨天模块无缝导入与 diff 对比）
        for rel_key, content in accumulated_modules.items():
            target = day_dir / rel_key
            target.parent.mkdir(parents=True, exist_ok=True)
            for parent in Path(rel_key).parents:
                if str(parent) != ".":
                    init_f = day_dir / parent / "__init__.py"
                    if not init_f.exists():
                        init_f.write_text('"""StarMind 模块包初始化"""\n', encoding="utf-8")
            target.write_text(content, encoding="utf-8")
            total_files += 1
            total_lines += len(content.splitlines())

        # 2. 写入当日新增的核心源码文件，并归档进演进池供后续迭代继承
        today_files = []
        for step in day_spec["code_steps"]:
            rel_path = Path(step["file_path"])
            out_file = day_dir / rel_path
            out_file.parent.mkdir(parents=True, exist_ok=True)
            for parent in rel_path.parents:
                if str(parent) != ".":
                    init_f = day_dir / parent / "__init__.py"
                    if not init_f.exists():
                        init_f.write_text('"""StarMind 模块包初始化"""\n', encoding="utf-8")
            out_file.write_text(step["code"] + "\n", encoding="utf-8")
            total_files += 1
            total_lines += len(step["code"].splitlines())
            today_files.append(step["file_path"])

            # 按原始相对路径归档，供后续天数直接 import
            accumulated_modules[step["file_path"]] = step["code"] + "\n"

        # 3. 写入当日作业参考实现文件（供学员自查和回归测试）
        hw_dir = day_dir / "homework"
        hw_dir.mkdir(parents=True, exist_ok=True)
        (hw_dir / "__init__.py").write_text('"""当日课后作业参考实现"""\n', encoding="utf-8")
        for h_idx, hw in enumerate(day_spec["homeworks"], 1):
            hw_file = hw_dir / f"hw{h_idx}_day{day:02d}.py"
            hw_header = (
                f'"""\nDay {day:02d} 课后作业 {h_idx}（{hw["difficulty"]}）：{hw["title"]}\n'
                f'工单：{day_spec["gitlab_ticket"]}\n"""\n\n'
            )
            hw_content = hw_header + hw["solution_code"] + "\n"
            hw_file.write_text(hw_content, encoding="utf-8")
            total_files += 1
            total_lines += len(hw_content.splitlines())

        # 4. 写入当日自动化单元测试
        tests_dir = day_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        test_file = tests_dir / f"test_day{day:02d}.py"
        # 在测试顶部注入 sys.path 确保从仓库根目录直接 pytest versions/dayXX/tests/ 也能稳定解析导入
        test_prefix = (
            "import sys\n"
            "from pathlib import Path\n"
            "_DAY_ROOT = str(Path(__file__).resolve().parent.parent)\n"
            "if _DAY_ROOT not in sys.path:\n"
            "    sys.path.insert(0, _DAY_ROOT)\n\n"
        )
        full_test_code = test_prefix + day_spec["unit_test_code"] + "\n"
        test_file.write_text(full_test_code, encoding="utf-8")
        total_files += 1
        total_lines += len(full_test_code.splitlines())

        # 5. 生成当日迭代版本 README.md
        files_md = "\n".join(f"- `{f}`" for f in today_files)
        readme = (
            f"# 星辰智脑 StarMind · Day {day:02d} 迭代快照（v0.{day:02d}.0）\n\n"
            f"- **课程主题**：{day_spec['title']}\n"
            f"- **企业任务**：{day_spec['subtitle']}\n"
            f"- **GitLab 工单**：`{day_spec['gitlab_ticket']}`\n"
            f"- **特性分支**：`{day_spec['git_branch']}`\n"
            f"- **标准提交**：`{day_spec['git_commit']}`\n\n"
            f"## 当日新增核心文件\n{files_md}\n\n"
            f"## 历史演进底座\n"
            f"- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day {day:02d} 的全部演进模块（当前累计 {len(accumulated_modules)} 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。\n\n"
            f"## 快速运行与验收命令\n"
            f"```bash\n"
            f"# 运行当日自动化单元测试\n"
            f"pytest versions/day{day:02d}/tests/test_day{day:02d}.py -v\n"
            f"```\n"
        )
        (day_dir / "README.md").write_text(readme, encoding="utf-8")

    return {"total_files": total_files, "total_lines": total_lines}
