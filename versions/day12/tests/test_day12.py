import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-012 自动化单元测试（全程离线，零外网依赖）。"""

import sys
from pathlib import Path
import httpx
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day12_llm_http_client import (
    LLMAPIError,
    LLMRequestConfig,
    StarMindHTTPClient,
    build_chat_payload,
    parse_chat_response,
)
from day12_cli_qa import ask_once, run_cli_qa


def test_payload_and_response_parser():
    payload = build_chat_payload([{"role": "user", "content": "你好"}], model="qwen-plus", temperature=0.3)
    assert payload["model"] == "qwen-plus"
    assert payload["temperature"] == 0.3

    raw = {
        "model": "qwen-plus",
        "choices": [{"message": {"role": "assistant", "content": "  你好，星辰同事！  "}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
    }
    resp = parse_chat_response(raw, latency_ms=12.345, source="remote")
    assert resp.content == "你好，星辰同事！"
    assert resp.total_tokens == 15
    assert resp.latency_ms == 12.35

    with pytest.raises(ValueError):
        parse_chat_response({"choices": []}, latency_ms=1.0)


def test_auto_mock_fallback_without_api_key():
    client = StarMindHTTPClient(LLMRequestConfig(api_key="", model="deepseek-chat"))
    assert client.mock_mode is True
    resp = ask_once(client, "年假有多少天？")
    assert resp.source == "mock"
    assert "年假" in resp.content


def test_remote_http_success_and_error_codes_with_mock_transport():
    # 1. 模拟 HTTP 200 正常返回并校验 Authorization 请求头
    def ok_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer sk-test-key"
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={
                "model": "deepseek-chat",
                "choices": [{"message": {"role": "assistant", "content": "来自远程模拟节点的回复"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 18, "total_tokens": 30},
            },
        )

    cfg = LLMRequestConfig(api_key="sk-test-key", model="deepseek-chat")
    client_ok = StarMindHTTPClient(cfg, transport=httpx.MockTransport(ok_handler))
    resp = client_ok.chat([{"role": "user", "content": "测试远程调用"}])
    assert resp.source == "remote"
    assert resp.content == "来自远程模拟节点的回复"
    assert resp.total_tokens == 30

    # 2. 模拟 HTTP 401 鉴权失败与 HTTP 429 限流
    client_401 = StarMindHTTPClient(
        cfg,
        transport=httpx.MockTransport(lambda req: httpx.Response(401, json={"error": "invalid key"})),
    )
    with pytest.raises(LLMAPIError) as exc_401:
        client_401.chat([{"role": "user", "content": "hi"}])
    assert exc_401.value.status_code == 401

    client_429 = StarMindHTTPClient(
        cfg,
        transport=httpx.MockTransport(lambda req: httpx.Response(429, json={"error": "rate limit"})),
    )
    with pytest.raises(LLMAPIError) as exc_429:
        client_429.chat([{"role": "user", "content": "hi"}])
    assert exc_429.value.status_code == 429


def test_run_cli_qa_scripted():
    client = StarMindHTTPClient(LLMRequestConfig(api_key=""))
    logs = run_cli_qa(client, inputs=["", "报销流程", "/exit"])
    assert "不能为空" in logs[0]
    assert "费用报销单" in logs[1]
    assert "已退出" in logs[2]

