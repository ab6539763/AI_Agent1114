"""
Day 26 课后作业 3（架构进阶）：作业三：实现带自动重试修复的 OutputFixingParser
工单：STARMIND-026
"""

"""Day 26 作业三参考答案：结构化输出自愈解析器 OutputFixingParser"""
import json
import sys
from pathlib import Path
from typing import Callable, Generic, TypeVar

from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day26_lcel_core import Runnable
from src.day26_parsers_and_chain import OutputParserException, PydanticOutputParser

T = TypeVar("T", bound=BaseModel)


class TicketSchema(BaseModel):
    category: str
    priority: int


class OutputFixingParser(Runnable[str, T], Generic[T]):
    def __init__(
        self,
        parser: PydanticOutputParser[T],
        fixer_fn: Callable[[str, str], str],
        max_retries: int = 2,
    ) -> None:
        self.parser = parser
        self.fixer_fn = fixer_fn
        self.max_retries = max_retries

    def invoke(self, input_data: str) -> T:
        current = input_data
        for attempt in range(self.max_retries + 1):
            try:
                return self.parser.invoke(current)
            except OutputParserException as exc:
                if attempt == self.max_retries:
                    raise
                current = self.fixer_fn(exc.llm_output, str(exc))
        raise RuntimeError("unreachable")


if __name__ == "__main__":
    # 模拟大模型第一次返回了带单引号的非法 JSON，修复函数将其纠正
    def mock_fixer(bad_output: str, err: str) -> str:
        return json.dumps({"category": "网络故障", "priority": 1}, ensure_ascii=False)

    fixing = OutputFixingParser(PydanticOutputParser(TicketSchema), fixer_fn=mock_fixer)
    result = fixing.invoke("{'category': '网络故障', priority: P1}")
    print("自愈解析成功:", result.model_dump())
    assert result.priority == 1

