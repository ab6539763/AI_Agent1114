"""
Day 26 - 步骤二：OutputParser 体系与「翻译 -> 润色 -> 摘要」三级 LCEL 流水线
对应生产包：langchain_core.output_parsers
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Generic, List, Type, TypeVar

from pydantic import BaseModel, Field, ValidationError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import AIMessage, BaseChatModel, BaseMessage, StarMindChatModel
from src.day25_prompt_template import ChatPromptTemplate
from src.day26_lcel_core import Runnable, RunnableParallel, RunnablePassthrough

TModel = TypeVar("TModel", bound=BaseModel)


class OutputParserException(ValueError):
    """结构化输出解析失败异常，保留大模型原始回复方便告警与重试。"""

    def __init__(self, message: str, llm_output: str) -> None:
        super().__init__(message)
        self.llm_output = llm_output


class RunnablePrompt(Runnable[Dict[str, Any], List[BaseMessage]]):
    """将 Day 25 的 ChatPromptTemplate 适配为 LCEL Runnable。"""

    def __init__(self, prompt: ChatPromptTemplate) -> None:
        self.prompt = prompt

    def invoke(self, input_data: Dict[str, Any]) -> List[BaseMessage]:
        return self.prompt.format_messages(**input_data)


class RunnableChatModel(Runnable[List[BaseMessage], AIMessage]):
    """将 Day 25 的 BaseChatModel 适配为 LCEL Runnable。"""

    def __init__(self, model: BaseChatModel) -> None:
        self.model = model

    def invoke(self, input_data: List[BaseMessage]) -> AIMessage:
        return self.model.invoke(input_data)


class StrOutputParser(Runnable[AIMessage | str, str]):
    """提取 AIMessage 正文文本。"""

    def invoke(self, input_data: AIMessage | str) -> str:
        return input_data.content if isinstance(input_data, AIMessage) else str(input_data)


class JsonOutputParser(Runnable[AIMessage | str, Dict[str, Any]]):
    """容错 JSON 解析器：自动剥离 Markdown ```json 代码块与前后冗余文本。"""

    FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)

    def invoke(self, input_data: AIMessage | str) -> Dict[str, Any]:
        raw = input_data.content if isinstance(input_data, AIMessage) else str(input_data)
        match = self.FENCE_RE.search(raw)
        candidate = match.group(1) if match else raw.strip()
        if not candidate.startswith("{"):
            start, end = candidate.find("{"), candidate.rfind("}")
            if start != -1 and end != -1 and end > start:
                candidate = candidate[start : end + 1]
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise OutputParserException(f"JSON 解析失败: {exc}", llm_output=raw) from exc
        if not isinstance(data, dict):
            raise OutputParserException("期望 JSON 对象(dict)，但解析结果非字典", llm_output=raw)
        return data


class PydanticOutputParser(Runnable[AIMessage | str, TModel], Generic[TModel]):
    """强类型 Pydantic 解析器：自动生成 Schema 指令并校验返回对象。"""

    def __init__(self, pydantic_object: Type[TModel]) -> None:
        self.pydantic_object = pydantic_object
        self._json_parser = JsonOutputParser()

    def get_format_instructions(self) -> str:
        schema = json.dumps(self.pydantic_object.model_json_schema(), ensure_ascii=False)
        return f"请严格按照以下 JSON Schema 输出纯 JSON，不要添加多余解释：{schema}"

    def invoke(self, input_data: AIMessage | str) -> TModel:
        raw = input_data.content if isinstance(input_data, AIMessage) else str(input_data)
        data = self._json_parser.invoke(raw)
        try:
            return self.pydantic_object.model_validate(data)
        except ValidationError as exc:
            raise OutputParserException(f"Pydantic 字段校验失败: {exc}", llm_output=raw) from exc


class DocQualityReport(BaseModel):
    """海外技术文档结构化质检报告 Schema。"""

    executive_summary: str = Field(description="一句话高管摘要")
    keywords: List[str] = Field(min_length=1, description="核心英文关键词")
    tone: str = Field(description="语调评估，如 Professional / Formal")
    word_count: int = Field(gt=0, description="润色后英文词数")


def _enterprise_doc_handler(messages: List[BaseMessage]) -> str:
    """模拟支持翻译/润色/摘要/结构化分析的多任务大模型后端。"""
    sys_msg = messages[0].content
    user_msg = messages[-1].content

    if "【任务：翻译】" in sys_msg:
        if "知识库" in user_msg:
            return "StarMind Knowledge Base 2.0 supports hybrid retrieval and millisecond response."
        return f"Translated English draft: {user_msg}"

    if "【任务：润色】" in sys_msg:
        return (
            "StarMind Enterprise Knowledge Base v2.0 delivers hybrid semantic-lexical retrieval "
            "with sub-second latency for global teams."
        )

    if "【任务：摘要】" in sys_msg:
        return "StarMind KB v2.0 upgrades enterprise search with hybrid retrieval and sub-second latency."

    if "【任务：质检JSON】" in sys_msg:
        # 故意包裹 Markdown 围栏，验证 Json/Pydantic Parser 的生产级容错能力
        word_count = len(user_msg.split())
        payload = {
            "executive_summary": "StarMind KB v2.0 achieves hybrid retrieval with sub-second latency.",
            "keywords": ["StarMind", "Hybrid Retrieval", "Sub-second Latency"],
            "tone": "Professional",
            "word_count": max(1, word_count),
        }
        return f"好的，分析结果如下：\n```json\n{json.dumps(payload, ensure_ascii=False)}\n```"

    return user_msg


def build_translation_pipeline() -> Runnable[Dict[str, Any], Dict[str, Any]]:
    """构建「翻译 -> 润色 -> (摘要 || 结构化质检)」企业级 LCEL 流水线。"""
    llm = RunnableChatModel(StarMindChatModel(model_name="deepseek-v3", handler=_enterprise_doc_handler))
    str_parser = StrOutputParser()
    report_parser = PydanticOutputParser(DocQualityReport)

    translate_chain = (
        RunnablePrompt(ChatPromptTemplate.from_messages([
            ("system", "【任务：翻译】你是科技文档译员，请将中文准确翻译为英文。"),
            ("human", "{raw_text}"),
        ]))
        | llm
        | str_parser
    )

    polish_chain = (
        RunnablePrompt(ChatPromptTemplate.from_messages([
            ("system", "【任务：润色】你是母语为英语的科技主编，请润色以下译文使其符合海外发布会标准。"),
            ("human", "{translated}"),
        ]))
        | llm
        | str_parser
    )

    summary_chain = (
        RunnablePrompt(ChatPromptTemplate.from_messages([
            ("system", "【任务：摘要】请用一句精炼英文总结核心亮点。"),
            ("human", "{polished}"),
        ]))
        | llm
        | str_parser
    )

    quality_chain = (
        RunnablePrompt(
            ChatPromptTemplate.from_messages([
                ("system", "【任务：质检JSON】请评估以下英文稿件。{format_instructions}"),
                ("human", "{polished}"),
            ]).partial(format_instructions=report_parser.get_format_instructions())
        )
        | llm
        | report_parser
    )

    # 通过 assign 保留每一步中间产物，并在最后一步并行生成摘要与强类型质检对象
    return (
        RunnablePassthrough.assign(translated=translate_chain)
        | RunnablePassthrough.assign(polished=polish_chain)
        | RunnablePassthrough.assign(
            final=RunnableParallel({
                "summary": summary_chain,
                "quality_report": quality_chain,
            })
        )
    )


if __name__ == "__main__":
    pipeline = build_translation_pipeline()
    output = pipeline.invoke({"raw_text": "星辰智脑企业知识库2.0正式上线，支持混合检索与毫秒级响应。"})
    print("1. 直译结果:", output["translated"])
    print("2. 商务润色:", output["polished"])
    print("3. 高管摘要:", output["final"]["summary"])
    report: DocQualityReport = output["final"]["quality_report"]
    print("4. 强类型质检报告:", report.model_dump())

