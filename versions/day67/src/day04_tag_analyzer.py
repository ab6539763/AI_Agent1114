"""
STARMIND-004 模块二：知识库文档标签去重与集合差异分析器。
演示 set 创建、去重清洗、交集(&)/并集(|)/差集(-)与排序输出。
"""

from typing import List, Dict, Set


def normalize_tags(raw_tags: List[str]) -> Set[str]:
    """清洗并去重标签：去首尾空格、转小写、过滤空串。"""
    # 使用集合推导式一步完成清洗与去重
    return {tag.strip().lower() for tag in raw_tags if tag and tag.strip()}


def compare_tag_versions(old_tags: List[str], new_tags: List[str]) -> Dict[str, List[str]]:
    """
    对比旧版与新版知识库标签，返回确定顺序（已排序）的差异报告：
    - common: 两版共同保留的标签
    - added: 新版新增的标签
    - removed: 新版移除的标签
    - all_unique: 两版合并后的全部唯一标签
    """
    set_old = normalize_tags(old_tags)
    set_new = normalize_tags(new_tags)

    return {
        "common": sorted(set_old & set_new),
        "added": sorted(set_new - set_old),
        "removed": sorted(set_old - set_new),
        "all_unique": sorted(set_old | set_new),
    }


if __name__ == "__main__":
    v1_tags = [" Python ", "Prompt", "git", "python", ""]
    v2_tags = ["python", "RAG", "Agent", "Prompt ", "RAG"]
    diff = compare_tag_versions(v1_tags, v2_tags)
    for k, v in diff.items():
        print(f"{k:12s}: {v}")

