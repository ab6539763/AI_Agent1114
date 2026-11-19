import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 58 单元测试：选题矩阵与架构评审门禁"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day58_arch_review import REQUIRED_SUBSYSTEMS, ArchProposal, review_architecture
from src.day58_topic_matrix import TOPICS_8, rank_capstone_topics


def test_eight_topics_ranked_with_starmind_first():
    assert len(TOPICS_8) == 8
    ranked = rank_capstone_topics()
    assert ranked[0][0].code == "T1"
    assert ranked[0][1] >= 9.0


def test_arch_review_approves_complete_proposal():
    prop = ArchProposal(
        "StarMind", "v1.0", set(REQUIRED_SUBSYSTEMS), 1200.0, 0.9, True, True,
        {d: f"Day {d}" for d in range(59, 65)},
    )
    res = review_architecture(prop)
    assert res["approved"] is True
    assert res["blocker_count"] == 0


def test_arch_review_rejects_incomplete_proposal():
    prop = ArchProposal("Demo", "v0.1", {"hybrid_rag"}, 3000.0, 0.6, False, False, {59: "init"})
    res = review_architecture(prop)
    assert res["approved"] is False
    assert res["blocker_count"] >= 5

