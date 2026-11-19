import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 26 自动化单元测试：验证 LCEL Runnable 编排与三大 OutputParser。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day26_lcel_core import RunnableLambda, RunnableParallel, RunnablePassthrough
from src.day26_parsers_and_chain import (
    DocQualityReport,
    JsonOutputParser,
    OutputParserException,
    PydanticOutputParser,
    StrOutputParser,
    build_translation_pipeline,
)


def test_lcel_pipe_batch_and_stream():
    chain = (
        RunnableLambda(lambda x: x.strip())
        | (lambda x: f"星辰智脑:{x}")
    )
    assert chain.invoke("  hello ") == "星辰智脑:hello"
    assert chain.batch([" a ", " b "]) == ["星辰智脑:a", "星辰智脑:b"]
    chunks = list(chain.stream("  streaming_test  "))
    assert "".join(chunks) == "星辰智脑:streaming_test"
    assert len(chunks) >= 2


def test_json_and_pydantic_parsers():
    jp = JsonOutputParser()
    assert jp.invoke('说明如下：```json\n{"a": 1}\n```') == {"a": 1}

    with pytest.raises(OutputParserException):
        jp.invoke("这里根本没有合法JSON")

    pp = PydanticOutputParser(DocQualityReport)
    assert "executive_summary" in pp.get_format_instructions()
    with pytest.raises(OutputParserException, match="Pydantic"):
        # word_count 必须 > 0
        pp.invoke('{"executive_summary": "ok", "keywords": ["k"], "tone": "Formal", "word_count": 0}')


def test_translation_polish_summary_pipeline():
    pipeline = build_translation_pipeline()
    res = pipeline.invoke({"raw_text": "星辰智脑知识库升级上线"})
    assert "translated" in res and "polished" in res
    assert isinstance(res["final"]["summary"], str)
    assert isinstance(res["final"]["quality_report"], DocQualityReport)
    assert res["final"]["quality_report"].word_count > 0

