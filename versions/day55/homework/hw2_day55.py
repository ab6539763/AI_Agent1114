"""
Day 55 课后作业 2（企业实战）：企业实战：编写面向真实 Ollama / vLLM 的 OpenAI 兼容 SSE 流式适配器
工单：STARMIND-055
"""

import json
from typing import AsyncIterator
import httpx


async def openai_compat_stream(
    base_url: str, api_key: str, model: str, prompt: str
) -> AsyncIterator[str]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    yield delta


print("OpenAI 兼容流式适配器定义完成，可直接注入 run_benchmark！")

