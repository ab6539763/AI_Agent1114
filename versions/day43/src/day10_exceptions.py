"""
STARMIND-010 模块一：星辰智脑自定义异常体系。
演示异常类继承、结构化错误元数据（code/retryable）以及标准错误字典序列化。
"""

from typing import Dict, Any


class StarMindError(Exception):
    """星辰智脑平台所有业务异常的统一基类。"""

    code: str = "E500"
    retryable: bool = False

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def to_error_dict(self) -> Dict[str, Any]:
        """将异常转为前后端统一的 JSON 错误响应结构。"""
        return {
            "ok": False,
            "error_code": self.code,
            "message": self.message,
            "detail": self.detail,
            "retryable": self.retryable,
        }


class RateLimitError(StarMindError):
    """上游大模型触发限流（HTTP 429），支持退避重试或切备用模型。"""

    code = "E429"
    retryable = True


class ModelTimeoutError(StarMindError):
    """上游大模型推理超时（HTTP 504），支持降级重试。"""

    code = "E504"
    retryable = True


class AuthError(StarMindError):
    """API Key 无效或已过期（HTTP 401），不可重试，需立即告警人工介入。"""

    code = "E401"
    retryable = False


if __name__ == "__main__":
    err = RateLimitError("DeepSeek 主通道触发 TPM 限流", detail="retry-after: 3s")
    print("异常字典:", err.to_error_dict())

