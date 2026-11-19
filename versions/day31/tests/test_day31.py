import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 31 自动化单元测试：验证周测 100 分通关与消融实验框架指标计算准确。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day31_rag_ablation import render_markdown_report, run_ablation_suite
from src.day31_weekly_quiz import run_weekly_quiz


def test_weekly_quiz_all_pass():
    results = run_weekly_quiz()
    assert len(results) == 5
    assert all(r.passed for r in results)
    assert sum(r.score for r in results) == 100


def test_ablation_suite_metrics_and_report():
    suite = run_ablation_suite()
    assert len(suite) == 6
    by_name = {r.exp_name: r for r in suite}
    # 增强版 256d Embedding 的 MRR 应当显著高于或等于弱单字 64d 基线
    assert by_name["E3_中切片_140字"].mrr >= by_name["E1_基线单字_64d"].mrr
    assert by_name["E3_中切片_140字"].hit_at_k >= 0.85

    md = render_markdown_report(suite)
    assert "推荐线上配置" in md
    assert "| 实验组 |" in md

