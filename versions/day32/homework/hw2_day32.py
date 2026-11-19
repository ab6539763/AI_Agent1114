"""
Day 32 课后作业 2（企业实战）：作业二：实现基于多轮历史的指代消解改写器（CoreferenceRewriter）
工单：STARMIND-032
"""

"""Day 32 作业二参考答案：多轮对话指代消解查询改写器"""
from typing import List


def rewrite_with_history(history_questions: List[str], current_query: str) -> str:
    if not history_questions:
        return current_query
    last_q = history_questions[-1]
    pronouns = ("它", "这个", "那个", "该制度", "这项")
    if any(p in current_query for p in pronouns) or (current_query.startswith("那") and len(current_query) <= 8):
        # 提取上一轮的核心主题词作为上下文锚点
        topic = last_q.replace("请问", "").replace("？", "").replace("?", "")[:14]
        resolved = current_query
        for p in pronouns:
            resolved = resolved.replace(p, f"「{topic}」")
        if resolved == current_query:
            resolved = f"结合前文「{topic}」，{current_query}"
        return resolved
    return current_query


if __name__ == "__main__":
    hist = ["杭州星辰数科年假有几天？"]
    r1 = rewrite_with_history(hist, "它需要提前几天申请？")
    r2 = rewrite_with_history(hist, "那病假呢？")
    print("改写1:", r1)
    print("改写2:", r2)
    assert "年假" in r1 and "年假" in r2

