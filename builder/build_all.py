"""
星辰智脑 (StarMind) 70 天课程与企业级 Agent 平台一键总构建脚本。
用法: python builder/build_all.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from builder.data.stage1_days01_14 import DAYS_STAGE_1
from builder.data.stage2_days15_24 import DAYS_STAGE_2
from builder.data.stage3_days25_38 import DAYS_STAGE_3
from builder.data.stage4_days39_50 import DAYS_STAGE_4
from builder.data.stage5_days51_57 import DAYS_STAGE_5
from builder.data.stage6_days58_70 import DAYS_STAGE_6

from builder.build_versions import build_daily_versions
from builder.render_notebooks import render_day_notebook
from builder.render_docs import render_daily_markdown_docs, render_milestone_docs
from builder.render_courseware import render_day_html, render_portal_html


def strip_html_visible_text(html: str) -> str:
    """剔除 script/style 和 HTML 标签，计算课件页面真实可见字符数。"""
    cleaned = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    cleaned = re.sub(r"<style[\s\S]*?</style>", "", cleaned, flags=re.I)
    cleaned = re.sub(r"<svg[\s\S]*?</svg>", "", cleaned, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned


def count_repo_code_lines(root: Path) -> int:
    """统计仓库中真实源码行数（.py / .html / .css / .js / .yml / .yaml / Dockerfile / Makefile）。"""
    exts = {".py", ".js", ".css", ".yml", ".yaml", ".sql"}
    names = {"Dockerfile", "Makefile"}
    total = 0
    for path in root.rglob("*"):
        if any(p in path.parts for p in (".venv", ".git", "__pycache__", ".pytest_cache")):
            continue
        if path.is_file():
            if path.suffix in exts or path.name in names:
                try:
                    total += len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
                except OSError:
                    pass
            elif path.suffix == ".ipynb":
                import json
                try:
                    nb = json.loads(path.read_text(encoding="utf-8"))
                    for c in nb.get("cells", []):
                        if c.get("cell_type") == "code":
                            src = c.get("source", [])
                            total += len(src) if isinstance(src, list) else len(str(src).splitlines())
                except Exception:
                    pass
    return total


def main():
    all_days = (
        list(DAYS_STAGE_1)
        + list(DAYS_STAGE_2)
        + list(DAYS_STAGE_3)
        + list(DAYS_STAGE_4)
        + list(DAYS_STAGE_5)
        + list(DAYS_STAGE_6)
    )
    all_days.sort(key=lambda x: x["day"])
    day_nums = [d["day"] for d in all_days]
    assert day_nums == list(range(1, 71)), f"天数不连续！当前: {len(day_nums)} 天"

    print(f"✅ 成功加载全部 {len(all_days)} 天课程蓝图 (Day 01 ~ Day 70)")

    # 1. 构建 70 天迭代版本快照
    ver_stats = build_daily_versions(all_days, ROOT / "versions")
    print(f"✅ 70 天版本迭代快照构建完成：共 {ver_stats['total_files']} 个源码/测试文件，累计 {ver_stats['total_lines']:,} 行")

    # 2. 生成 70 份 Jupyter Notebook
    for d in all_days:
        day = d["day"]
        nb_path = ROOT / "notebooks" / f"day{day:02d}" / f"day{day:02d}_practice.ipynb"
        render_day_notebook(d, nb_path)
    print("✅ 70 份 Jupyter Notebook 实操手册生成完成")

    # 3. 生成 Markdown 辅助文档
    render_daily_markdown_docs(all_days, ROOT / "docs")
    render_milestone_docs(ROOT / "docs")
    print("✅ 70 份每日 GitLab PRD 文档与 4 份企业里程碑报告生成完成")

    # 4. 渲染 70 份 HTML5 课件并统计可见字数
    char_counts = []
    for d in all_days:
        day = d["day"]
        html = render_day_html(d, total_days=70)
        out_html = ROOT / "courseware" / f"day{day:02d}" / "index.html"
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(html, encoding="utf-8")
        vis_len = len(strip_html_visible_text(html))
        char_counts.append((day, vis_len))

    min_day, min_chars = min(char_counts, key=lambda x: x[1])
    max_day, max_chars = max(char_counts, key=lambda x: x[1])
    avg_chars = sum(c for _, c in char_counts) // len(char_counts)
    print(
        f"✅ 70 份 HTML5 课件渲染完成：最短 Day {min_day:02d} ({min_chars:,} 字)，"
        f"最长 Day {max_day:02d} ({max_chars:,} 字)，平均 {avg_chars:,} 字/天"
    )

    # 5. 统计全仓库代码量并生成总门户 index.html
    total_code_lines = count_repo_code_lines(ROOT)
    portal_html = render_portal_html(
        all_days,
        stats={
            "total_code_lines": total_code_lines,
            "min_courseware_chars": min_chars,
        },
    )
    (ROOT / "index.html").write_text(portal_html, encoding="utf-8")
    print(f"✅ 总门户 index.html 生成完成，全仓库累计代码量：{total_code_lines:,} 行")


if __name__ == "__main__":
    main()
