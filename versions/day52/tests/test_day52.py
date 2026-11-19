import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 52 单元测试：数据清洗管道与 500 条客服语料合成器"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.day52_dataset_cleaner import alpaca_to_sharegpt, clean_alpaca_dataset, mask_pii
from src.day52_self_instruct_gen import export_datasets, synthesize_customer_service_dataset


def test_mask_pii_phone_and_email():
    text = "请联系13900112233或发送至ops@starmind.cn处理"
    masked, cnt = mask_pii(text)
    assert cnt == 2
    assert "13900112233" not in masked
    assert "<PHONE_MASKED>" in masked and "<EMAIL_MASKED>" in masked


def test_clean_pipeline_filters_duplicates_and_ai_tone():
    rows = [
        {"instruction": "如何重置密码？", "input": "", "output": "请点击登录页忘记密码，通过企业邮箱验证码重置即可生效。"},
        {"instruction": "如何重置密码？", "input": "", "output": "请点击登录页忘记密码，通过企业邮箱验证码重置即可生效。"},
        {"instruction": "你是谁？", "input": "", "output": "作为一个AI语言模型，我无法透露身份信息。"},
        {"instruction": "空回复测试", "input": "", "output": "好"},
    ]
    cleaned, stats = clean_alpaca_dataset(rows)
    assert len(cleaned) == 1
    assert stats.dropped_exact_dup == 1
    assert stats.dropped_low_quality == 2


def test_synthesize_500_samples_and_export(tmp_path):
    summary = export_datasets(tmp_path, target_count=500)
    assert summary["total"] == 500
    assert summary["train"] == 450
    assert summary["eval"] == 50
    assert (tmp_path / "starmind_cs_train_alpaca.json").exists()
    assert (tmp_path / "starmind_cs_train_sharegpt.json").exists()


def test_sharegpt_format_valid():
    train_data, _ = synthesize_customer_service_dataset(target_count=20)
    sg = alpaca_to_sharegpt(train_data[:5])
    assert len(sg) == 5
    for item in sg:
        convs = item["conversations"]
        assert convs[0]["from"] == "human"
        assert convs[1]["from"] == "gpt"

