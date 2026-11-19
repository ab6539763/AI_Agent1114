"""
Day 42 课后作业 2（企业实战）：实现带降级兜底的并行章节 Fan-out
工单：STARMIND-042
"""

"""Day 42 作业 2 参考答案：部分失败容错的并行 Fan-out 执行器。"""

from concurrent.futures import ThreadPoolExecutor


def write_one(sec: dict) -> dict:
    if sec["index"] == 2:
        raise TimeoutError("第2章接口超时")
    return {"index": sec["index"], "text": f"正文-{sec['title']}", "ok": True}


def safe_parallel_write(sections: list[dict]) -> list[dict]:
    out = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        future_map = {pool.submit(write_one, s): s for s in sections}
        for fut, sec in future_map.items():
            try:
                out.append(fut.result())
            except Exception as exc:
                out.append({"index": sec["index"], "text": f"【降级占位】生成失败: {exc}", "ok": False})
    out.sort(key=lambda x: x["index"])
    return out


if __name__ == "__main__":
    secs = [{"index": 1, "title": "背景"}, {"index": 2, "title": "架构"}, {"index": 3, "title": "计划"}]
    res = safe_parallel_write(secs)
    print(res)
    assert res[0]["ok"] is True and res[1]["ok"] is False and res[2]["ok"] is True

