# STARMIND-024 · Day 24 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 24 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 4 周：第4周：全栈 Web 聊天应用与 FastAPI 后端工程） |
| **需求标题** | FastAPI 后端开发(下)+数据库：SSE流式、CORS、SQLAlchemy持久化与全栈联调 —— 第二阶段收官里程碑！打造可持久化、支持 SSE 流式打字机的「网页版星辰 ChatGPT 克隆」 |
| **GitLab 分支** | `feat/day24-fastapi-sse-sqlite` |
| **Commit 规范** | `feat(day24): 实现SSE流式接口、CORS跨域、SQLite+SQLAlchemy对话持久化与网页版ChatGPT全栈联调` |
| **配套课件** | `courseware/day24/index.html` |
| **配套 Notebook** | `notebooks/day24/day24_practice.ipynb` |
| **迭代快照** | `versions/day24/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 23）我们用 FastAPI + Pydantic v2 把星辰智脑封装成了标准 REST API 并跑通了 `TestClient` 测试。但距离真正的网页版 ChatGPT 还差最后三块拼图：第一，重启服务后内存里的聊天记录全没了；第二，接口还是同步一次性返回，没有 SSE 流式打字机推送；第三，前后端分离部署时会遇到浏览器 CORS 跨域拦截！
- **启下（明日演进）**：明天（Day 25）我们将正式迈入第三阶段——LangChain 与企业级 RAG 开发！我们会把这两周手写的模型调用、Prompt 模板与工具调用全面升级为 LangChain 标准化抽象层，并构建企业级知识库问答系统。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑 V1.0 网页版工作台需要正式交付内测：员工在浏览器打开即可进行流式对话，刷新页面或重启后端后历史会话完整保留，同时允许公司内部其他前端域名（如 OA 门户）安全跨域调用 API。

### 核心痛点
- 内存字典存储聊天记录在进程重启或多 Worker 部署时全部丢失。
- 同步接口等待时间长，缺少符合标准的 `text/event-stream` SSE 流式端点。
- 前端独立域名访问后端时触发浏览器 CORS 预检（OPTIONS）拦截，无法联调。

### 迭代目标
- 使用 SQLAlchemy 2.x 现代声明式 ORM（`DeclarativeBase` + `Mapped` + `mapped_column`）设计 `ChatSession` 与 `ChatMessage` 一对多数据表并实现 CRUD 仓库层。
- 在 FastAPI 中配置 `CORSMiddleware`，托管企业聊天前端页面 `/`，并实现 `POST /api/v1/chat/stream` SSE 流式对话接口。
- 流式响应完成后自动将用户提问与 AI 完整回答持久化至 SQLite，提供历史会话列表查询与级联删除接口，并完成全栈 `TestClient` 端到端验收。

### 验收标准
- [x] SQLite 数据库落盘后，即使重新创建新的 `create_app(db_url)` 实例，仍能完整读出此前的会话与消息历史。
- [x] `POST /api/v1/chat/stream` 返回 `Content-Type: text/event-stream`，产出多帧合法 JSON `data:` 事件并以 `data: [DONE]` 收尾。
- [x] 带 `Origin` 请求头的跨域请求能正确获得 `access-control-allow-origin` 响应头，且 `GET /` 返回可交互的星辰智脑 HTML 页面。

### 非功能指标
- 兼容 SQLAlchemy 2.x 规范，SQLite 连接开启 `check_same_thread=False` 以适配 FastAPI 线程池。
- 删除会话时通过 `cascade='all, delete-orphan'` 自动级联清理关联消息，杜绝孤儿脏数据。

## 3. 架构设计与交付清单

这是第二阶段最完整的一套**企业级全栈 AI Web 架构**：
1. **数据持久化层（`day24_database.py`）**：采用 SQLAlchemy 2.x 现代 ORM，`ChatSession`（主键 `id`、标题 `title`、创建时间 `created_at`）与 `ChatMessage`（主键 `id`、外键 `session_id`、角色 `role`、内容 `content`、创建时间 `created_at`）构成一对多关系。通过仓库类 `ChatRepository` 屏蔽底层 SQL 细节，日后从 SQLite 平滑迁移到生产 PostgreSQL 只需改一行连接串 `DATABASE_URL`！
2. **SSE 流式推送与落盘时机**：`POST /api/v1/chat/stream` 先把用户的提问写入 SQLite，然后返回一个 `StreamingResponse(event_generator(), media_type='text/event-stream')`。生成器在逐片 `yield f'data: {json}\n\n'` 的同时将片段缓存在列表里，待全部推送完毕后把完整回复写入 SQLite，最后发送 `data: [DONE]\n\n`。
3. **CORS 跨域与前后端联调**：配置 `CORSMiddleware` 允许受控前端源访问，并在 `GET /` 直接输出内置联调版星辰智脑 HTML 页面，做到启动即用、开箱联调。

### 当日交付代码文件
- `src/day24_database.py`：步骤一：实现 SQLAlchemy 2.x + SQLite 对话历史持久化层
- `src/day24_chatgpt_backend.py`：步骤二：实现 SSE 流式接口、CORS 跨域与网页版 ChatGPT 克隆全栈后端

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
用 `tmp_path` 创建真实 SQLite 文件并实例化两个独立的 FastAPI App 来验证「跨重启持久化」，这个测试思路就是生产级标准！

### Reviewer：阿杰 (后端工程师)（Approved）
SSE 响应头加了 `X-Accel-Buffering: no`，明天上预发 Nginx 就不会卡顿了。

### Reviewer：林产品 (产品经理)（Approved）
刚刚在内网打开网页版星辰智脑试用了一把，流式打字机 + 刷新页面历史不丢，老板看了直接竖大拇指！

