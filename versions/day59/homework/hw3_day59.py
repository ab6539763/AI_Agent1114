"""
Day 59 课后作业 3（架构进阶）：架构进阶：实现基于 contextvars 的异步协程级 trace_id 上下文传递
工单：STARMIND-059
"""

import asyncio
from contextvars import ContextVar

trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="tr-none")


async def handle_req(req_id: str) -> str:
    trace_id_ctx.set(f"tr-{req_id}")
    await asyncio.sleep(0.01)
    return trace_id_ctx.get()


async def main():
    res = await asyncio.gather(handle_req("A"), handle_req("B"), handle_req("C"))
    assert res == ["tr-A", "tr-B", "tr-C"]
    print("ContextVar 并发 trace_id 隔离验证通过:", res)


asyncio.run(main())

