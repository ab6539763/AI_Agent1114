"""Day 44 - 步骤一：严格遵循 JSON-RPC 2.0 规范的自研 MCP Server 与 MCP Client。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

JSONRPC_VERSION = "2.0"
ERR_PARSE = -32700
ERR_INVALID_REQUEST = -32600
ERR_METHOD_NOT_FOUND = -32601
ERR_INVALID_PARAMS = -32602
ERR_INTERNAL = -32603


@dataclass
class MCPToolSpec:
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]


@dataclass
class MCPResourceSpec:
    uri: str
    name: str
    mime_type: str
    content: str


class MCPServer:
    """轻量级企业 MCP Server：暴露 Tools 与 Resources，并严格按 JSON-RPC 2.0 响应。"""

    def __init__(self, server_name: str, version: str = "1.0.0") -> None:
        self.server_name = server_name
        self.version = version
        self._tools: Dict[str, MCPToolSpec] = {}
        self._resources: Dict[str, MCPResourceSpec] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[[Dict[str, Any]], Any],
    ) -> None:
        self._tools[name] = MCPToolSpec(name, description, input_schema, handler)

    def register_resource(self, uri: str, name: str, content: str, mime_type: str = "text/plain") -> None:
        self._resources[uri] = MCPResourceSpec(uri, name, mime_type, content)

    def _ok(self, req_id: Any, result: Any) -> str:
        return json.dumps({"jsonrpc": JSONRPC_VERSION, "id": req_id, "result": result}, ensure_ascii=False)

    def _err(self, req_id: Any, code: int, message: str) -> str:
        return json.dumps(
            {"jsonrpc": JSONRPC_VERSION, "id": req_id, "error": {"code": code, "message": message}},
            ensure_ascii=False,
        )

    def handle_json_line(self, raw_line: str) -> str:
        """处理单条 JSON-RPC 2.0 请求报文并返回响应 JSON 字符串。"""
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            return self._err(None, ERR_PARSE, f"JSON 解析失败: {exc}")

        if not isinstance(payload, dict) or payload.get("jsonrpc") != JSONRPC_VERSION or "method" not in payload:
            return self._err(payload.get("id") if isinstance(payload, dict) else None, ERR_INVALID_REQUEST, "非法 JSON-RPC 2.0 请求")

        req_id = payload.get("id")
        method = payload["method"]
        params = payload.get("params") or {}

        if method == "initialize":
            return self._ok(
                req_id,
                {
                    "protocolVersion": "2025-03-26",
                    "serverInfo": {"name": self.server_name, "version": self.version},
                    "capabilities": {"tools": {}, "resources": {}},
                },
            )

        if method == "tools/list":
            tools = [
                {"name": t.name, "description": t.description, "inputSchema": t.input_schema}
                for t in self._tools.values()
            ]
            return self._ok(req_id, {"tools": tools})

        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if tool_name not in self._tools:
                return self._err(req_id, ERR_INVALID_PARAMS, f"未知工具: {tool_name}")
            spec = self._tools[tool_name]
            required = spec.input_schema.get("required", [])
            missing = [k for k in required if k not in arguments]
            if missing:
                return self._err(req_id, ERR_INVALID_PARAMS, f"缺少必填参数: {missing}")
            try:
                output = spec.handler(arguments)
                return self._ok(
                    req_id,
                    {
                        "content": [{"type": "text", "text": json.dumps(output, ensure_ascii=False)}],
                        "isError": False,
                    },
                )
            except Exception as exc:
                return self._ok(
                    req_id,
                    {"content": [{"type": "text", "text": f"工具执行失败: {exc}"}], "isError": True},
                )

        if method == "resources/list":
            resources = [
                {"uri": r.uri, "name": r.name, "mimeType": r.mime_type}
                for r in self._resources.values()
            ]
            return self._ok(req_id, {"resources": resources})

        if method == "resources/read":
            uri = params.get("uri")
            if uri not in self._resources:
                return self._err(req_id, ERR_INVALID_PARAMS, f"资源不存在: {uri}")
            r = self._resources[uri]
            return self._ok(req_id, {"contents": [{"uri": r.uri, "mimeType": r.mime_type, "text": r.content}]})

        return self._err(req_id, ERR_METHOD_NOT_FOUND, f"不支持的方法: {method}")


class MCPClient:
    """MCP 客户端：封装 JSON-RPC 2.0 请求编号、握手与能力调用。"""

    def __init__(self, transport_fn: Callable[[str], str]) -> None:
        self._transport = transport_fn
        self._seq = 0

    def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self._seq += 1
        req = {"jsonrpc": JSONRPC_VERSION, "id": self._seq, "method": method, "params": params or {}}
        raw_resp = self._transport(json.dumps(req, ensure_ascii=False))
        return json.loads(raw_resp)

    def initialize(self) -> Dict[str, Any]:
        return self.request("initialize", {"clientInfo": {"name": "starmind-host", "version": "1.0"}})

    def list_tools(self) -> List[Dict[str, Any]]:
        resp = self.request("tools/list")
        return resp["result"]["tools"]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self.request("tools/call", {"name": name, "arguments": arguments})

    def read_resource(self, uri: str) -> str:
        resp = self.request("resources/read", {"uri": uri})
        return resp["result"]["contents"][0]["text"]


def create_starmind_enterprise_mcp_server() -> MCPServer:
    """构建星辰数科企业内网演示 MCP Server。"""
    server = MCPServer("starmind-enterprise-mcp", version="1.2.0")
    directory = {
        "老陈": {"dept": "AI 平台架构部", "title": "首席架构师", "email": "chen@starmind.cn"},
        "林产品": {"dept": "智能产品部", "title": "高级产品经理", "email": "lin@starmind.cn"},
    }
    server.register_tool(
        name="lookup_employee",
        description="按员工姓名查询所属部门、职级与企业邮箱",
        input_schema={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
        handler=lambda args: directory.get(args["name"], {"found": False, "name": args["name"]}),
    )
    server.register_resource(
        uri="starmind://policies/mcp-security",
        name="星辰数科 MCP 安全接入规范",
        content="所有生产 MCP Server 必须启用最小权限白名单，且禁止向 stdout 打印非 JSON-RPC 调试信息。",
    )
    return server


if __name__ == "__main__":
    srv = create_starmind_enterprise_mcp_server()
    client = MCPClient(transport_fn=srv.handle_json_line)
    print("握手响应:", client.initialize()["result"]["serverInfo"])
    print("发现工具:", [t["name"] for t in client.list_tools()])
    print("调用工具:", client.call_tool("lookup_employee", {"name": "老陈"})["result"])
    print("读取资源:", client.read_resource("starmind://policies/mcp-security"))

