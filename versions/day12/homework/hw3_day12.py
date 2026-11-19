"""
Day 12 课后作业 3（架构进阶）：架构进阶：带自定义 Trace-ID 的 httpx 拦截测试封装
工单：STARMIND-012
"""

"""Day 12 课后题 3：带 X-Trace-Id 链路追踪头的 httpx 请求与离线 Mock 验证。"""

from typing import Any, Dict
import httpx


def send_traced_request(
    url: str,
    trace_id: str,
    transport: httpx.BaseTransport,
) -> Dict[str, Any]:
    """发送带链路追踪 ID 的 GET 请求并校验回显。"""
    with httpx.Client(timeout=5.0, transport=transport) as client:
        resp = client.get(url, headers={"X-Trace-Id": trace_id})
        resp.raise_for_status()
        data = resp.json()
    if data.get("echo_trace_id") != trace_id:
        raise ValueError("服务端未正确回显 X-Trace-Id")
    return data


if __name__ == "__main__":
    def mock_server(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"status": "ok", "echo_trace_id": request.headers.get("X-Trace-Id")},
        )

    result = send_traced_request(
        "https://api.starmind.local/health",
        trace_id="trace-20260512-001",
        transport=httpx.MockTransport(mock_server),
    )
    print("链路追踪验证通过:", result)

