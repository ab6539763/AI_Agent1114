"""
Day 10 课后作业 3（架构进阶）：架构进阶：自定义上下文超长异常与自动截断恢复
工单：STARMIND-010
"""

"""Day 10 课后题 3：上下文超长自愈恢复机制。"""


class ContextOverflowError(Exception):
    def __init__(self, max_chars: int) -> None:
        super().__init__(f"上下文超过最大长度 {max_chars}")
        self.max_chars = max_chars


def invoke_with_auto_truncate(model_fn, prompt: str) -> str:
    try:
        return model_fn(prompt)
    except ContextOverflowError as exc:
        trimmed = prompt[: exc.max_chars]
        return model_fn(trimmed)


if __name__ == "__main__":
    def strict_model(text: str) -> str:
        if len(text) > 10:
            raise ContextOverflowError(max_chars=10)
        return f"OK({text})"

    print(invoke_with_auto_truncate(strict_model, "这是一段超过十个字符的长提问文本"))

