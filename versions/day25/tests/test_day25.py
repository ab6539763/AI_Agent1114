import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 25 自动化单元测试：验证 ChatModel 统一接口与 PromptTemplate 渲染安全。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day25_chat_model import (
    AIMessage,
    HumanMessage,
    StarMindChatModel,
    SystemMessage,
)
from src.day25_prompt_template import (
    ChatPromptTemplate,
    PromptTemplate,
    build_it_ticket_prompt,
)


def test_chat_model_invoke_and_metadata():
    llm = StarMindChatModel(model_name="deepseek-v3-test", temperature=0.0)
    resp = llm.invoke([
        SystemMessage(content="你是IT工单分类助手"),
        HumanMessage(content="VPN断网了连不上GitLab"),
    ])
    assert isinstance(resp, AIMessage)
    assert "网络与权限类" in resp.content
    assert resp.usage_metadata["total_tokens"] > 0
    assert resp.response_metadata["model_name"] == "deepseek-v3-test"


def test_chat_model_custom_handler_and_str_input():
    llm = StarMindChatModel(handler=lambda msgs: f"ECHO:{msgs[-1].content}")
    resp = llm.invoke("你好星辰智脑")
    assert resp.content == "ECHO:你好星辰智脑"


def test_prompt_template_missing_var_and_escaped_braces():
    tpl = PromptTemplate.from_template('请返回JSON：{{"dept": "{dept}", "q": "{q}"}}')
    assert tpl.input_variables == ["dept", "q"]
    rendered = tpl.format(dept="研发部", q="报销流程")
    assert rendered == '请返回JSON：{"dept": "研发部", "q": "报销流程"}'

    with pytest.raises(ValueError, match="缺少必填变量"):
        tpl.format(dept="研发部")


def test_chat_prompt_partial_and_fewshot():
    prompt = build_it_ticket_prompt()
    assert prompt.input_variables == ["dept", "issue"]
    msgs = prompt.format_messages(dept="财务部", issue="笔记本蓝屏无法开机")
    assert len(msgs) == 4
    assert msgs[0].role == "system"
    assert "杭州星辰数科" in msgs[0].content
    resp = StarMindChatModel().invoke(msgs)
    assert "硬件设备类" in resp.content

