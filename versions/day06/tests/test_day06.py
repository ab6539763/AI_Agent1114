import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-006 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day06_text_pipeline import strip_and_collapse, redact_secret_key, run_pipeline, build_chat_request
from day06_kb_tree import flatten_kb_tree, top_largest_docs


def test_text_pipeline_and_request_builder():
    out = run_pipeline("  key= sk-abc123  hello  ", strip_and_collapse, redact_secret_key)
    assert out == "key= sk-***REDACTED*** hello"

    req1 = build_chat_request("qwen-plus", "你好", temperature=0.5, seed=None)
    req2 = build_chat_request("qwen-plus", "第二条")
    assert len(req1["messages"]) == 1
    assert len(req2["messages"]) == 1  # 确保两次调用消息列表完全隔离
    assert "seed" not in req1
    assert req1["temperature"] == 0.5


def test_kb_tree_recursion_and_ranking():
    tree = {
        "type": "dir",
        "name": "root",
        "children": [
            {"type": "file", "name": "a.md", "size_kb": 10},
            {
                "type": "dir",
                "name": "sub",
                "children": [
                    {"type": "file", "name": "b.md", "size_kb": 50},
                    {"type": "file", "name": "c.md", "size_kb": 50},
                ],
            },
        ],
    }
    flat = flatten_kb_tree(tree)
    assert len(flat) == 3
    top2 = top_largest_docs(tree, top_n=2)
    assert [d["path"] for d in top2] == ["root/sub/b.md", "root/sub/c.md"]

    with pytest.raises(RecursionError):
        flatten_kb_tree(tree, max_depth=0)

