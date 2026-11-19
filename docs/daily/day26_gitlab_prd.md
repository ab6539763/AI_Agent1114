# STARMIND-026 · Day 26 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 26 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 4 周：第4周：LangChain 核心架构与 RAG 文档预处理） |
| **需求标题** | LCEL表达式与链：Runnable协议、管道符原理与结构化输出解析 —— 揭秘 `prompt | model | parser` 底层魔法，搭建企业涉外文档「翻译->润色->摘要」三级流水线 |
| **GitLab 分支** | `feat/day26-lcel-runnable-pipeline` |
| **Commit 规范** | `feat(day26): 实现Runnable协议与LCEL管道编排，完成翻译润色摘要三级链` |
| **配套课件** | `courseware/day26/index.html` |
| **配套 Notebook** | `notebooks/day26/day26_practice.ipynb` |
| **迭代快照** | `versions/day26/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 25）我们实现了 `BaseChatModel` 和 `ChatPromptTemplate`，解耦了模型与提示词。但大家写测试时发现：每次都要先调 `prompt.format_messages()`，再手动把结果传给 `llm.invoke()`，再从 `AIMessage.content` 里抠文本甚至做 `json.loads()`，步骤一多代码就变成面条。
- **启下（明日演进）**：明天（Day 27）我们要给今天搭好的无状态链装上「大脑海马体」——Memory 记忆机制，解决多轮对话失忆和 SQLite 多用户 `session_id` 隔离持久化问题。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科海外业务部每周需要处理上百份中文产品更新日志与技术白皮书，人工需要经历「英译 -> 商务润色 -> 提炼核心摘要与关键词」三个环节，耗时耗力且格式难以统一。

### 核心痛点
- 多步骤串行调用大模型时，中间变量传递繁琐，缺乏统一的批处理（batch）与流式（stream）接口。
- 大模型返回 JSON 时经常夹带 ```json 代码块标记或多余解释文字，导致 `json.loads` 频繁报错。
- 需要对同一份文档同时并行生成「摘要」和「风险/关键词标签」，串行执行耗时翻倍。

### 迭代目标
- 实现完整的 Runnable 协议基类，支持 `|` 管道串联、`invoke`、`batch`、`stream` 统一调用。
- 实现 `RunnableLambda`、`RunnablePassthrough`、`RunnableParallel` 三大编排原语。
- 实现 `StrOutputParser`、`JsonOutputParser`、`PydanticOutputParser`，构建「翻译 -> 润色 -> 摘要」三级串行链与并行分析链。

### 验收标准
- [x] `chain = step1 | step2 | step3` 支持任意深度组合，且支持 `batch` 批量处理与 `stream` 分块流式吐出。
- [x] `JsonOutputParser` 能自动剥离 Markdown 代码块围栏并容错解析，`PydanticOutputParser` 能校验字段类型并返回强类型 BaseModel 对象。
- [x] 三级链端到端运行稳定，所有 pytest 单元测试 100% 通过。

### 非功能指标
- 并行链（RunnableParallel）支持并发执行各分支，降低多任务总延迟。
- 解析失败时抛出带原始输出片段的结构化 `OutputParserException` 便于排障。

## 3. 架构设计与交付清单

为什么 LangChain 0.2/0.3 要大张旗鼓地用 LCEL 淘汰老旧的 `LLMChain` / `SequentialChain`？从架构师视角看，核心有三点：
1. **统一契约（Uniform Interface）**：在 LCEL 世界里，Prompt、Model、OutputParser、Retriever 全部继承自同一个基类 `Runnable`，都实现 `invoke`（单条）、`batch`（批量并发）、`stream`（流式吐字）。这意味着任意两个组件只要输入输出类型匹配，就能用 `|` 像 Linux Shell 管道一样拼装。
2. **数据流图可视化与并行加速**：`RunnableParallel`（在字典写法 `{ 'summary': chain_a, 'tags': chain_b }` 中自动触发）允许底层通过线程池（`ThreadPoolExecutor`）或 `asyncio.gather` 同时发起多个独立的 LLM 请求，直接把串行耗时 $T_1 + T_2$ 压缩为 $\max(T_1, T_2)$。
3. **结构化契约边界（OutputParser）**：大模型天生输出非结构化文本，而企业后端系统只认强类型结构体。`PydanticOutputParser` 在上游通过 `get_format_instructions()` 自动把 Pydantic Schema 注入 Prompt，在下游自动完成 Markdown 围栏清洗、JSON 反序列化和字段校验，把不可控的概率输出变成确定性的业务对象。

### 当日交付代码文件
- `src/day26_lcel_core.py`：步骤一：从零实现 LCEL 核心 Runnable 协议引擎
- `src/day26_parsers_and_chain.py`：步骤二：实现三大 OutputParser 与「翻译->润色->摘要」三级 LCEL 链

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
`OutputParserException` 把 `llm_output` 原始文本挂在异常对象上这个设计很老道！后面我们做自动重试（OutputFixingParser）时可以直接把出错原文喂回给模型自修复。

### Reviewer：林产品（Approved）
海外团队希望在页面上同时看到「直译稿」和「润色稿」做对比，不能只返回最终摘要。

