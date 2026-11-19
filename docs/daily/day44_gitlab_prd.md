# STARMIND-044 · Day 44 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 44 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | MCP 与 Agent 生态 —— Model Context Protocol 协议详解、JSON-RPC 2.0 自研 MCP Server/Client 与长短期记忆架构 |
| **GitLab 分支** | `feat/day44-mcp-jsonrpc-and-memory` |
| **Commit 规范** | `feat(day44): 实现JSON-RPC 2.0 MCP Server/Client与SQLite长短期双层记忆引擎` |
| **配套课件** | `courseware/day44/index.html` |
| **配套 Notebook** | `notebooks/day44/day44_practice.ipynb` |
| **迭代快照** | `versions/day44/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 43）我们组建了多 Agent 行业研究团队，解决了复杂任务的角色拆分问题。但在接入公司内部的 Jira、CRM、GitLab、企业微信等十几个系统时，阿杰抱怨道：难道每个 Agent 项目都要把这些工具重新封装一遍吗？
- **启下（明日演进）**：明天（Day 45）我们将迎来第六周综合实战周测，同时拆解 Dify / Coze 低代码平台的 DSL 工作流引擎，帮你建立“什么时候用低代码、什么时候必须代码自研”的架构选型矩阵。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科内部已有 3 个不同业务线的 Agent 团队，分别重复编写了访问员工通讯录、查询工单系统和读取制度文档的工具代码，接口变更时三边同时报错。同时，员工反馈每次新开对话都要重复介绍自己的部门、常用汇报风格，缺乏跨会话记忆。

### 核心痛点
- 工具封装与具体 Agent 框架强耦合，存在严重的 M×N 重复对接与维护灾难。
- 缺少标准的工具发现（`tools/list`）与只读资源暴露（`resources/read`）通信协议。
- Agent 只有单轮对话上下文，重启或新开会话后完全遗忘用户的长期偏好与历史关键事实。

### 迭代目标
- 掌握 MCP 架构（Host / Client / Server）及底层 JSON-RPC 2.0 请求-响应-错误码规范。
- 零外部端口依赖，纯 Python 实现标准 JSON-RPC 2.0 的 `MCPServer` 与 `MCPClient`，支持 `initialize`、`tools/list`、`tools/call`、`resources/list`、`resources/read`。
- 实现 Agent 双层记忆系统：`ShortTermMemory`（滑动窗口防上下文溢出）+ `SQLiteLongTermMemory`（跨会话事实与偏好持久化与相关性召回）。

### 验收标准
- [x] MCP Client 与 MCP Server 握手后能动态发现工具 Schema、调用工具并返回符合 JSON-RPC 2.0 结构的响应。
- [x] 调用未知 JSON-RPC 方法时返回标准错误码 `-32601`（Method not found），参数非法时返回 `-32602`。
- [x] 长期记忆落库 SQLite 后，新建记忆实例仍能按 `user_id` 和关键词召回历史偏好与事实，所有单测本地 100% 通过。

### 非功能指标
- MCP Server 工具执行异常必须封装为 JSON-RPC error 或 `isError: true`，严禁裸抛栈信息导致协议通道断裂。
- 短期记忆裁剪必须严格保留 System Prompt 或最新 N 轮对话，防止 Token 无限膨胀。

## 3. 架构设计与交付清单

MCP（Model Context Protocol）本质上是一个基于 **JSON-RPC 2.0** 的有状态应用层协议，把 AI 应用解耦为三个角色：**Host**（宿主应用，如 IDE 或星辰办公助手）、**Client**（维护 1:1 协议连接的客户端）和 **Server**（轻量级能力提供方，暴露三大原语：`Tools` 可执行动作、`Resources` 只读数据文档、`Prompts` 复用提示词模板）。在传输层上，本地工具通常走 `stdio`（标准输入输出换行分隔 JSON），远程跨团队服务走 `Streamable HTTP / SSE`。

与 MCP 互补的是 Agent 的 **记忆架构（Memory Architecture）**。参考认知科学，生产级 Agent 至少需要两层记忆：
1. **短期记忆（Short-Term / Working Memory）**：绑定当前 `session_id`，存放最近 K 轮对话。随着对话拉长，必须通过滑动窗口（Sliding Window）或滚动摘要（Rolling Summary）把历史压缩在模型上下文窗口的安全水位内。
2. **长期记忆（Long-Term Memory）**：绑定 `user_id` 或 `tenant_id`，持久化在 SQLite/PostgreSQL/向量库中，跨会话保留“用户偏好（如：汇报喜欢用三点式结论）”和“关键业务事实（如：负责华东区大客户）”。每次新对话开始前，Agent 自动按当前问题检索 Top-K 长期记忆注入 System Prompt，实现“越用越懂你”的企业级体验。

### 当日交付代码文件
- `src/day44_mcp_protocol.py`：步骤一：严格遵循 JSON-RPC 2.0 的自研 MCP Server 与 MCP Client
- `src/day44_agent_memory.py`：步骤二：实现 Agent 短期滑动窗口记忆 + SQLite 跨会话长期记忆

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
把 JSON-RPC 2.0 错误码 `-32601` / `-32602` 严格写进单测里非常专业！这样以后不管对接 Claude Desktop 还是自研网关都不会因为协议细节翻车。

### Reviewer：阿杰 (后端工程师)（Approved）
长期记忆的 `ON CONFLICT DO UPDATE` 很细心，避免了同一条用户偏好被反复插入十几次。

### Reviewer：林产品 (产品经理)（Approved）
跨会话记住领导喜欢“三点式精简汇报”这个功能太戳痛点了，一定要整合进后期的智能办公助手项目里！

