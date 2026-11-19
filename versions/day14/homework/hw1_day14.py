"""
Day 14 课后作业 1（基础巩固）：基础巩固：为多轮对话增加 Markdown 导出器
工单：STARMIND-014
"""

"""Day 14 课后题 1：多轮对话记录 Markdown 导出器。"""

from typing import Dict, List


def export_messages_to_markdown(
    messages: List[Dict[str, str]],
    title: str = "星辰智脑对话记录",
) -> str:
    """将标准 messages 列表导出为易读的 Markdown 纪要文本。"""
    role_map = {"user": "用户", "assistant": "星辰智脑", "system": "系统人设"}
    blocks = [f"# {title}"]
    for idx, msg in enumerate(messages, 1):
        role_label = role_map.get(msg.get("role", ""), msg.get("role", "未知"))
        blocks.append(f"### {idx}. {role_label}\n\n{msg.get('content', '').strip()}")
    return "\n\n".join(blocks)


if __name__ == "__main__":
    sample = [
        {"role": "user", "content": "星辰智脑有哪些指令？"},
        {"role": "assistant", "content": "支持 /help、/clear、/save、/stats 和 /exit。"},
    ]
    print(export_messages_to_markdown(sample))

