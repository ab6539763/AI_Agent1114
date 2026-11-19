"""
Day 37 课后作业 3（架构进阶）：作业三：实现前端引用角标 `[1][2]` 自动校验与死链清理器
工单：STARMIND-037
"""

"""Day 37 作业三参考答案：大模型幽灵引用角标校验与清理器"""
import re


def sanitize_citation_markers(answer: str, max_index: int) -> str:
    def _repl(match: re.Match) -> str:
        idx = int(match.group(1))
        return match.group(0) if 1 <= idx <= max_index else ""

    return re.sub(r"\[(\d+)\]", _repl, answer)


if __name__ == "__main__":
    raw = "北京住宿上限600元[1]，餐补100元[2]，且周末发红包[5][0]。"
    clean = sanitize_citation_markers(raw, max_index=2)
    print("清理后:", clean)
    assert "[1]" in clean and "[2]" in clean
    assert "[5]" not in clean and "[0]" not in clean

