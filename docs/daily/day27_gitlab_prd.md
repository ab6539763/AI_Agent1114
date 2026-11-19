# STARMIND-027 · Day 27 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 27 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 4 周：第4周：LangChain 核心架构与 RAG 文档预处理） |
| **需求标题** | Memory记忆机制：多轮会话隔离、窗口摘要压缩与SQLite持久化 —— 告别金鱼脑！实现支持多员工并发隔离的 RunnableWithMessageHistory 与记忆裁剪引擎 |
| **GitLab 分支** | `feat/day27-memory-sqlite-session` |
| **Commit 规范** | `feat(day27): 实现SQLite多会话隔离历史存储、窗口/摘要记忆与RunnableWithMessageHistory` |
| **配套课件** | `courseware/day27/index.html` |
| **配套 Notebook** | `notebooks/day27/day27_practice.ipynb` |
| **迭代快照** | `versions/day27/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 26）我们用 LCEL 管道符串起了多步推理流水线。但测试同学一测就发现：第一句说「我叫小王，在研发部」，第二句问「我叫什么名字？」，链直接装傻——因为大模型本身是无状态的（Stateless），每次 HTTP 请求都是全新失忆。
- **启下（明日演进）**：明天（Day 28）我们将正式迈出企业级 RAG 系统的第一步：多格式文档加载（PDF/Word/MD/HTML/CSV）与中文递归分块（RecursiveCharacterTextSplitter）。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑内部助手即将在全公司 800 名员工中灰度推广，员工在查询报销、休假、IT 故障时往往需要连续追问 5~15 轮，且服务需支持重启后恢复历史会话。

### 核心痛点
- 无状态链无法理解多轮上下文，用户每轮都要重复背景信息。
- 内存态 dict 存历史在服务重启后丢失，且多实例部署时状态不一致。
- 长对话全量塞入 Prompt 导致 Token 费用失控与首字延迟（TTFT）飙升。

### 迭代目标
- 实现 `BaseChatMessageHistory` 抽象及基于 SQLite 的 `SQLiteChatMessageHistory`，严格按 `session_id` 隔离并支持持久化。
- 实现两种企业级记忆压缩策略：滑动窗口记忆（保留最近 K 轮）与摘要缓冲记忆（超出阈值将早期对话压缩为摘要）。
- 实现 `RunnableWithMessageHistory` 包装器，无侵入地为任意 LCEL 链注入多轮记忆能力。

### 验收标准
- [x] 不同 `session_id` 的并发读写完全隔离，绝不串台；重新实例化对象后可从 SQLite 恢复完整历史。
- [x] 滑动窗口能精确截断保留最近 `k` 轮（`2*k` 条消息）；摘要记忆在超限时自动生成摘要并缩减消息数。
- [x] 所有 pytest 单元测试（含跨会话隔离、重启持久化、窗口截断与摘要触发）100% 通过。

### 非功能指标
- SQLite 写入支持线程安全与索引加速（按 `session_id, id` 建复合索引）。
- 单次历史加载耗时 < 5ms。

## 3. 架构设计与交付清单

在 LangChain 0.2/0.3 中，官方正式废弃了状态与链耦合在一起的旧版 `ConversationChain`，转而推荐「存储与编排解耦」的 `RunnableWithMessageHistory` 架构：
1. **历史存储层（ChatMessageHistory）**：只负责按 `session_id` 存取 `BaseMessage` 列表。开发环境用 SQLite，生产高并发集群无缝切换为 Redis（带 TTL 自动过期）或 PostgreSQL。
2. **记忆压缩策略层（Memory Trimmer / Summarizer）**：在把历史消息送进大模型之前，经过一道「上下文网关」：
   - **滑动窗口策略（Window）**：只取最近 $K$ 轮对话（$2K$ 条消息），简单高效、零额外 LLM 调用，适合客服与工单场景。
   - **摘要缓冲策略（Summary Buffer）**：当历史消息总字符数/Token 超过阈值时，将较早的 $N$ 轮对话提炼成一条精简的「历史摘要」作为 `SystemMessage` 置顶，同时完整保留最近 $K$ 轮原文，兼顾长期记忆与低 Token 消耗。
3. **无侵入包装层（RunnableWithMessageHistory）**：在每次 `invoke(input, config={'configurable': {'session_id': '...'}})` 前自动读取并裁剪历史，调用完成后自动将本轮 `HumanMessage` 和 `AIMessage` 持久化落盘。

### 当日交付代码文件
- `src/day27_sqlite_history.py`：步骤一：实现线程安全、按 session_id 隔离的 SQLiteChatMessageHistory
- `src/day27_memory_chain.py`：步骤二：实现窗口记忆、摘要缓冲记忆与 RunnableWithMessageHistory

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
把历史写回放在 `self.runnable.invoke` 成功之后非常正确！另外提醒一下，生产上 `session_id` 一定要做非空校验，你这里也补了，给个赞。

### Reviewer：阿杰（Approved）
SQLite 建表语句加上了 `(session_id, id)` 复合索引，后续如果表膨胀到几百万行，建议再加一个定时清理 30 天前历史记录的归档任务。

