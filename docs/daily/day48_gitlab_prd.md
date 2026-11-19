# STARMIND-048 · Day 48 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 48 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 7 周：Agent 工程化护栏、行业场景与多 Agent 办公助手实战） |
| **需求标题** | 阶段项目三(上)——多 Agent 智能办公助手 —— 星辰办公助手整体架构设计、专家 Agent 角色划分与 5 大企业办公工具集实现 |
| **GitLab 分支** | `feat/day48-project3-office-tools-agents` |
| **Commit 规范** | `feat(day48): 完成阶段项目三架构设计、5大企业办公工具集与三大领域专家Agent` |
| **配套课件** | `courseware/day48/index.html` |
| **配套 Notebook** | `notebooks/day48/day48_practice.ipynb` |
| **迭代快照** | `versions/day48/` |

## 1. 上下文衔接

- **承上（昨日基线）**：前面九天我们把 ReAct、LangGraph、Checkpointer/HITL、多 Agent Supervisor、MCP、Guardrails 和 Text-to-SQL 全部练熟了。从今天开始，我们要把所有技能融会贯通，打造第四阶段毕业大项目——**星辰智脑「多 Agent 智能办公助手」**！
- **启下（明日演进）**：明天（Day 49）进入阶段项目三（下）：把今天建好的 5 大工具和 3 名专家 Agent 装配进带 SQLite Checkpointer + 高危动作 HITL 人工确认的状态图编排器，并封装生产级 FastAPI 服务完成全链路联调测试！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科员工日常办公分散在 OA 审批、企业日历、企业邮箱、Confluence 知识库和外部资讯 5 个孤立系统中，完成一次“查差旅标准 -> 约评审会 -> 发邮件通知 -> 提报销单”的复合任务平均需要切换 4 个网页耗时 25 分钟。

### 核心痛点
- 多套办公系统割裂，员工频繁切换入口、重复填写会议时间与审批字段。
- 单 Agent 挂载全部办公工具极易误触发外发邮件或错提财务审批，风险不可控。
- 缺少统一的工具返回契约（`ToolResult`）与操作风险分级，后续编排层无法识别哪些动作必须人工确认。

### 迭代目标
- 完成「多 Agent 智能办公助手」整体四层架构设计（API 网关层 -> 编排与 HITL 持久层 -> 专家 Agent 层 -> 企业工具与数据层）。
- 实现 5 个完整可本地运行的企业办公工具：`calendar_tool`、`email_draft_tool`、`web_search_tool`、`doc_rag_tool`、`approval_tool`。
- 实现 3 位领域专家 Agent：`SchedulerAgent`（日程/邮件）、`KnowledgeAgent`（文档 RAG/资讯搜索）、`ApprovalAgent`（审批单），并输出明确的风险等级标记。

### 验收标准
- [x] 日程工具支持检测会议室/参会人时间冲突，冲突时拒绝预定并给出冲突详情；空闲时段预定成功。
- [x] 邮件工具校验收件人邮箱格式合法性并生成草稿（标记为 `HIGH_RISK`，等待人工确认后才真正外发）。
- [x] 审批工具支持请假与报销单创建，金额 > 5000 元自动标记 `HIGH_RISK` 需总监人工复核；文档 RAG 与搜索工具可精准召回相关条目，所有单测本地 100% 通过。

### 非功能指标
- 所有工具返回统一 `ToolResult(ok, tool_name, risk_level, data, message)`，便于上层编排器与 Trace 统一观测。
- 所有状态数据保存在独立实例对象（`OfficeWorkspaceStore`）中，确保并发测试与多租户隔离互不干扰。

## 3. 架构设计与交付清单

阶段项目三「多 Agent 智能办公助手」是星辰智脑中台最具代表性的综合工程项目，采用经典的**四层清晰解耦架构**：

1. **入口与安全网关层（Day 49 落地）**：FastAPI REST 接口 + `GuardrailsEngine`（Prompt 注入拦截 + 输出 PII 脱敏）。
2. **多 Agent 编排与持久层（Day 49 落地）**：Supervisor 意图路由 + SQLite Checkpointer + 高危动作 `HITL` 人工确认中断/恢复。
3. **领域专家 Agent 层（今天落地）**：按企业职能拆分为三位职责清晰、工具权限严格隔离的专家：
   - `KnowledgeAgent`（只读低风险）：绑定 `doc_rag_tool` + `web_search_tool`，负责制度查询与行业情报检索；
   - `SchedulerAgent`（写操作混合风险）：绑定 `calendar_tool`（日程冲突校验预定）+ `email_draft_tool`（邮件草拟，外发标记 `HIGH_RISK`）；
   - `ApprovalAgent`（强合规高风险）：绑定 `approval_tool`，负责请假/报销单草拟与提交，大额报销（> ¥5000）自动升级为 `HIGH_RISK` 强制人工复核。
4. **企业工具与工作区存储层（今天落地）**：全部 5 个工具共享统一 `ToolResult` 数据契约与可注入的 `OfficeWorkspaceStore`，既杜绝全局可变状态污染单测，又方便明天无缝接入编排器和 FastAPI。

### 当日交付代码文件
- `src/day48_office_tools.py`：步骤一：实现 5 大企业办公工具集与统一工作区底座
- `src/day48_office_agents.py`：步骤二：实现三大领域专家 Agent（知识/日程邮件/审批）与权限边界

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
工具层与专家 Agent 层切分得非常干净，`OfficeWorkspaceStore` 可实例化注入设计保证了单测之间 0 污染，明天接 FastAPI 极其丝滑！

### Reviewer：阿杰 (后端工程师)（Approved）
日历工具把 10-11 点和 11-12 点的相邻边界测进去了，点赞！这种边界最容易在线上被吐槽。

### Reviewer：林产品 (产品经理)（Approved）
超过 5000 元报销和对外发邮件自动打 `HIGH_RISK` 标签完全符合财务与信息安全部要求，期待明天联调上线！

