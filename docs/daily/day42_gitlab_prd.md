# STARMIND-042 · Day 42 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 42 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | LangGraph 进阶 —— Checkpointer 断点续跑、HITL 人在回路、Subgraph 子图与 Fan-out/Fan-in 并行写作 Agent |
| **GitLab 分支** | `feat/day42-langgraph-advanced-writer` |
| **Commit 规范** | `feat(day42): 实现SQLite Checkpointer、HITL中断恢复、重试机制与并行章节写作Agent` |
| **配套课件** | `courseware/day42/index.html` |
| **配套 Notebook** | `notebooks/day42/day42_practice.ipynb` |
| **迭代快照** | `versions/day42/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 41）我们手写了 `StateGraph` 引擎并跑通了同步版的 ReAct 和采购审批流，但留下了生产级异步中断、状态持久化以及多任务并发加速三大进阶课题。
- **启下（明日演进）**：明天（Day 43）我们将从单 Agent 状态图跃迁到“多 Agent 协同系统”，学习 Supervisor 模式、协作模式与层级模式，并组建星辰数科“搜索员+分析师+撰写员”研究团队。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科售前方案团队每周要为政企客户撰写 3000 字以上的技术方案书。以往串行生成 4 个章节耗时长达 40 秒，且生成前需要售前经理确认大纲，一旦中途 API 抖动报错，之前写好的章节全部作废重来。

### 核心痛点
- 审批/确认流程耗时跨度大（几分钟到几小时），不能阻塞后端 HTTP 线程，必须支持断点落库与异步恢复。
- 长文档多章节串行生成延迟过高，用户体验极差。
- 外部模型接口偶发 429 限流或网络抖动，缺少节点级自动重试机制导致整条任务失败。

### 迭代目标
- 实现 `SQLiteCheckpointer`，按 `thread_id` 持久化每一步状态快照与下一待执行节点，支持 `interrupt_before` 挂起与 `resume` 恢复。
- 为状态图节点增加可配置的指数退避错误重试机制（`RetryPolicy`）。
- 基于 Subgraph（单章撰写+质量校验子图）与 Fan-out/Fan-in 并行分发，实现“大纲规划 -> 并发写章节 -> 汇总润色”写作 Agent。

### 验收标准
- [x] 在 `interrupt_before=['human_review']` 处自动暂停并写入 SQLite，模拟新进程重启后仍能按 `thread_id` 注入人工修改意见并恢复执行至 `END`。
- [x] 模拟某节点前 2 次抛临时网络异常、第 3 次成功时，重试机制可自动恢复且最终状态无误。
- [x] 写作 Agent 并行执行 3 个章节子图的总耗时明显低于串行总耗时，且最终成文严格保持大纲章节顺序。

### 非功能指标
- Checkpointer 读写需使用参数化 SQL，保证并发安全并支持历史快照时间旅行查询（`get_history`）。
- 并行 Fan-in 汇总必须按原大纲索引排序，严禁因线程完成先后不同导致章节乱序。

## 3. 架构设计与交付清单

当 Agent 从 Demo 走向企业生产，必须解决三大工程难题：**长周期挂起（Durability）**、**模块化复用（Modularity）**与**低延迟并发（Concurrency）**。

1. **Checkpointer 与时间旅行（Time Travel）**：在每个 Super-step（节点执行完毕）后，引擎自动将 `(thread_id, step_no, next_node, state_json)` 写入 SQLite（生产环境用 PostgreSQL + `langgraph-checkpoint-postgres`）。这不仅支撑了跨进程/跨小时的 **Human-in-the-loop（HITL）** 中断恢复，还天然赋予了系统“时间旅行”能力——线上出了 Bad Case，可以直接回滚到第 2 步的 Checkpoint 修改参数重跑！
2. **Subgraph（子图封装）**：如果把大纲生成、每章起草、每章敏感词校验、汇总润色全塞进一张大图，节点很快会膨胀到 20+ 个难以维护。把“起草单章 -> 格式与字数校验 -> 不合格重写”封装为一个独立的 **Chapter Subgraph**，主图只需把它当作一个黑盒节点调用，极大提升复用性。
3. **Fan-out / Fan-in（扇出与扇入并行）**：在真实 LangGraph 中通过 `Send('write_chapter', {'section': sec})` 实现动态扇出，配合 `Annotated[list, operator.add]` 收集各分支结果。工程上最容易踩的坑是**乱序问题**：第 3 章字数少可能比第 1 章先写完，因此每个并行分支必须携带 `index` 字段，在 Fan-in 汇总节点按 `index` 重新排序后再拼接润色。

### 当日交付代码文件
- `src/day42_checkpoint_hitl.py`：步骤一：实现 SQLite Checkpointer、HITL 中断恢复与节点重试引擎
- `src/day42_parallel_writer.py`：步骤二：Subgraph 子图 + Fan-out/Fan-in 并行技术方案写作 Agent

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
跨实例 SQLite 重启恢复的单测写得非常扎实！生产切 PostgreSQL 时只需要把连接驱动替换成 `psycopg`，上层 `PersistentGraph` 一行不用改。

### Reviewer：阿杰 (后端工程师)（Approved）
并行写作里 `results.sort(key=lambda ch: ch.index)` 这行救了大命，我之前用 `as_completed` 直接拼字符串，结果第三章老是跑到第一章前面。

### Reviewer：林产品 (产品经理)（Approved）
售前同事听说大纲能人工改完再并发生成全文，已经来催排期了！

