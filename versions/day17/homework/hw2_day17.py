"""
Day 17 课后作业 2（企业实战）：动态 Few-Shot 检索选择器（按关键词匹配最相关示例）
工单：STARMIND-017
"""

from typing import List, Tuple


def select_relevant_examples(
    query: str,
    examples: List[Tuple[str, str]],
    top_k: int = 2,
) -> List[Tuple[str, str]]:
    """根据字符重合度动态筛选最相关的 Few-Shot 示例。"""
    q_chars = set(query)
    scored = sorted(
        examples,
        key=lambda item: len(q_chars & set(item[0])),
        reverse=True,
    )
    return scored[:top_k]


if __name__ == "__main__":
    pool = [
        ("怎么开增值税专票？", "billing"),
        ("支付接口返回502超时", "payment"),
        ("普通电子发票怎么重新下载？", "billing"),
    ]
    print(select_relevant_examples("我的电子专票下载不了", pool, top_k=2))

