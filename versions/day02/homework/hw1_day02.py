"""
Day 02 课后作业 1（基础巩固）：基础巩固：商品标题去噪与截断
工单：STARMIND-002
"""

"""Day 2 课后题 1：商品标题清洗与截断。"""


def normalize_title(title: str, limit: int = 20) -> str:
    """移除营销标签、压缩空白并按字数限制截断标题。"""
    cleaned = title.replace("【爆款】", "").replace("[限时]", "")
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > limit:
        return cleaned[: max(0, limit - 3)] + "..."
    return cleaned


if __name__ == "__main__":
    raw = "  【爆款】  [限时]  星辰智脑   企业级AI知识库私有化部署套件  "
    print(normalize_title(raw, limit=16))

