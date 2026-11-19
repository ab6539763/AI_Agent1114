# STARMIND-061 · Day 61 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 61 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 9 周：星辰智脑毕业设计全栈开发与上线） |
| **需求标题** | 毕业设计开发 Day 3：核心多 Agent 主链路（MCP 工具 + 多轮记忆 + 人工审批） —— Supervisor 路由调度、MCP 标准工具注册中心、滑动窗口记忆与高危操作 HITL 审批门禁 |
| **GitLab 分支** | `feat/day61-capstone-multi-agent-hitl` |
| **Commit 规范** | `feat(day61): 实现多Agent编排主链路(MCP工具+多轮记忆+人工审批HITL)` |
| **配套课件** | `courseware/day61/index.html` |
| **配套 Notebook** | `notebooks/day61/day61_practice.ipynb` |
| **迭代快照** | `versions/day61/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们打通了星辰智脑的混合检索 RAG + Rerank + 引用溯源引擎，今天正式进入核心智能体主链路开发。
- **启下（明日演进）**：明天（Day 62）我们把 RAG 与多 Agent 引擎统一封装为 FastAPI 全量 REST/SSE 接口，并与前端控制台完成全链路联调。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑不仅需要回答企业知识库问题，还要能代表员工执行请假、差旅报销提交、IT 工单派发等操作，并在多轮对话中记住上下文、对高风险操作强制引入人工审批。

### 核心痛点
- 单 Prompt 大杂烩既要查知识库又要调工具，指令冲突严重、幻觉率飙升。
- 工具调用缺少统一 Schema 校验与审计日志，参数传错直接导致业务接口报错。
- 高金额报销或高危运维操作若自动放行，存在极大资金与生产安全风险。

### 迭代目标
- 实现 MCP 风格工具注册中心：统一声明工具名、参数 Schema、风险等级与执行审计。
- 实现多轮会话记忆管理器：支持滑动窗口裁剪与历史摘要压缩，避免上下文超长。
- 实现 Supervisor 多 Agent 编排器与 HITL 审批状态机：低危自动执行，高危挂起待审批并支持批准/驳回恢复。

### 验收标准
- [x] 知识问答类请求准确路由至 `knowledge_agent`，业务办理类请求路由至 `action_agent`。
- [x] 金额超过 2000 元的报销申请自动进入 `PENDING_APPROVAL`，批准后完成执行并写入审计轨迹，驳回则终止。
- [x] 多轮记忆自动保留最近 N 轮对话并将更早历史压缩为摘要。

### 非功能指标
- 所有状态流转确定性可复现，pytest 100% 离线通过。

## 3. 架构设计与交付清单

星辰智脑核心 Agent 主链路采用 **Supervisor 分发 + MCP 标准化工具层 + 状态机 HITL 审批门禁** 架构：
1. **MCP 工具抽象层（Tool Registry）**：每个工具以统一契约注册（名称、必填参数、风险策略函数 `requires_approval(args)`、执行器），调用前后统一记录耗时与入参出参审计日志。
2. **分级会话记忆（Sliding Window + Summary）**：每个 `session_id` 保留最近 `max_turns` 轮原始对话，超出部分自动折叠进滚动摘要，既不丢失前情又严控 Token 账单。
3. **HITL 中断与恢复（Interrupt & Resume）**：当 `ActionAgent` 检测到高危工具调用（如报销金额 > 2000 元），不直接执行，而是持久化一张 `ApprovalTicket(status='PENDING')` 返回给前端；管理员通过 `/approvals/{ticket_id}` 审批通过后，编排器再取出挂起上下文完成最终执行。

### 当日交付代码文件
- `src/day61_mcp_and_memory.py`：步骤一：实现 MCP 风格工具注册中心与多轮滑动窗口记忆
- `src/day61_multi_agent_hitl.py`：步骤二：实现 Supervisor 多 Agent 编排器与 HITL 人工审批状态机

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
审批单加上终态幂等校验（`ticket.status != 'PENDING'` 抛异常）非常老道！线上前端连点两次审批按钮的坑被你提前堵死了。

### Reviewer：阿杰（Approved）
MCPToolRegistry 里的 `audit_log` 明天可以顺手落到 Day 59 的 SQLite 审计表里，方便查账。

