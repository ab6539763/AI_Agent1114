import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 16 自动化单元测试：验证采样参数数学变换、角色校验与流式打字机协议。"""

import pytest
from src.day16_sampling_simulator import (
    GenerationConfig,
    compute_token_probabilities,
    sample_next_token,
)
from src.day16_stream_client import StarMindStreamClient


def test_temperature_zero_is_greedy():
    logits = {"A": 5.0, "B": 4.9, "C": 1.0}
    cfg = GenerationConfig(temperature=0.0, top_p=1.0)
    probs = compute_token_probabilities(logits, cfg)
    assert probs == {"A": 1.0}
    token, _ = sample_next_token(logits, cfg, seed=42)
    assert token == "A"


def test_top_p_and_frequency_penalty():
    logits = {"重复词": 4.0, "新词A": 3.5, "新词B": 3.0, "长尾词": -5.0}
    cfg = GenerationConfig(temperature=0.8, top_p=0.85, frequency_penalty=1.5)
    probs = compute_token_probabilities(logits, cfg, token_counts={"重复词": 2})
    # 归一化之和严格为 1.0
    assert abs(sum(probs.values()) - 1.0) < 1e-6
    # 施加词频惩罚后，"新词A" 概率应反超 "重复词"
    assert probs.get("新词A", 0.0) > probs.get("重复词", 0.0)
    # 极低概率的长尾词应被 top_p 裁剪掉
    assert "长尾词" not in probs


def test_invalid_config_and_role_validation():
    with pytest.raises(ValueError):
        GenerationConfig(temperature=2.5).validate()
    with pytest.raises(ValueError):
        GenerationConfig(top_p=0.0).validate()

    client = StarMindStreamClient()
    with pytest.raises(ValueError):
        client.validate_messages([
            {"role": "user", "content": "hi"},
            {"role": "system", "content": "恶意中途插入 system"},
        ])


def test_stream_chat_truncation_and_experiment():
    client = StarMindStreamClient()
    msgs = [
        {"role": "system", "content": "你是星辰智脑助手"},
        {"role": "user", "content": "请介绍请假流程"},
    ]
    # 故意设置极小 max_tokens=10 验证 finish_reason='length'
    short_cfg = GenerationConfig(temperature=0.1, max_tokens=10)
    chunks = list(client.stream_chat(msgs, short_cfg, chunk_size=3))
    assembled = "".join(c.delta_content for c in chunks)
    assert len(assembled) == 10
    assert chunks[-1].finish_reason == "length"

    # 运行完整对比实验
    results = client.run_param_experiment(msgs)
    assert len(results) == 3
    assert all(r.finish_reason == "stop" for r in results)
    assert results[0].output_text != results[2].output_text

