"""
Day 22 课后作业 2（企业实战）：轻量级纯 Python HTML 转义工具函数（防 XSS）
工单：STARMIND-022
"""

import html


def safe_render_bubble_html(role: str, content: str) -> str:
    """服务端安全渲染消息气泡 HTML，严格防 XSS 注入。"""
    if role not in {"user", "assistant"}:
        raise ValueError(f"非法角色: {role}")
    escaped = html.escape(content, quote=True)
    return f'<div class="msg-row {role}"><div class="bubble">{escaped}</div></div>'


if __name__ == "__main__":
    print(safe_render_bubble_html("user", "<script>alert('xss')</script>"))

