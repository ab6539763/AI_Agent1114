# STARMIND-043 · Day 43 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 43 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | 多 Agent 系统 —— Supervisor / 协作 / 层级模式对比与星辰行业研究团队多 Agent 协同实战 |
| **GitLab 分支** | `feat/day43-multi-agent-supervisor-team` |
| **Commit 规范** | `feat(day43): 实现Supervisor路由状态机与搜索员/分析师/撰写员多Agent研究团队` |
| **配套课件** | `courseware/day43/index.html` |
| **配套 Notebook** | `notebooks/day43/day43_practice.ipynb` |
| **迭代快照** | `versions/day43/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 42）我们攻克了 LangGraph 的 Checkpointer 断点持久化、HITL 中断恢复、节点重试与并行章节写作 Agent，单个复杂 Agent 的工程底座已经非常扎实。
- **启下（明日演进）**：明天（Day 44）我们将把视野拓展到跨系统生态协议——Model Context Protocol（MCP），手写符合 JSON-RPC 2.0 规范的 MCP Server/Client，并构建 Agent 短期与长期双层记忆架构。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科战略发展部每周需要针对目标行业（如新能源、企业级 SaaS、工业视觉）输出一份包含竞品动态、财务估算与落地建议的深度研报。单 Agent 同时承担搜索、量化计算和公文排版时，经常出现数据引用错位或遗漏关键章节。

### 核心痛点
- 单 Agent 挂载过多工具与角色指令后，Prompt 膨胀导致推理准确率断崖式下降。
- 不同专家任务需要不同上下文视图（分析师只需结构化数据，撰写员只需结论与论据），全量广播历史消息极度浪费 Token。
- 多 Agent 之间若缺少统一调度与轮次限制，极易在“打回修改 -> 重新分析 -> 再次打回”中陷入无限踢皮球。

### 迭代目标
- 对比 Supervisor（主管集中式）、Peer-to-Peer（去中心化交接）与 Hierarchical（层级树状）三种多 Agent 编排模式的适用边界。
- 实现通用的 `SupervisorOrchestrator` 状态机，支持共享黑板（Blackboard State）、按角色裁剪上下文视图与防踢皮球熔断。
- 落地星辰行业研究团队：`ResearcherAgent`（情报搜索员）+ `AnalystAgent`（数据分析师）+ `WriterAgent`（报告撰写员），支持主管质检打回重写。

### 验收标准
- [x] 给定行业研究主题后，Supervisor 能按「搜索 -> 分析 -> 撰写 -> 质检」顺序动态路由各专家节点。
- [x] 当撰写员初稿缺少“风险提示”关键章节时，Supervisor 能将其打回重写并在下一轮通过验收。
- [x] 设置 `max_rounds` 上限，模拟死循环路由时能触发安全熔断并返回降级报告，所有单测本地 100% 通过。

### 非功能指标
- 每个专家 Agent 拥有独立的 `allowed_tools` 权限边界，禁止撰写员直接越权调用原始搜索或写库工具。
- 完整记录每次路由决策的 `routing_history`（轮次、目标角色、路由原因），便于线上复盘。

## 3. 架构设计与交付清单

多 Agent 系统（Multi-Agent System, MAS）的核心价值在于**关注点分离（Separation of Concerns）**与**最小权限隔离**。工业界最主流的三种编排模式各有取舍：

1. **Supervisor（主管集中式）**：由一个中心化的 `Supervisor` 节点读取全局状态（Blackboard），每轮决定派发给哪位专家 Worker（或宣布 `FINISH`）。优点是全局可控、审计清晰、极易在主管层统一做质检和熔断；缺点是主管节点本身会成为调用热点。**星辰数科 80% 的企业多 Agent 业务首选此模式**。
2. **Collaborative / Handoff（去中心化协作交接）**：各 Agent 之间直接通过 `Command(goto='next_agent')` 移交控制权（如 OpenAI Swarm 模式）。优点是延迟低、少一次主管路由调用；缺点是 Agent 数量超过 4 个后跳转拓扑迅速网状化，极难维护。
3. **Hierarchical（层级团队模式）**：将多个 Supervisor 嵌套为 Subgraph（例如“总编主管”下辖“调研小组主管”和“法务审校主管”），适合超大型复杂流水线。

在工程落地时，多 Agent 最关键的三个设计原则是：① **共享黑板 + 局部视图**：用结构化字典保存 `facts`、`metrics`、`draft` 等工件，每个专家只读自己关心的字段，不把原始冗余日志塞进所有人的上下文；② **明确的交接契约（Artifact Contract）**：搜索员必须产出带来源的条目列表，分析师必须产出可验证的数值指标；③ **硬性轮次熔断与踢皮球检测**：限制总轮次 `max_rounds` 与单角色最大返工次数 `max_revisions`，防止两个 Agent 互相指责死循环烧光预算。

### 当日交付代码文件
- `src/day43_multi_agent_patterns.py`：步骤一：实现通用 Supervisor 多 Agent 路由状态机与权限隔离底座
- `src/day43_research_team.py`：步骤二：组建星辰行业研究团队（搜索员 + 分析师 + 撰写员 + 质检打回闭环）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
路由轨迹 `routing_history` 记录得非常清楚，配合 `truncated` 熔断标志，线上排查多 Agent 死循环一目了然。

### Reviewer：阿杰 (后端工程师)（Approved）
赞一个 `WorkerAgent` 的 Protocol 设计，把分析师和搜索员解耦之后，以后给分析师单独换一个擅长数学推理的模型（比如 DeepSeek-R1）也只需改它自己。

### Reviewer：林产品 (产品经理)（Approved）
质检不通过自动打回补齐“风险提示”这个效果太直观了，战略部总监看了演示直接说要拿去试跑下周的行业周报！

