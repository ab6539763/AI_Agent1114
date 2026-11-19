# STARMIND-037 · Day 37 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 37 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 6 周：第6周：阶段项目二——企业级知识库问答系统实战与答辩） |
| **需求标题** | 阶段项目二(下)：企业级知识库问答系统——多轮改写、引用高亮、SSE流式与全链路联调 —— 补齐企业级交互体验闭环：多会话上下文记忆、指代消解改写、证据高亮溯源与 SSE 打字机流式输出 |
| **GitLab 分支** | `feat/day37-project2-multiturn-sse-e2e` |
| **Commit 规范** | `feat(day37): 完成多会话管理、多轮指代消解改写、引用高亮与SSE流式问答API全链路联调` |
| **配套课件** | `courseware/day37/index.html` |
| **配套 Notebook** | `notebooks/day37/day37_practice.ipynb` |
| **迭代快照** | `versions/day37/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 36）我们完成了项目二（上）：多格式文档解析入库、ACL 权限过滤、混合检索+Rerank 引擎和 FastAPI 基础接口。但前端联调时立刻提了三个最影响用户体验的硬需求：「1. 员工连续追问『那需要提前几天申请？』系统忘了上一轮在聊年假；2. 引用片段是一坨纯文本，用户找不到重点词；3. 等整段答案拼完才返回太慢，必须上 ChatGPT 同款 SSE 流式打字机！」
- **启下（明日演进）**：明天（Day 38）我们将迎来第三阶段收官大战——**项目二答辩与代码评审**：准备 10 分钟技术答辩架构讲稿、执行 GitLab Code Review 评分表、并对项目二进行并发压测瓶颈定位与重构优化实战！

## 2. 业务需求说明 (PRD)

### 业务背景
项目二后端单轮问答 API 已就绪，现需补齐企业级聊天产品的核心交互闭环：多会话并发隔离、多轮追问上下文改写、引用片段关键词高亮溯源，以及降低用户首字等待焦虑的 SSE 流式传输。

### 核心痛点
- 多轮追问（如「那病假呢？」「它怎么申请？」）直接送去检索会导致召回完全偏航。
- 用户看到 150 字的引用原文仍需肉眼扫读寻找核心数字与条款，信任建立慢。
- 同步接口需等待完整答案生成才返回，首字节时间（TTFT）体验差。

### 迭代目标
- 实现 `SessionManager`：支持多会话创建、列表、滑动窗口历史查询、删除与状态隔离。
- 实现 `MultiTurnQueryRewriter`：结合会话历史自动识别指代词与短追问，输出带上下文锚点的规范化检索 Query。
- 实现 `CitationHighlighter`：自动提取查询关键词并在引用片段中插入 `<mark>...</mark>` 高亮标签。
- 实现 FastAPI SSE 流式端点 `POST /api/v1/chat/stream`，按标准 SSE 帧协议依次推送 `meta`、`citation`、`token`、`done` 事件。

### 验收标准
- [x] 两个不同 `session_id` 的并发对话历史 100% 隔离，互不干扰。
- [x] 在「年假规定」之后的追问「它需要提前几天申请？」能被正确改写包含「年假」并精准命中年假审批条款。
- [x] 返回的引用片段包含有效的 `<mark>...</mark>` 高亮标签且不破坏原文完整性。
- [x] SSE 接口响应头包含 `text/event-stream`，客户端解析全部 `token` 帧后可无损还原完整回答，且本轮对话自动持久化至会话历史。

### 非功能指标
- SSE 响应头必须设置 `Cache-Control: no-cache` 和 `X-Accel-Buffering: no`（防止生产 Nginx 缓冲导致打字机卡顿）。
- 单会话历史支持 `max_turns` 滑动窗口截断，防止超长对话撑爆内存与 Token 窗口。

## 3. 架构设计与交付清单

多轮流式 RAG 与单轮问答最大的架构差异在于「状态流转」与「渐进式渲染」：
1. **两步分离（改写只用于检索，原文用于展示）**：收到用户追问后，先从 `SessionManager` 取出最近 3 轮对话，经 `MultiTurnQueryRewriter` 生成独立完整的 `rewritten_query` 送去检索；但写入对话历史展示给用户的仍是原始问题，保证 UI 界面自然清爽。
2. **引用先行 + 文本流式（Citations-First SSE Pattern）**：在 SSE 流式协议中，我们先推送 `event: meta`（包含 `session_id` 和 `rewritten_query`，让用户知道 AI 听懂了指代）和 `event: citation`（带 `<mark>` 高亮的证据卡片，前端立刻渲染右侧溯源栏），再逐块推送 `event: token` 打字机正文，最后发送 `event: done` 结束信号并将本轮问答原子落盘。
3. **安全的高亮策略**：`CitationHighlighter` 按词长降序匹配非重叠高亮词（并做 HTML 特殊字符防注入转义思想），避免短词切碎长词导致嵌套 `<mark><mark>...</mark></mark>` 的前端渲染 Bug。

### 当日交付代码文件
- `src/day37_session_highlight.py`：步骤一：实现多会话管理、多轮指代消解改写、安全高亮与 SSE 流式服务引擎
- `src/day37_sse_api.py`：步骤二：实现多会话管理与 SSE 流式问答 FastAPI 服务（day37_sse_api.py）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
先 `html.escape()` 再插 `<mark>` 这个防 XSS 细节加分！顺手把单元测试也覆盖上了 `<script>` 注入，非常规范。

### Reviewer：林产品（Approved）
SSE 里先推 `meta` 和 `citation` 再推 `token` 体验太好了！用户点发送 50ms 就能先看到右侧亮起依据文档，完全不会觉得卡顿。

