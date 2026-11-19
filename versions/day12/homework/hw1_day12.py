"""
Day 12 课后作业 1（基础巩固）：基础巩固：HTTP 状态码智能诊断器
工单：STARMIND-012
"""

"""Day 12 课后题 1：大模型 API HTTP 状态码智能诊断器。"""

from typing import Any, Dict


def diagnose_http_status(status_code: int) -> Dict[str, Any]:
    """根据 HTTP 状态码返回故障分类、是否建议重试及排查建议。"""
    if 200 <= status_code < 300:
        return {"category": "success", "retryable": False, "advice": "请求成功，正常解析响应即可。"}
    if status_code in (401, 403):
        return {"category": "auth_error", "retryable": False, "advice": "检查 API Key 是否正确、过期或缺少权限。"}
    if status_code == 429:
        return {"category": "rate_limit", "retryable": True, "advice": "触发限流或配额不足，建议指数退避重试或检查账户余额。"}
    if 500 <= status_code < 600:
        return {"category": "server_error", "retryable": True, "advice": "大模型厂商服务端抖动，建议稍后重试或切换备用模型。"}
    return {"category": "client_error", "retryable": False, "advice": f"客户端请求异常（HTTP {status_code}），请检查 URL 与请求体格式。"}


if __name__ == "__main__":
    for code in (200, 401, 429, 503):
        print(code, "->", diagnose_http_status(code))

