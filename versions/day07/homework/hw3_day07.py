"""
Day 07 课后作业 3（架构进阶）：架构进阶：带备份快照的安全保存函数
工单：STARMIND-007
"""

"""Day 7 课后题 3：带自动备份快照的 JSON 安全落盘。"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any


def safe_save_with_backup(db_path: Path, data: Dict[str, Any]) -> Path:
    """若旧文件存在则先生成 .bak 备份，再写入最新 JSON 数据。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        backup_path = db_path.with_suffix(db_path.suffix + ".bak")
        backup_path.write_text(db_path.read_text(encoding="utf-8"), encoding="utf-8")
    with db_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return db_path


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "contacts.json"
        safe_save_with_backup(p, {"v": 1})
        safe_save_with_backup(p, {"v": 2})
        print("主文件:", p.read_text(encoding="utf-8").strip())
        print("备份文件存在:", p.with_suffix(".json.bak").exists())

