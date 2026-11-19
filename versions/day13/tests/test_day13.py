import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-013 自动化单元测试。"""

import asyncio
import inspect
import sys
import time
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day13_decorators_and_env import (
    load_env_settings,
    retry_with_backoff,
    stream_text_chunks,
)
from day13_async_llm_runner import batch_ask_concurrently, invoke_with_timeout


def test_load_env_settings_with_and_without_file(tmp_path: Path):
    # 缺失 .env 文件应平滑返回默认值
    default_cfg = load_env_settings(tmp_path / "missing.env")
    assert default_cfg.model_name == "deepseek-chat"
    assert default_cfg.api_key == ""

    # 存在 .env 文件时正确解析
    env_file = tmp_path / ".env"
    env_file.write_text(
        "STARMIND_MODEL=qwen-plus\nSTARMIND_API_KEY=sk-local-123\nSTARMIND_TIMEOUT=25.5\nSTARMIND_MAX_RETRIES=4\n",
        encoding="utf-8",
    )
    loaded = load_env_settings(env_file)
    assert loaded.model_name == "qwen-plus"
    assert loaded.api_key == "sk-local-123"
    assert loaded.timeout_sec == 25.5
    assert loaded.max_retries == 4


def test_retry_with_backoff_success_and_exhaustion():
    attempts = {"n": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.001, exceptions=(RuntimeError,))
    def recover_on_third() -> str:
        """恢复测试文档字符串。"""
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient error")
        return "recovered"

    assert recover_on_third.__name__ == "recover_on_third"
    assert recover_on_third() == "recovered"
    assert attempts["n"] == 3

    @retry_with_backoff(max_retries=2, base_delay=0.001, exceptions=(RuntimeError,))
    def always_fail() -> str:
        raise RuntimeError("permanent error")

    with pytest.raises(RuntimeError, match="permanent error"):
        always_fail()


def test_stream_text_chunks_generator():
    gen = stream_text_chunks("星辰智脑AI助手", chunk_size=3)
    assert inspect.isgenerator(gen)
    parts = list(gen)
    assert parts == ["星辰智", "脑AI", "助手"]
    assert "".join(parts) == "星辰智脑AI助手"


def test_async_concurrent_batch_and_timeout():
    prompts = [f"Q{i}" for i in range(5)]
    start = time.perf_counter()
    results = asyncio.run(
        batch_ask_concurrently(prompts, delay_sec=0.04, timeout_sec=0.3, max_concurrency=5)
    )
    elapsed = time.perf_counter() - start
    assert len(results) == 5
    assert all(r["status"] == "ok" for r in results)
    # 5 个 40ms 任务并发执行，总耗时应明显小于串行的 200ms
    assert elapsed < 0.16

    # 验证单请求超时优雅降级
    timeout_res = asyncio.run(invoke_with_timeout("慢查询", delay_sec=0.1, timeout_sec=0.02))
    assert timeout_res["status"] == "timeout"
    assert "超时" in timeout_res["answer"]

