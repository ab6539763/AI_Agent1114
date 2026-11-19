# STARMIND-041 · Day 41 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 41 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | LangGraph 入门（重点） —— 状态机与图编排：用 StateGraph 重写 ReAct Agent 并打造带人工审批节点的企业工作流 |
| **GitLab 分支** | `feat/day41-langgraph-state-machine` |
| **Commit 规范** | `feat(day41): 实现StateGraph核心状态图引擎、Mermaid/ASCII可视化与审批流工作流` |
| **配套课件** | `courseware/day41/index.html` |
| **配套 Notebook** | `notebooks/day41/day41_practice.ipynb` |
| **迭代快照** | `versions/day41/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 40）我们深入实现了 `@tool` 装饰器和 `AgentExecutor`，但在结尾我们发现黑盒循环在面对“确定性业务规则 + 自由推理 + 人工审批分支”的混合场景时根本无法精细控场。
- **启下（明日演进）**：明天（Day 42）我们进入 LangGraph 进阶：给状态图加上 SQLite Checkpointer 断点持久化、真正的 `interrupt_before` 异步人工审批恢复、Subgraph 子图封装，以及 Fan-out/Fan-in 并行写长文 Agent。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科 IT 采购与运维系统准备接入星辰智脑：员工提出设备采购或资料查询需求时，系统既要具备 ReAct 自主查库存/查价格的能力，又要对超过 5000 元的采购单强制路由到总监人工审批节点，严禁大模型绕过审批直接下单。

### 核心痛点
- 纯 `AgentExecutor` 黑盒循环无法强制保证“高金额必经审批节点”，仅靠 Prompt 约束存在被提示词注入绕过的合规风险。
- 复杂业务链路缺乏可视化拓扑图，产品经理与研发评审流程时沟通成本极高。
- 状态散落在局部变量里，节点之间传递字段容易互相覆盖或丢失历史消息。

### 迭代目标
- 理解有向循环图（Cyclic State Machine）相比 DAG 流水线的架构优势。
- 实现 100% 对齐 LangGraph 核心语义的 `StateGraph` 引擎（`START`/`END`、`add_node`、`add_edge`、`add_conditional_edges`、Reducer 状态合并、`draw_mermaid`、`draw_ascii`）。
- 使用状态图分别实现：1）循环版 ReAct Agent；2）带大小额条件路由与人工审批节点的企业采购工作流。

### 验收标准
- [x] `StateGraph` 支持条件边动态路由与带最大步数保护的循环边，且能同时导出合法的 Mermaid 语法与清晰的 ASCII 终端流程图。
- [x] ReAct 状态图能完成 `agent -> tools -> agent -> END` 的闭环推理。
- [x] 采购审批状态图对金额 <= 5000 元走 `auto_approve`，金额 > 5000 元强制路由到 `human_approval` 节点并按审批结果流向 `execute_order` 或 `reject_notify`。

### 非功能指标
- 节点函数必须保持无副作用的状态增量返回风格（返回 `dict` 补丁，由引擎按 Reducer 合并）。
- 图编译期必须校验所有边的起点/终点节点均已注册，提前暴露配置错误。

## 3. 架构设计与交付清单

LangGraph 的核心思想源自 Google Pregel 分布式图计算模型与经典有限状态机（FSM）：将整个 Agent 应用抽象为一个**显式状态驱动的有向图（Stateful Cyclic Graph）**。

相比 `AgentExecutor` 的“全权放手”，LangGraph 实现了工业界梦寐以求的 **可控自主性（Controlled Autonomy）**：
1. **全局状态与 Reducer 机制**：整个图维护一份强类型 `State`（在真实 LangGraph 中使用 `TypedDict` + `Annotated[list, operator.add]`）。每个节点只接收当前 `state`，返回一个局部更新字典 `update: dict`。对于普通字段采用覆盖（Overwrite），对于 `messages`、`audit_logs` 这类列表字段则采用追加（Reducer Merge），彻底避免节点间误覆盖历史记录。
2. **确定性边与条件边分离**：如果 A 节点干完活**必须**去 B 节点（例如工具执行完必须回到大脑节点汇总），就用确定性边 `add_edge('tools', 'agent')`；如果下一站取决于运行时数据（例如“模型是否发起了工具调用”、“采购金额是否超过 5000 元”），就用条件边 `add_conditional_edges(source, router_fn, path_map)`。把合规红线写在 `router_fn` 的 Python 代码里，比在 Prompt 里求大模型“千万别绕过审批”可靠一万倍！
3. **编译期静态检查与图可视化**：`graph.compile()` 阶段会扫描所有注册边，防止拼错节点名导致线上跑一半报错；同时因为拓扑结构显式存储在图对象中，随时可以调用 `draw_mermaid()` 生成文档图，或 `draw_ascii()` 在终端里直接打印拓扑结构。

### 当日交付代码文件
- `src/day41_state_graph.py`：步骤一：实现 StateGraph 状态图核心引擎与双格式可视化
- `src/day41_react_and_approval.py`：步骤二：用状态图重写 ReAct Agent 并实现企业人工审批工作流

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
`StateGraph.compile()` 的静态边校验非常赞！建议在 `audit_logs` 中把时间戳也带上，财务审计回溯审批链路时会用到。

### Reviewer：阿杰 (后端工程师)（Approved）
`draw_mermaid()` 导出的图我直接贴到 GitLab Wiki 里秒渲染出来了，以后改完图代码就能自动同步架构图，再也不用手工画 Visio 了！

### Reviewer：林产品 (产品经理)（Approved）
超过 5000 元必走人工审批的逻辑很清晰。不过现在总监审批是同步回调函数，真实场景总监可能隔 2 小时才在钉钉点同意，这怎么处理？

