# STARMIND-049 · Day 49 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 49 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 7 周：Agent 工程化护栏、行业场景与多 Agent 办公助手实战） |
| **需求标题** | 阶段项目三(下)——多 Agent 智能办公助手 —— LangGraph 多 Agent 编排、高危动作人工确认中断恢复与 FastAPI 生产级接口联调 |
| **GitLab 分支** | `feat/day49-project3-langgraph-hitl-fastapi` |
| **Commit 规范** | `feat(day49): 完成多Agent智能办公助手状态机编排、HITL中断恢复与FastAPI端到端联调` |
| **配套课件** | `courseware/day49/index.html` |
| **配套 Notebook** | `notebooks/day49/day49_practice.ipynb` |
| **迭代快照** | `versions/day49/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 48）我们完成了阶段项目三（上）：落地了 5 大企业办公工具、统一 `ToolResult` 契约与三大领域专家 Agent。今天我们把它们全部串联进带持久化断点与安全护栏的状态图编排器，并对外暴露生产级 FastAPI 服务！
- **启下（明日演进）**：明天（Day 50）我们将迎来阶段项目三的正式答辩评审、代码重构优化与第四阶段（Day 39 ~ 50）Agent 中台架构演进复盘，为跨入第五阶段“模型微调与本地私有化推理部署”做好冲刺准备。

## 2. 业务需求说明 (PRD)

### 业务背景
在完成工具层与专家 Agent 层搭建后，星辰数科需要一套可对外提供标准 REST API 的智能办公编排服务，对接前端办公工作台与钉钉审批卡片，确保普通查询秒级直出、高危操作（发外部邮件、大额报销）强制挂起等待人工点击确认。

### 核心痛点
- 普通咨询与高危写操作混在同一个接口里，如果缺少异步中断落库机制，无法支撑跨分钟/跨小时的人工审批体验。
- 用户若在审批卡片点击“拒绝”，系统必须安全取消待发邮件或待审单据，严禁残留脏状态或误执行。
- 缺少端到端 HTTP 联调测试，前端对接时常遇到字段格式不一致或 500 未捕获异常。

### 迭代目标
- 构建 `OfficeAssistantOrchestrator`：整合 Input Guardrail、Supervisor 路由、三大专家执行、SQLite Checkpointer 状态持久化、HITL 中断恢复与 Output PII 脱敏。
- 基于 FastAPI + Pydantic 封装生产级办公助手 API（`/api/v1/office/chat`、`/api/v1/office/tasks/{thread_id}/confirm`、`/api/v1/office/tasks/{thread_id}`、`/api/v1/health`）。
- 使用 `fastapi.testclient.TestClient` 完成四条端到端联调场景验收：低风险直出、高危挂起+人工同意恢复、高危挂起+人工拒绝取消、Prompt 注入安全拦截。

### 验收标准
- [x] 低风险制度查询通过 `/api/v1/office/chat` 直接返回 `status='COMPLETED'` 与准确制度内容。
- [x] 发起对外发邮件或 >5000 元报销请求时返回 `status='WAITING_CONFIRMATION'` 与 `thread_id`；调用 `/confirm` 传 `approved=True` 后恢复执行并返回 `COMPLETED`，传 `approved=False` 后返回 `REJECTED`。
- [x] 重复对已结束的 `thread_id` 调用 `/confirm` 返回 HTTP 409 Conflict 防止幂等重放，所有联调测试本地 100% 通过。

### 非功能指标
- 使用工厂函数 `create_office_app(db_path=...)` 创建 FastAPI 应用，确保单测与生产环境存储彻底隔离。
- 每次请求必须返回 `trace_id`、`routed_agent` 与 `latency_ms` 便于前端排查与监控埋点。

## 3. 架构设计与交付清单

把多 Agent 系统封装成生产级 Web 服务时，最核心的架构挑战是**“异步长周期 HITL 状态机”与“无状态 HTTP 请求”的桥接**。

我们采用 **Thread-Scoped Checkpointer + 显式确认端点** 模式彻底解决这一难题：
1. **请求入口（`POST /api/v1/office/chat`）**：
   - 先过 `Input Guardrail`（拦截 Prompt 注入直接返回 `status='BLOCKED'`）；
   - `Supervisor` 根据意图路由到 `knowledge_agent` / `scheduler_agent` / `approval_agent`；
   - 若专家返回的是低风险结果（如查制度、预定空闲会议），经过 `Output PII Redaction` 后直接落库为 `COMPLETED` 并同步返回；
   - 若专家触发高危动作（如外发邮件草稿、>5000 元报销单），编排器自动将完整上下文与待执行动作 (`pending_action`) 持久化到 SQLite，状态置为 `WAITING_CONFIRMATION`，立刻释放 HTTP 连接并返回 `thread_id` 给前端渲染审批确认卡片。
2. **人工确认恢复（`POST /api/v1/office/tasks/{thread_id}/confirm`）**：
   - 服务端先从 SQLite 校验任务是否存在（不存在返回 `404`）以及是否处于 `WAITING_CONFIRMATION`（已处理返回 `409 Conflict` 防止手抖重复提交）；
   - 人工选择 `approved=True`：执行最终提交（标记邮件 `SENT` 或审批单 `APPROVED_SUBMITTED`），更新快照为 `COMPLETED`；
   - 人工选择 `approved=False`：执行安全撤销（标记 `CANCELLED`），更新快照为 `REJECTED`。

### 当日交付代码文件
- `src/day49_office_orchestrator.py`：步骤一：实现带 SQLite Checkpointer 与 HITL 中断恢复的多 Agent 办公编排器
- `src/day49_office_api.py`：步骤二：封装生产级 FastAPI 接口服务与 Pydantic 强类型契约

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
端到端 `TestClient` 把低风险、PII 脱敏、HITL 同意、HITL 拒绝、409 防重放、注入拦截和 404 全覆了一遍，这就是生产级交付的标准！

### Reviewer：阿杰 (后端工程师)（Approved）
`create_office_app` 工厂模式配 `tmp_path` 太清爽了，整个联调单测跑完不到 0.2 秒。

### Reviewer：林产品 (产品经理)（Approved）
前端同事已经拿 Swagger 文档对接好 `/chat` 和 `/confirm` 了，明天项目三答辩绝对惊艳全场！

