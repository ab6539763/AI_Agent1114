import sys
from pathlib import Path
_DAY_ROOT = str(Path(__file__).resolve().parent.parent)
if _DAY_ROOT not in sys.path:
    sys.path.insert(0, _DAY_ROOT)

"""Day 44 自动化单元测试：验证 JSON-RPC 2.0 MCP Server/Client 与 SQLite 双层记忆引擎。"""

import json
from pathlib import Path
from src.day44_mcp_protocol import (
    ERR_INVALID_PARAMS,
    ERR_METHOD_NOT_FOUND,
    MCPClient,
    create_starmind_enterprise_mcp_server,
)
from src.day44_agent_memory import HybridMemoryManager, SQLiteLongTermMemory


def test_mcp_handshake_tools_and_resources():
    srv = create_starmind_enterprise_mcp_server()
    cli = MCPClient(srv.handle_json_line)

    init = cli.initialize()
    assert init["jsonrpc"] == "2.0"
    assert init["result"]["serverInfo"]["name"] == "starmind-enterprise-mcp"

    tools = cli.list_tools()
    assert any(t["name"] == "lookup_employee" for t in tools)

    call_resp = cli.call_tool("lookup_employee", {"name": "林产品"})
    assert call_resp["result"]["isError"] is False
    parsed = json.loads(call_resp["result"]["content"][0]["text"])
    assert parsed["dept"] == "智能产品部"

    policy = cli.read_resource("starmind://policies/mcp-security")
    assert "最小权限白名单" in policy


def test_mcp_jsonrpc_standard_error_codes():
    srv = create_starmind_enterprise_mcp_server()
    cli = MCPClient(srv.handle_json_line)

    unknown_method = cli.request("tools/delete_all")
    assert unknown_method["error"]["code"] == ERR_METHOD_NOT_FOUND

    missing_param = cli.call_tool("lookup_employee", {})
    assert missing_param["error"]["code"] == ERR_INVALID_PARAMS


def test_long_term_memory_persists_across_sessions(tmp_path: Path):
    db_file = tmp_path / "memory.db"
    ltm1 = SQLiteLongTermMemory(db_file)
    ltm1.remember("emp_01", "preference", "代码评审优先指出并发安全隐患", importance=5)
    ltm1.remember("emp_01", "fact", "所在部门为企业研发二部", importance=3)
    ltm1.close()

    # 模拟新会话重启连接同一 SQLite 文件
    ltm2 = SQLiteLongTermMemory(db_file)
    mgr = HybridMemoryManager("emp_01", ltm2, max_short_messages=2)
    mgr.short_term.add("user", "第一句")
    mgr.short_term.add("assistant", "第一答")
    mgr.short_term.add("user", "帮我做一下并发代码评审")
    ctx = mgr.build_prompt_context("并发代码评审", top_k=1)

    assert len(ctx["short_term_messages"]) == 2
    assert ctx["evicted_count"] == 1
    assert "并发安全隐患" in ctx["long_term_memories"][0]
    ltm2.close()

