import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 42 自动化单元测试：验证 SQLite 跨实例断点续跑、节点重试与并行写作 Agent。"""

from pathlib import Path
import pytest
from src.day42_checkpoint_hitl import (
    PersistentGraph,
    RetryPolicy,
    SQLiteCheckpointer,
    START,
    END,
)
from src.day42_parallel_writer import ParallelProposalWriterAgent


def test_sqlite_checkpointer_hitl_across_instances(tmp_path: Path):
    db_file = tmp_path / "starmind_ckpt.db"
    # 实例 1：执行到 publish 前中断落库
    ckpt1 = SQLiteCheckpointer(db_file)
    g1 = PersistentGraph(checkpointer=ckpt1, interrupt_before=["publish"])
    g1.add_node("draft", lambda s: {"draft_text": f"方案:{s['topic']}"})
    g1.add_node("publish", lambda s: {"published": True, "approver": s["approver"]})
    g1.add_edge(START, "draft")
    g1.add_edge("draft", "publish")
    g1.add_edge("publish", END)

    res1 = g1.run("thread-99", {"topic": "金融风控Agent"})
    assert res1["status"] == "INTERRUPTED"
    assert res1["waiting_node"] == "publish"
    ckpt1.close()

    # 实例 2：模拟服务重启后重新打开同一个 SQLite 文件并恢复执行
    ckpt2 = SQLiteCheckpointer(db_file)
    g2 = PersistentGraph(checkpointer=ckpt2, interrupt_before=["publish"])
    g2.add_node("draft", lambda s: {"draft_text": f"方案:{s['topic']}"})
    g2.add_node("publish", lambda s: {"published": True, "approver": s["approver"]})
    g2.add_edge(START, "draft")
    g2.add_edge("draft", "publish")
    g2.add_edge("publish", END)

    res2 = g2.resume("thread-99", human_patch={"approver": "老陈"})
    assert res2["status"] == "COMPLETED"
    assert res2["state"]["published"] is True
    assert res2["state"]["approver"] == "老陈"
    assert len(ckpt2.get_history("thread-99")) >= 3
    ckpt2.close()


def test_node_retry_policy_recovers_transient_error():
    attempts = {"count": 0}

    def flaky_api_node(_state):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ConnectionError("模拟临时 502 抖动")
        return {"ok": True}

    ckpt = SQLiteCheckpointer(":memory:")
    g = PersistentGraph(checkpointer=ckpt)
    g.add_node("flaky", flaky_api_node, retry_policy=RetryPolicy(max_attempts=3, initial_delay_sec=0.001))
    g.add_edge(START, "flaky")
    g.add_edge("flaky", END)

    res = g.run("retry-1", {})
    assert res["status"] == "COMPLETED"
    assert res["state"]["ok"] is True
    assert attempts["count"] == 3
    ckpt.close()


def test_parallel_writer_order_and_speedup():
    writer = ParallelProposalWriterAgent(max_workers=3, simulated_io_sec=0.04)
    out = writer.run("星辰政企知识库")
    assert out["chapter_count"] == 3
    assert out["all_passed_qa"] is True
    assert out["ordered_titles"] == [
        "一、项目背景与痛点分析",
        "二、核心系统架构与技术选型",
        "三、安全合规与交付验收计划",
    ]
    # 3 章各 40ms 并行总耗时应显著低于串行 120ms
    assert out["elapsed_ms"] < 115

