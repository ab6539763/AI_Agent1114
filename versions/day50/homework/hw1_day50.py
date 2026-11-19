"""
Day 50 课后作业 1（基础巩固）：为责任链管道新增一个请求限流中间件（RateLimitMiddleware）
工单：STARMIND-050
"""

"""Day 50 作业 1 参考答案：用户级请求限流中间件。"""

from collections import defaultdict
from typing import Callable, Dict


def make_rate_limit_middleware(max_requests: int = 2) -> Callable:
    counts: Dict[str, int] = defaultdict(int)

    def rate_limit_mw(ctx: dict, nxt: Callable) -> dict:
        uid = ctx["user_id"]
        counts[uid] += 1
        if counts[uid] > max_requests:
            ctx["status"] = "RATE_LIMITED"
            ctx["reply"] = "请求过于频繁，请稍后再试。"
            return ctx
        return nxt(ctx)

    return rate_limit_mw


if __name__ == "__main__":
    mw = make_rate_limit_middleware(max_requests=2)
    nxt = lambda c: {**c, "status": "COMPLETED"}
    assert mw({"user_id": "u1"}, nxt)["status"] == "COMPLETED"
    assert mw({"user_id": "u1"}, nxt)["status"] == "COMPLETED"
    assert mw({"user_id": "u1"}, nxt)["status"] == "RATE_LIMITED"
    print("限流中间件测试通过")

