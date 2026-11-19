"""
STARMIND-010 模块二：主备模型容错执行器与 requirements.txt 规范审计工具。
演示 try/except/else/finally、精准异常分流、异常链 raise...from 与工程依赖检查。
"""

from typing import Callable, Dict, Any, List
from day10_exceptions import StarMindError, AuthError


def call_with_fallback(
    primary_fn: Callable[[str], str],
    fallback_fn: Callable[[str], str],
    prompt: str,
) -> Dict[str, Any]:
    """
    高可用模型调用调度器：
    - 主模型正常：直接返回 primary 结果；
    - 主模型抛出可重试 StarMindError（如 RateLimitError/Timeout）：自动降级至备用模型；
    - 主模型抛出 AuthError 等不可重试异常：立即透传上抛，绝不掩盖根因。
    """
    audit_events: List[str] = []
    try:
        audit_events.append("try_primary")
        reply = primary_fn(prompt)
    except AuthError:
        # 鉴权失败属于配置事故，不降级直接暴露
        audit_events.append("auth_abort")
        raise
    except StarMindError as exc:
        if not exc.retryable:
            audit_events.append("non_retryable_abort")
            raise
        # 可重试/可降级异常：自动切换备用模型
        audit_events.append(f"fallback_on_{exc.code}")
        try:
            reply = fallback_fn(prompt)
            channel = "fallback"
        except Exception as fb_exc:
            raise StarMindError("主备模型均调用失败", detail=str(fb_exc)) from fb_exc
    else:
        # 仅当 try 块完全无异常时执行
        channel = "primary"
        audit_events.append("primary_ok")
    finally:
        # 无论成功、降级还是抛异常，审计收尾钩子必然执行
        audit_events.append("audit_closed")

    return {
        "ok": True,
        "channel": channel,
        "reply": reply,
        "audit_events": audit_events,
    }


def audit_requirements_text(req_content: str) -> Dict[str, List[str]]:
    """检查 requirements.txt 文本，识别已锁版本与未锁版本的风险依赖。"""
    pinned: List[str] = []
    unpinned: List[str] = []
    for raw_line in req_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            pinned.append(line)
        else:
            unpinned.append(line)
    return {"pinned": pinned, "unpinned": unpinned}


if __name__ == "__main__":
    from day10_exceptions import RateLimitError

    def mock_primary(_p: str) -> str:
        raise RateLimitError("主通道 429 限流")

    def mock_fallback(p: str) -> str:
        return f"[备用通义千问兜底] 已处理: {p}"

    print("降级结果:", call_with_fallback(mock_primary, mock_fallback, "查询报销流程"))
    sample_req = "# 核心依赖\nfastapi==0.115.0\npydantic\nuvicorn==0.30.0\n"
    print("依赖审计:", audit_requirements_text(sample_req))

