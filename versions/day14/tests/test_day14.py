import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""STARMIND-014 阶段考核项目一自动化验收测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day14_session_memory import ConversationMemory
from day14_cli_assistant import StarMindCLIAssistant


def test_memory_sliding_window_and_json_roundtrip(tmp_path: Path):
    mem = ConversationMemory(system_prompt="你是星辰助教", max_history_messages=2, session_id="s-01")
    mem.add_user_message("第1问")
    mem.add_assistant_message("第1答")
    mem.add_user_message("第2问")
    mem.add_assistant_message("第2答")

    payload = mem.build_payload_messages()
    # system 置顶 + 最近 2 条消息 = 共 3 条
    assert len(payload) == 3
    assert payload[0] == {"role": "system", "content": "你是星辰助教"}
    assert payload[1]["content"] == "第2问"
    assert payload[2]["content"] == "第2答"

    saved_file = mem.save_to_json(tmp_path / "history.json")
    restored = ConversationMemory.load_from_json(saved_file)
    assert restored.session_id == "s-01"
    assert restored.system_prompt == "你是星辰助教"
    assert len(restored.messages) == 4

    # 损坏的 JSON 必须抛出 ValueError
    broken = tmp_path / "broken.json"
    broken.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError):
        ConversationMemory.load_from_json(broken)


def test_cli_assistant_multiturn_commands_and_persistence(tmp_path: Path):
    assistant = StarMindCLIAssistant(save_dir=tmp_path)

    # 1. 多轮记忆验证
    ok1, out1 = assistant.handle_line("你好，我叫阿杰")
    assert ok1 is True and "阿杰" in out1

    ok2, out2 = assistant.handle_line("你还记得我叫什么吗？")
    assert ok2 is True and "阿杰" in out2

    # 2. /stats 与 /history 与 /save
    _, stats_out = assistant.handle_line("/stats")
    assert "对话轮数: 2" in stats_out

    _, hist_out = assistant.handle_line("/history")
    assert "阿杰" in hist_out

    _, save_out = assistant.handle_line("/save my_chat")
    saved_path = tmp_path / "my_chat.json"
    assert saved_path.exists()
    assert "my_chat.json" in save_out

    # 3. /clear 清空后忘记上下文，但系统人设仍在
    _, clear_out = assistant.handle_line("/clear")
    assert "已清空" in clear_out
    assert len(assistant.memory.messages) == 0

    _, out3 = assistant.handle_line("你还记得我叫什么吗？")
    assert "还没有告诉我" in out3

    # 4. /exit 正常结束循环
    keep_going, exit_out = assistant.handle_line("/exit")
    assert keep_going is False
    assert "再见" in exit_out


def test_cli_assistant_error_rollback_and_edge_cases(tmp_path: Path):
    assistant = StarMindCLIAssistant(save_dir=tmp_path)
    assistant.handle_line("第一轮正常提问")
    assert len(assistant.memory.messages) == 2

    # 触发模拟后端故障：助手不应崩溃，且失败的 user 消息应被自动回滚
    keep_going, err_out = assistant.handle_line("请执行 __TRIGGER_ERROR__")
    assert keep_going is True
    assert "已自动回滚" in err_out
    assert len(assistant.memory.messages) == 2

    # 空输入与未知指令
    _, empty_out = assistant.handle_line("   ")
    assert "不能为空" in empty_out

    _, unknown_out = assistant.handle_line("/foobar")
    assert "未知指令" in unknown_out


def test_run_repl_end_to_end(tmp_path: Path):
    assistant = StarMindCLIAssistant(save_dir=tmp_path)
    outputs = assistant.run_repl(["/help", "我叫老陈", "报销怎么走？", "/exit"])
    assert len(outputs) == 4
    assert "/clear" in outputs[0]
    assert "老陈同学" in outputs[2]
    assert "再见" in outputs[3]

