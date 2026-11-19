import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 45 自动化单元测试：验证 Dify DSL 引擎分支执行、环路检测与选型矩阵。"""

import pytest
from src.day45_dify_dsl_runner import DifyDSLRunner, sample_ticket_triage_dsl
from src.day45_platform_selector import (
    ProjectRequirements,
    WEEK6_ANSWER_KEY,
    grade_week6_quiz,
    recommend_platform,
)


def test_dify_dsl_runner_branches_correctly():
    runner = DifyDSLRunner(sample_ticket_triage_dsl())

    p0 = runner.run({"priority": "P0", "query": "数据库连接池耗尽"})
    assert p0["outputs"]["level"] == "URGENT"
    assert "15 分钟内响应" in p0["outputs"]["reply"]

    p2 = runner.run({"priority": "P2", "query": "如何申请测试账号"})
    assert p2["outputs"]["level"] == "NORMAL"
    assert "4 个工作小时内响应" in p2["outputs"]["reply"]


def test_dify_dsl_detects_cycle():
    cyclic_dsl = {
        "nodes": [
            {"id": "start", "type": "start"},
            {"id": "a", "type": "llm", "prompt_template": "hi"},
            {"id": "end", "type": "end", "outputs": {}},
        ],
        "edges": [
            {"source": "start", "target": "a"},
            {"source": "a", "target": "start"},
            {"source": "a", "target": "end"},
        ],
    }
    runner = DifyDSLRunner(cyclic_dsl)
    with pytest.raises(ValueError, match="循环依赖"):
        runner.validate_dsl()


def test_platform_selector_and_week6_quiz():
    ops_req = ProjectRequirements(
        private_deployment_required=True,
        has_complex_cycles_or_hitl=False,
        need_strict_rbac_and_ci=False,
        delivery_days=2,
        maintainer_is_non_dev=True,
    )
    assert recommend_platform(ops_req)["recommended"] == "Dify"

    core_req = ProjectRequirements(
        private_deployment_required=True,
        has_complex_cycles_or_hitl=True,
        need_strict_rbac_and_ci=True,
        delivery_days=14,
        maintainer_is_non_dev=False,
    )
    assert recommend_platform(core_req)["recommended"] == "LangGraph"

    full_score = grade_week6_quiz(WEEK6_ANSWER_KEY)
    assert full_score["score"] == 100 and full_score["passed"] is True

