"""
STARMIND-002 模块一：企业客服工单文本清洗器。
演示字符串不可变性、核心方法（replace/split/join/upper）、切片截断与成员运算符。
"""

# 定义常见的违禁/高风险测试词（演示成员运算符 in）
BLOCKED_KEYWORDS = ("刷单", "代开发票", "木马链接")


def clean_ticket_text(raw_text: str, max_length: int = 200) -> str:
    """
    清洗客服工单原始文本：
    1. 将中文全角空格（\\u3000）替换为普通空格；
    2. 利用 split() + join() 折叠所有连续空格、制表符和多余换行；
    3. 统一把小写订单前缀 'ord-' 标准化为 'ORD-'；
    4. 若超过 max_length，使用切片截断并追加省略号。
    """
    # 防御 None 或空字符串输入
    if not raw_text:
        return ""

    # 第 1 步：替换全角空格与不间断空格
    normalized = raw_text.replace("\u3000", " ").replace("\xa0", " ")

    # 第 2 步：split() 不传参会按任意连续空白切分，再用单个空格拼回
    compact = " ".join(normalized.split())

    # 第 3 步：标准化常见小写订单号前缀
    standardized = compact.replace("ord-", "ORD-").replace("Ord-", "ORD-")

    # 第 4 步：使用切片进行长度控制，防止超长文本打爆 Token 预算
    if len(standardized) > max_length:
        # 预留 3 个字符给 '...'
        cutoff = max(0, max_length - 3)
        return standardized[:cutoff] + "..."

    return standardized


def has_blocked_content(text: str) -> bool:
    """检查清洗后的文本是否命中风险关键词。"""
    # 使用成员运算符 in 结合 any 表达式判断
    return any(keyword in text for keyword in BLOCKED_KEYWORDS)


if __name__ == "__main__":
    dirty = "  \u3000你好！！\n\n  我的订单  ord-20260501   一直没发货，   麻烦查一下\t谢谢！  "
    cleaned = clean_ticket_text(dirty, max_length=60)
    print(f"原始长度: {len(dirty)} -> 清洗后长度: {len(cleaned)}")
    print(f"清洗结果: {cleaned}")
    print(f"风险拦截: {has_blocked_content(cleaned)}")

