# STARMIND-023 · Day 23 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 23 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 4 周：第4周：全栈 Web 聊天应用与 FastAPI 后端工程） |
| **需求标题** | FastAPI 后端开发(上)：路由设计、Pydantic v2 校验与 REST API 实战 —— 把 AI 对话能力封装为生产级 HTTP 微服务，并用 FastAPI TestClient 实现零端口自动化测试 |
| **GitLab 分支** | `feat/day23-fastapi-rest-chat` |
| **Commit 规范** | `feat(day23): 使用FastAPI与Pydantic v2封装星辰智脑REST对话API并完成TestClient回归测试` |
| **配套课件** | `courseware/day23/index.html` |
| **配套 Notebook** | `notebooks/day23/day23_practice.ipynb` |
| **迭代快照** | `versions/day23/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 22）我们用一天时间速成了企业级聊天前端，产出了 `index.html`、`styles.css`、`chat_app.js` 并通过了 DOM 与防 XSS 校验。但现在前端页面发出的 `/api/v1/chat` 请求还没有真实的后端接口来承接！
- **启下（明日演进）**：明天（Day 24）将是第二阶段的收官大戏——FastAPI 后端开发（下）+ 数据库：我们将接入 SSE 流式接口、CORS 跨域、SQLite + SQLAlchemy 对话历史持久化，彻底跑通「网页版星辰 ChatGPT 克隆」前后端联调！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑需要向前端网页和内部业务系统（OA、钉钉机器人、客服工作台）暴露统一、强类型、文档自动化的 RESTful HTTP API，替代此前的本地 Python 函数调用。

### 核心痛点
- 外部调用方经常传入空消息、超长文本或非法 `temperature=5.0`，若无统一 Schema 校验极易引发后端 500 崩溃。
- 模型列表查询、会话历史查询与对话发送缺少规范的 REST URL 与 HTTP 状态码约定。
- 传统接口测试需要手动启动 Uvicorn 再用 Postman 点点点，无法纳入 GitLab CI 自动化回归。

### 迭代目标
- 使用 Pydantic v2 定义严格的请求/响应模型：`ChatRequest`、`ChatResponse`、`ModelInfo`、`SessionDetailResponse`，包含字段范围约束与自定义 `field_validator`。
- 使用 FastAPI 构建完整 REST API：`/health`、`/api/v1/models`（查询参数过滤）、`/api/v1/chat`（POST 对话）、`/api/v1/sessions/{session_id}`（路径参数查询与删除）。
- 使用 `fastapi.testclient.TestClient` 编写完整 pytest 自动化测试，覆盖正常 200、参数非法 422、资源不存在 404 以及多轮会话状态校验。

### 验收标准
- [x] 非法入参（空消息、`temperature > 2.0`、未支持的 `model`）自动返回 HTTP 422 与清晰错误字段定位。
- [x] 查询不存在的 `session_id` 返回标准 HTTP 404 JSON 错误，而非 500 堆栈泄露。
- [x] `/api/v1/models?provider=DeepSeek` 查询参数能精准筛选模型列表，所有 `TestClient` 用例 100% 通过。

### 非功能指标
- 严格使用 Pydantic v2 现代语法（`field_validator`、`ConfigDict`），杜绝已废弃的 v1 `@validator` 写法。
- 通过 `create_app()` 工厂函数创建 FastAPI 实例，确保每个测试用例拥有干净隔离的会话状态。

## 3. 架构设计与交付清单

在企业级 Python 后端架构中，清晰的模块分层能避免「所有代码堆在一个 `main.py` 里」的泥球灾难：
1. **契约层（`day23_schemas.py`）**：用 Pydantic v2 定义所有外部可见的请求体与响应体。Pydantic v2 底层由 Rust 编写，校验吞吐比 v1 快 5~50 倍；FastAPI 会根据这些模型自动生成 OpenAPI 3.1 规范与 `/docs` 调试页。
2. **应用工厂模式（`create_app()`）**：很多教程把内存字典 `SESSIONS = {}` 写成模块全局变量，导致 pytest 跑第二个用例时被第一个用例的数据污染！使用 `create_app()` 工厂函数在实例内初始化独立状态（或注入依赖），测试隔离极其干净。
3. **标准 HTTP 语义**：成功查询/对话返回 `200 OK`，资源不存在抛出 `HTTPException(status_code=404)`，入参违反 Pydantic 规则由 FastAPI 自动返回 `422 Unprocessable Entity`。

### 当日交付代码文件
- `src/day23_schemas.py`：步骤一：使用 Pydantic v2 定义星辰智脑 REST API 强类型请求与响应模型
- `src/day23_fastapi_app.py`：步骤二：使用 FastAPI 封装星辰智脑 RESTful 对话微服务（工厂模式）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
全部采用 Pydantic v2 现代语法 + `create_app()` 工厂隔离，单测把 200/404/422 全覆盖到了，非常干净。

### Reviewer：阿杰 (后端工程师)（Approved）
现在内存字典 `sessions` 重启服务就会丢数据，明天 Day 24 我们立刻换成 SQLite + SQLAlchemy 持久化！

### Reviewer：林产品 (产品经理)（Approved）
Swagger `/docs` 自动把每个参数范围和示例都列出来了，第三方业务线对接方便太多了。

