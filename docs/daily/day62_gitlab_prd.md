# STARMIND-062 · Day 62 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 62 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 9 周：星辰智脑毕业设计全栈开发与上线） |
| **需求标题** | 毕业设计开发 Day 4：FastAPI 全量接口与前端控制台联调 —— REST + SSE 流式对话接口、X-Trace-Id 链路中间件、审批工作台接口与前端流式解析联调 |
| **GitLab 分支** | `feat/day62-capstone-fastapi-console` |
| **Commit 规范** | `feat(day62): 实现FastAPI全量REST/SSE接口并完成前端控制台流式联调` |
| **配套课件** | `courseware/day62/index.html` |
| **配套 Notebook** | `notebooks/day62/day62_practice.ipynb` |
| **迭代快照** | `versions/day62/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们完成了星辰智脑的多 Agent 编排、MCP 工具与 HITL 人工审批引擎，今天把它暴露为标准 Web API 并完成前后端联调。
- **启下（明日演进）**：明天（Day 63）进入毕业设计质量保障阶段：自动化测试、Ragas 量化评估报告、高并发压测与 Token 成本优化。

## 2. 业务需求说明 (PRD)

### 业务背景
前端管理控制台（Next.js/React）需要一套契约清晰、支持 SSE 打字机流式渲染、支持审批单交互与知识库动态录入的后端 HTTP 接口。

### 核心痛点
- 同步接口等待大模型生成 10 秒以上，前端长时间白屏，用户体验差。
- 前后端联调排查问题时缺少统一请求追踪 ID，难以把浏览器报错和后端日志关联起来。
- 接口入参不做严格 Pydantic 校验，空提问或负数金额直接打穿底层服务。

### 迭代目标
- 基于 FastAPI 实现全量生产级 REST + SSE 接口，并挂载全局 `X-Trace-Id` 中间件。
- 实现 SSE 事件流协议（`meta` / `delta` / `done` 事件）与前端流式解析器。
- 通过 FastAPI `TestClient` 完成全接口端到端自动化联调验证。

### 验收标准
- [x] 所有响应均自动携带 `X-Trace-Id` 响应头；`/healthz` 与 `/readyz` 返回 200。
- [x] `/api/v1/chat/stream` 返回 `text/event-stream` 且前端解析器可完整拼装回复与事件类型。
- [x] 支持动态录入新知识文档并立即检索命中，支持高危报销挂起并通过 `/api/v1/approvals/{ticket_id}` 审批。

### 非功能指标
- 使用 FastAPI `TestClient` 零外部端口依赖完成全量接口自动化验收。

## 3. 架构设计与交付清单

前后端联调层遵循 **强类型契约（OpenAPI/Pydantic）+ 统一链路透传 + 标准 SSE 分帧** 三原则：
1. **全局 Trace 中间件**：每个 HTTP 请求进入 FastAPI 时，若请求头未带 `X-Trace-Id`，自动生成 `tr-xxxxxxxx` 并写回响应头，前后端排障一秒定位。
2. **SSE 事件分帧协议**：流式接口 `/api/v1/chat/stream` 依次推送 `event: meta`（路由与会话元信息）、多条 `event: delta`（逐片文本增量）与 `event: done`（终态与审批单号），响应头显式设置 `Cache-Control: no-cache` 与 `X-Accel-Buffering: no` 防止 Nginx 缓冲。
3. **端到端联调闭环**：控制台客户端封装知识库管理、流式对话解析与审批操作，可直接对接真实线上地址或本地 FastAPI `TestClient`。

### 当日交付代码文件
- `src/day62_api_server.py`：步骤一：实现星辰智脑 FastAPI 全量 REST + SSE 后端服务
- `src/day62_console_client.py`：步骤二：实现前端控制台 SSE 流式解析器与全接口联调脚本

## 4. GitLab Merge Request Code Review 记录

### Reviewer：林产品（Approved）
SSE 接口把 `meta`/`delta`/`done` 拆得很清爽，前端一接到 `done.ticket_id` 就能立刻弹出'审批进度卡片'。

### Reviewer：老陈（Approved）
重复审批返回 HTTP 409 Conflict 很规范，比笼统返回 500 强太多了。

