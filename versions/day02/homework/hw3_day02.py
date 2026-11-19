"""
Day 02 课后作业 3（架构进阶）：架构进阶：带变量校验的安全 Prompt 渲染器
工单：STARMIND-002
"""

"""Day 2 课后题 3：防崩溃的 Prompt 模板安全渲染器。"""


class SafeDict(dict):
    """当模板缺少某个键时，保留原始占位符而不是抛出 KeyError。"""

    def __missing__(self, key: str) -> str:
        return f"<MISSING:{key}>"


def safe_render(template: str, variables: dict) -> str:
    """安全渲染模板，缺失字段自动标记为 <MISSING:key>。"""
    return template.format_map(SafeDict(variables))


if __name__ == "__main__":
    tpl = "你好 {user}，你的 {plan} 套餐剩余 {quota} Tokens。"
    print(safe_render(tpl, {"user": "陈小新", "plan": "企业版"}))

