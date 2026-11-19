import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 66 单元测试：STAR 简历体检 Linter 与 GitHub 作品集生成器"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day66_star_resume_builder import StarEntry, lint_resume_bullet
from src.day66_portfolio_generator import ProjectPortfolioSpec, generate_github_readme


def test_star_builder_and_high_score_lint():
    entry = StarEntry(
        situation_task="企业知识库召回漏检且高频问答 Token 成本高的问题",
        action="主导设计 BM25+RRF+Rerank 混合检索与 FastAPI SSE 流式网关，引入 Ragas 评测与缓存路由",
        result="将召回率从 65% 提升至 91%，P95 延迟压至 180ms，月度 Token 成本降低 52%",
    )
    res = lint_resume_bullet(entry.render())
    assert res["grade"] == "EXCELLENT"
    assert res["score"] >= 85
    assert len(res["matched_keywords"]) >= 4


def test_weak_bullet_flagged_needs_rewrite():
    res = lint_resume_bullet("负责参与了公司的智能问答模块开发，使用了 Python。")
    assert res["grade"] == "NEEDS_REWRITE"
    assert len(res["suggestions"]) >= 3


def test_github_readme_contains_benchmarks_and_quickstart():
    md = generate_github_readme(
        ProjectPortfolioSpec(
            project_name="StarMind",
            tagline="企业级 AI Agent 平台",
            tech_stack=["FastAPI", "RAG"],
            highlights=["混合检索溯源"],
            benchmarks={"Faithfulness": "92%"},
            quickstart_cmd="pytest -q",
        )
    )
    assert "# StarMind" in md
    assert "| Faithfulness | 92% |" in md
    assert "pytest -q" in md

