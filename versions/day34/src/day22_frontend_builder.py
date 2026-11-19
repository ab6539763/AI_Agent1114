"""
StarMind Day 22 - 步骤一：星辰智脑企业级静态聊天前端生成器
生成完整、无外部 CDN 依赖的 index.html、styles.css 与 chat_app.js（支持 fetch 流式读取）。
"""

from pathlib import Path
from typing import Dict


INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>星辰智脑 StarMind · 企业 AI 工作台</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-badge">SM</span>
        <div>
          <h1>星辰智脑</h1>
          <p>杭州星辰数科 AI 平台</p>
        </div>
      </div>
      <button id="new-chat-btn" class="primary-btn" type="button">+ 新建企业会话</button>
      <ul id="session-list" class="session-list">
        <li class="session-item active">当前会话 · 默认工作台</li>
      </ul>
    </aside>

    <main class="chat-main">
      <header class="chat-header">
        <div>
          <h2>智能问答与工具助手</h2>
          <span id="status-badge" class="status-badge">就绪 · SSE 流式通道</span>
        </div>
      </header>

      <section id="chat-log" class="chat-log" aria-live="polite">
        <div class="msg-row assistant">
          <div class="bubble">您好！我是星辰智脑企业 AI 助手，支持实时问答、差旅制度查询与流式打字机输出。</div>
        </div>
      </section>

      <form id="chat-form" class="chat-composer">
        <textarea id="chat-input" rows="2" placeholder="输入您的问题，例如：杭州差旅住宿报销上限是多少？" required></textarea>
        <button id="send-btn" class="send-btn" type="submit">发送</button>
      </form>
    </main>
  </div>
  <script src="chat_app.js"></script>
</body>
</html>
"""

STYLES_CSS = """:root {
  --bg-page: #f4f6fb;
  --bg-sidebar: #0f172a;
  --bg-panel: #ffffff;
  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --border: #e2e8f0;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; background: var(--bg-page); color: var(--text-main); height: 100vh; }

.app-shell { display: flex; height: 100vh; }
.sidebar { width: 260px; background: var(--bg-sidebar); color: #f8fafc; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.brand { display: flex; align-items: center; gap: 12px; }
.brand-badge { width: 38px; height: 38px; border-radius: 10px; background: var(--accent); display: grid; place-items: center; font-weight: 700; }
.brand h1 { font-size: 18px; }
.brand p { font-size: 12px; color: #94a3b8; }

.primary-btn { background: var(--accent); color: #fff; border: none; border-radius: 8px; padding: 10px 14px; cursor: pointer; font-weight: 600; }
.primary-btn:hover { background: var(--accent-hover); }
.session-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.session-item { padding: 10px 12px; border-radius: 8px; font-size: 13px; background: rgba(255, 255, 255, 0.08); }

.chat-main { flex: 1; display: flex; flex-direction: column; background: var(--bg-panel); }
.chat-header { padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.chat-header h2 { font-size: 16px; }
.status-badge { font-size: 12px; color: #059669; background: #ecfdf5; padding: 4px 10px; border-radius: 999px; }

.chat-log { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.msg-row { display: flex; }
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }
.bubble { max-width: 72%; padding: 12px 16px; border-radius: 12px; line-height: 1.6; font-size: 14px; white-space: pre-wrap; }
.msg-row.user .bubble { background: var(--accent); color: #ffffff; }
.msg-row.assistant .bubble { background: #f1f5f9; color: var(--text-main); }

.chat-composer { padding: 16px 24px; border-top: 1px solid var(--border); display: flex; gap: 12px; }
.chat-composer textarea { flex: 1; resize: none; padding: 10px 14px; border: 1px solid var(--border); border-radius: 10px; font-size: 14px; }
.send-btn { background: var(--accent); color: #fff; border: none; border-radius: 10px; padding: 0 22px; font-weight: 600; cursor: pointer; }
.send-btn:disabled { opacity: 0.6; cursor: not-allowed; }
"""

CHAT_APP_JS = """// 星辰智脑 StarMind 前端交互与流式通信脚本（严格使用 textContent 防 XSS）
const API_STREAM_ENDPOINT = "/api/v1/chat/stream";

let currentSessionId = "web_session_" + Date.now();

const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const statusBadge = document.getElementById("status-badge");
const newChatBtn = document.getElementById("new-chat-btn");

function appendMessageBubble(role, initialText) {
  const row = document.createElement("div");
  row.className = "msg-row " + role;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = initialText;
  row.appendChild(bubble);
  chatLog.appendChild(row);
  chatLog.scrollTop = chatLog.scrollHeight;
  return bubble;
}

async function sendStreamingMessage(userText) {
  sendBtn.disabled = true;
  statusBadge.textContent = "思考与流式输出中...";
  appendMessageBubble("user", userText);
  const aiBubble = appendMessageBubble("assistant", "");

  try {
    const response = await fetch(API_STREAM_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: currentSessionId, message: userText }),
    });
    if (!response.ok || !response.body) {
      throw new Error("HTTP " + response.status);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\\n");
      buffer = lines.pop() || "";
      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const raw = line.slice(6).trim();
          if (!raw || raw === "[DONE]") continue;
          const payload = JSON.parse(raw);
          if (payload.delta) {
            aiBubble.textContent += payload.delta;
            chatLog.scrollTop = chatLog.scrollHeight;
          }
        }
      }
    }
    statusBadge.textContent = "就绪 · SSE 流式通道";
  } catch (err) {
    aiBubble.textContent = "请求异常，请确认 FastAPI 服务已启动：" + err.message;
    statusBadge.textContent = "连接异常";
  } finally {
    sendBtn.disabled = false;
  }
}

if (chatForm) {
  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    chatInput.value = "";
    await sendStreamingMessage(text);
  });
}

if (newChatBtn) {
  newChatBtn.addEventListener("click", () => {
    currentSessionId = "web_session_" + Date.now();
    while (chatLog.firstChild) {
      chatLog.removeChild(chatLog.firstChild);
    }
    appendMessageBubble("assistant", "已开启全新企业会话，请问有什么可以帮您？");
  });
}
"""


def build_frontend_assets(output_dir: Path) -> Dict[str, Path]:
    """将完整的企业聊天前端三件套写入目标目录并返回路径字典。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "html": output_dir / "index.html",
        "css": output_dir / "styles.css",
        "js": output_dir / "chat_app.js",
    }
    files["html"].write_text(INDEX_HTML.strip() + "\n", encoding="utf-8")
    files["css"].write_text(STYLES_CSS.strip() + "\n", encoding="utf-8")
    files["js"].write_text(CHAT_APP_JS.strip() + "\n", encoding="utf-8")
    return files


if __name__ == "__main__":
    out = Path("generated_web_demo")
    created = build_frontend_assets(out)
    for kind, path in created.items():
        print(f"已生成 [{kind.upper()}]: {path} ({path.stat().st_size} bytes)")

