import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-009 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day09_base_model import BaseModel
from day09_model_providers import OpenAIModel, QwenModel, ModelRouter


def test_cannot_instantiate_abstract_base_model():
    with pytest.raises(TypeError):
        BaseModel("abstract-only")  # type: ignore


def test_temperature_property_validation():
    m = OpenAIModel("gpt-4o-mini", temperature=0.8)
    assert m.temperature == 0.8
    m.temperature = 0.0
    assert m.temperature == 0.0

    with pytest.raises(ValueError):
        m.temperature = 2.5
    with pytest.raises(ValueError):
        QwenModel("qwen-plus", temperature=-0.1)


def test_polymorphic_router_and_dunder_methods():
    router = ModelRouter()
    oai = OpenAIModel("gpt-4o-mini", temperature=0.2)
    qwen = QwenModel("qwen-max", temperature=0.6)

    router.register("oai", oai)
    router.register("qwen", qwen)
    assert len(router) == 2
    assert "qwen" in router

    r1 = router.ask("oai", "测试多态")
    r2 = router.ask("qwen", "测试多态")
    assert r1["provider"] == "openai" and oai.call_count == 1
    assert r2["provider"] == "qwen" and qwen.call_count == 1
    assert "X-DashScope-SSE" in qwen.build_headers()
    assert "openai" in str(oai)

