"""
Day 21 课后作业 2（企业实战）：会话导出为 Markdown 归档报告
工单：STARMIND-021
"""

from typing import Dict, List


def export_session_markdown(session_id: str, history: List[Dict[str, str]]) -> str:
    """将会话历史导出为可读 Markdown 文档。"""
    lines = [f"# 星辰智脑会话归档 `{session_id}`", ""]
    for msg in history:
        role = msg.get("role")
        if role == "system":
            continue
        title = "### 👤 用户" if role == "user" else "### 🤖 星辰智脑"
        lines.append(title)
        lines.append(msg.get("content", ""))
        lines.append("")
    return "\n".join(lines).strip()


if __name__ == "__main__":
    md = export_session_markdown("s01", [
        {"role": "system", "content": "hidden"},
        {"role": "user", "content": "杭州天气如何？"},
        {"role": "assistant", "content": "多云 19°C。"},
    ])
    print(md)

