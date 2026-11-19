"""
星辰智脑 (StarMind) 70 天课程与企业级 Agent 平台全链路自动化验收工具。
支持检查：
1. 结构完整性（70 天 HTML5 课件、Notebook、版本快照、每日 PRD、里程碑、面试题库）
2. 每日 HTML5 课件可见字数 >= 20,000 字校验
3. 全仓库累计代码行数 >= 100,000 行校验
4. 全量 70 个版本单元测试 + 企业级平台单元测试 (pytest)
5. Jupyter Notebook 真实内核执行校验 (nbclient)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def strip_html_visible_text(html: str) -> str:
    cleaned = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    cleaned = re.sub(r"<style[\s\S]*?</style>", "", cleaned, flags=re.I)
    cleaned = re.sub(r"<svg[\s\S]*?</svg>", "", cleaned, flags=re.I)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned


def check_courseware_and_structure():
    print("\n=== [1/5] 校验 70 天文件完整性与 HTML5 课件字数 ===")
    missing = []
    under_target = []
    char_stats = []
    for day in range(1, 71):
        cw = ROOT / "courseware" / f"day{day:02d}" / "index.html"
        nb = ROOT / "notebooks" / f"day{day:02d}" / f"day{day:02d}_practice.ipynb"
        ver = ROOT / "versions" / f"day{day:02d}" / "tests" / f"test_day{day:02d}.py"
        doc = ROOT / "docs" / "daily" / f"day{day:02d}_gitlab_prd.md"
        for p in (cw, nb, ver, doc):
            if not p.exists():
                missing.append(str(p.relative_to(ROOT)))
        if cw.exists():
            vis_len = len(strip_html_visible_text(cw.read_text(encoding="utf-8")))
            char_stats.append((day, vis_len))
            if vis_len < 20000:
                under_target.append((day, vis_len))

    if missing:
        print(f"❌ 缺失文件 ({len(missing)}): {missing[:10]}")
        return False
    min_d, min_c = min(char_stats, key=lambda x: x[1])
    max_d, max_c = max(char_stats, key=lambda x: x[1])
    total_c = sum(c for _, c in char_stats)
    print(f"✅ 70 天四件套（HTML5课件/Notebook/版本快照/PRD文档）100% 齐全")
    print(f"📊 课件可见字数统计：最低 Day {min_d:02d} = {min_c:,} 字 | 最高 Day {max_d:02d} = {max_c:,} 字 | 总计 = {total_c:,} 字")
    if under_target:
        print(f"❌ 以下天数课件不足 20,000 字: {under_target[:10]}")
        return False
    print("✅ 全部 70 天 HTML5 课件均 >= 20,000 可见字数！")
    return True


def check_code_lines():
    print("\n=== [2/5] 统计全仓库累计代码行数 ===")
    exts = {".py", ".js", ".css", ".yml", ".yaml", ".sql"}
    names = {"Dockerfile", "Makefile"}
    total = 0
    by_dir = {}
    for path in ROOT.rglob("*"):
        if any(p in path.parts for p in (".venv", ".git", "__pycache__", ".pytest_cache")):
            continue
        if not path.is_file():
            continue
        lines = 0
        if path.suffix in exts or path.name in names:
            lines = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        elif path.suffix == ".ipynb":
            try:
                nb = json.loads(path.read_text(encoding="utf-8"))
                for c in nb.get("cells", []):
                    if c.get("cell_type") == "code":
                        src = c.get("source", [])
                        lines += len(src) if isinstance(src, list) else len(str(src).splitlines())
            except Exception:
                pass
        if lines:
            total += lines
            top = path.relative_to(ROOT).parts[0]
            by_dir[top] = by_dir.get(top, 0) + lines

    for k, v in sorted(by_dir.items(), key=lambda x: -x[1]):
        print(f"  - {k:20s}: {v:>10,} 行")
    print(f"📊 全仓库累计代码行数：{total:,} 行")
    if total < 100000:
        print("❌ 累计代码量未达到 100,000 行要求")
        return False
    print("✅ 累计代码量已达标 (>= 100,000 行)！")
    return True


def check_platform_tests():
    print("\n=== [3/5] 运行企业级平台 (starmind_platform) 全链路测试 ===")
    pytest_bin = ROOT / ".venv" / "bin" / "pytest"
    res = subprocess.run(
        [str(pytest_bin), str(ROOT / "starmind_platform" / "tests"), "-v"],
        cwd=str(ROOT),
    )
    return res.returncode == 0


def check_all_versions():
    print("\n=== [4/5] 逐日运行 70 天版本迭代单元测试 ===")
    pytest_bin = ROOT / ".venv" / "bin" / "pytest"
    failed = []
    for day in range(1, 71):
        test_file = ROOT / "versions" / f"day{day:02d}" / "tests" / f"test_day{day:02d}.py"
        res = subprocess.run(
            [str(pytest_bin), str(test_file), "-q"],
            cwd=str(ROOT / "versions" / f"day{day:02d}"),
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            failed.append((day, res.stdout + "\n" + res.stderr))
            print(f"  ❌ Day {day:02d} 测试失败")
    if failed:
        for d, err in failed[:5]:
            print(f"\n--- Day {d:02d} 失败详情 ---\n{err[:1000]}")
        print(f"❌ 共 {len(failed)} 天单元测试失败")
        return False
    print("✅ 全部 70 天版本单元测试 70/70 100% 通过！")
    return True


def check_notebooks(sample_only: bool = False):
    print("\n=== [5/5] 校验 Jupyter Notebook 可执行性 ===")
    import nbformat
    from nbclient import NotebookClient

    days = [1, 7, 14, 19, 24, 30, 36, 41, 47, 53, 60, 70] if sample_only else list(range(1, 71))
    failed = []
    for day in days:
        nb_path = ROOT / "notebooks" / f"day{day:02d}" / f"day{day:02d}_practice.ipynb"
        try:
            nb = nbformat.read(nb_path, as_version=4)
            client = NotebookClient(nb, timeout=30, kernel_name="python3")
            client.execute()
        except Exception as exc:
            failed.append((day, str(exc)))
            print(f"  ❌ Day {day:02d} Notebook 执行失败: {exc}")
    if failed:
        print(f"❌ 共 {len(failed)} 份 Notebook 执行失败")
        return False
    print(f"✅ 校验通过：{len(days)}/{len(days)} 份 Jupyter Notebook 全部无报错执行成功！")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check-versions", action="store_true")
    parser.add_argument("--check-notebooks", action="store_true")
    parser.add_argument("--sample-notebooks", action="store_true")
    args = parser.parse_args()

    ok = True
    if args.all or not any([args.check_versions, args.check_notebooks]):
        ok = check_courseware_and_structure() and ok
        ok = check_code_lines() and ok
        ok = check_platform_tests() and ok
        ok = check_all_versions() and ok
        ok = check_notebooks(sample_only=args.sample_notebooks) and ok
    else:
        if args.check_versions:
            ok = check_all_versions() and ok
        if args.check_notebooks:
            ok = check_notebooks(sample_only=args.sample_notebooks) and ok

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
