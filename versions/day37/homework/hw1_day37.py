"""
Day 37 课后作业 1（基础巩固）：作业一：实现客户端 SSE 流式帧解析器（parse_sse_stream）
工单：STARMIND-037
"""

"""Day 37 作业一参考答案：兼容心跳帧的 SSE 客户端解析器"""
import json
from typing import Any, Dict, Iterable, List


def parse_sse_lines(lines: Iterable[str]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    cur_event = "message"
    cur_data: List[str] = []

    for raw in lines:
        line = raw.rstrip("\r\n")
        if line.startswith(":"):
            continue  # 跳过 SSE 心跳保活注释帧
        if line == "":
            if cur_data:
                events.append({"event": cur_event, "data": json.loads("\n".join(cur_data))})
                cur_event = "message"
                cur_data = []
            continue
        if line.startswith("event:"):
            cur_event = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            cur_data.append(line.split(":", 1)[1].strip())

    if cur_data:
        events.append({"event": cur_event, "data": json.loads("\n".join(cur_data))})
    return events


if __name__ == "__main__":
    sample = [
        ": keep-alive",
        "event: token",
        'data: {"delta": "你好"}',
        "",
        "event: done",
        'data: {"ok": true}',
        "",
    ]
    parsed = parse_sse_lines(sample)
    print(parsed)
    assert len(parsed) == 2 and parsed[0]["data"]["delta"] == "你好"

