"""
Day 14 课后作业 2（企业实战）：企业实战：本地多会话存档管理器
工单：STARMIND-014
"""

"""Day 14 课后题 2：多会话 JSON 存档扫描与容错摘要器。"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List


def list_saved_sessions(save_dir: Path) -> List[Dict[str, Any]]:
    """扫描会话目录，返回所有 JSON 存档的摘要信息（损坏文件安全标记不崩溃）。"""
    if not save_dir.exists():
        return []
    summaries: List[Dict[str, Any]] = []
    for path in sorted(save_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            summaries.append({
                "file_name": path.name,
                "session_id": str(data.get("session_id", "unknown")),
                "message_count": len(data.get("messages", [])),
            })
        except (json.JSONDecodeError, OSError, TypeError):
            summaries.append({
                "file_name": path.name,
                "session_id": "CORRUPTED",
                "message_count": 0,
            })
    return summaries


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "s1.json").write_text(json.dumps({"session_id": "hr-qa", "messages": [{"role": "user", "content": "hi"}]}), encoding="utf-8")
        (root / "bad.json").write_text("{broken", encoding="utf-8")
        print(list_saved_sessions(root))

