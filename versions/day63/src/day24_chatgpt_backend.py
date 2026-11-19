"""
StarMind Day 24 - 步骤二：网页版星辰 ChatGPT 克隆全栈后端
集成 CORS 跨域中间件、静态前端首页托管、SSE 流式对话推送与 SQLite 持久化。
"""

import json
from typing import Dict, Generator, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from src.day24_database import ChatRepository


EMBEDDED_CHAT_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>星辰智脑 StarMind · 网页版企业 ChatGPT</title>
</head>
<body>
  <main id="starmind-app">
    <h1>星辰智脑 StarMind 企业工作台</h1>
    <div id="chat-log"></div>
    <form id="chat-form">
      <input id="chat-input" type="text" placeholder="请输入问题..." />
      <button id="send-btn" type="submit">发送</button>
    </form>
  </main>
  <script>
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const log = document.getElementById("chat-log");
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      input.value = "";
      const resp = await fetch("/api/v1/chat/stream", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({session_id: "web_default", message: text})
      });
      const reader = resp.body.getReader();
      const decoder = new TextDecoder("utf-8");
      const p = document.createElement("p");
      log.appendChild(p);
      while (true) {
        const {value, done} = await reader.read();
        if (done) break;
        const lines = decoder.decode(value).split("\\n");
        for (const line of lines) {
          if (line.startsWith("data: ") && !line.includes("[DONE]")) {
            const obj = JSON.parse(line.slice(6));
            if (obj.delta) p.textContent += obj.delta;
          }
        }
      }
    });
  </script>
</body>
</html>
"""


class StreamChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: str = Field(..., min_length=2, max_length=64)
    message: str = Field(..., min_length=1, max_length=4000)
    chunk_size: int = Field(default=6, ge=1, le=64)


def _synthesize_stream_reply(message: str, history: List[Dict[str, str]]) -> str:
    """结合 SQLite 持久化历史生成上下文连贯的回复文本。"""
    if "差旅" in message or "住宿" in message:
        return "根据星辰数科差旅报销规范：杭州/北京/上海/深圳住宿上限为 600 元/晚，请保留电子专票。"
    if "历史" in message or "上一句" in message:
        user_msgs = [m["content"] for m in history if m["role"] == "user"]
        if len(user_msgs) >= 2:
            return f"我从数据库历史中查到，您上一条问题是：「{user_msgs[-2]}」。"
    return f"星辰智脑已收到您的消息「{message}」，本次对话已实时流式推送并持久化保存至 SQLite。"


def create_chatgpt_app(
    database_url: str = "sqlite:///:memory:",
    allowed_origins: List[str] | None = None,
) -> FastAPI:
    """构建完整可联调的网页版星辰 ChatGPT 克隆后端应用。"""
    app = FastAPI(title="星辰智脑 ChatGPT 克隆全栈服务", version="1.0.0")
    repo = ChatRepository(database_url=database_url)

    # 1. 配置企业级 CORS 跨域中间件
    origins = allowed_origins or ["http://localhost:3000", "http://localhost:5173", "https://starmind.local"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. 托管静态前端聊天首页
    @app.get("/", response_class=HTMLResponse, tags=["Web"])
    def serve_index() -> HTMLResponse:
        return HTMLResponse(content=EMBEDDED_CHAT_HTML)

    # 3. SSE 流式对话接口 + 自动持久化落盘
    @app.post("/api/v1/chat/stream", tags=["Chat"])
    def stream_chat(req: StreamChatRequest) -> StreamingResponse:
        # 先落盘用户提问，确保即使后续中断也能追溯请求
        repo.add_message(req.session_id, "user", req.message)
        history = repo.get_messages(req.session_id) or []
        full_reply = _synthesize_stream_reply(req.message, history)

        def sse_generator() -> Generator[str, None, None]:
            collected: List[str] = []
            for idx in range(0, len(full_reply), req.chunk_size):
                piece = full_reply[idx : idx + req.chunk_size]
                collected.append(piece)
                payload = json.dumps(
                    {"session_id": req.session_id, "delta": piece},
                    ensure_ascii=False,
                )
                yield f"data: {payload}\n\n"

            # 流式推送完毕，将完整助手回复持久化写入 SQLite
            repo.add_message(req.session_id, "assistant", "".join(collected))
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            sse_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # 4. 历史会话列表、详情与级联删除接口
    @app.get("/api/v1/sessions", tags=["Sessions"])
    def list_sessions() -> Dict[str, object]:
        return {"sessions": repo.list_sessions()}

    @app.get("/api/v1/sessions/{session_id}", tags=["Sessions"])
    def get_session_history(session_id: str) -> Dict[str, object]:
        msgs = repo.get_messages(session_id)
        if msgs is None:
            raise HTTPException(status_code=404, detail=f"会话 '{session_id}' 不存在")
        return {"session_id": session_id, "messages": msgs}

    @app.delete("/api/v1/sessions/{session_id}", tags=["Sessions"])
    def delete_session(session_id: str) -> Dict[str, str]:
        if not repo.delete_session(session_id):
            raise HTTPException(status_code=404, detail=f"会话 '{session_id}' 不存在")
        return {"status": "deleted", "session_id": session_id}

    return app


app = create_chatgpt_app()


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    client = TestClient(create_chatgpt_app())
    with client.stream("POST", "/api/v1/chat/stream", json={"session_id": "web_01", "message": "杭州差旅住宿报销标准？"}) as r:
        print("Content-Type:", r.headers["content-type"])
        for line in r.iter_lines():
            if line:
                print("SSE帧 ->", line)
    print("持久化查询:", client.get("/api/v1/sessions/web_01").json())

