# STARMIND-021 · Day 21 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 21 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 3 周：第3周：大模型底层原理、Prompt 工程与工具调用实战） |
| **需求标题** | 第3周周测与综合实战：多轮对话 + 工具调用 + 流式输出整合引擎 —— 一周知识大阅兵！整合安全网关、多轮记忆裁剪、Function Calling 与流式推送，并通过自动化周测 |
| **GitLab 分支** | `feat/day21-weekly-exam-engine` |
| **Commit 规范** | `feat(day21): 整合多轮对话+工具调用+流式输出综合引擎并完成第3周自动化周测评测` |
| **配套课件** | `courseware/day21/index.html` |
| **配套 Notebook** | `notebooks/day21/day21_practice.ipynb` |
| **迭代快照** | `versions/day21/` |

## 1. 上下文衔接

- **承上（昨日基线）**：过去六天（Day 15 ~ Day 20）我们从零攻克了 Token 成本估算、API 采样与流式协议、Prompt 四要素与 10 场景模板、CoT 与提示词注入防线、Function Calling 工具闭环以及多模态与语义向量匹配。但目前这些能力还像散落的零件一样各自躺在单独脚本里。
- **启下（明日演进）**：下周（Day 22 ~ Day 24）我们将开启全栈 Web 开发冲刺：先用一天速成 HTML/CSS/JS 前端聊天界面，再用两天拿 FastAPI + SSE + SQLite 打造出真正能前后端联调的「网页版星辰 ChatGPT 克隆」！

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科技术委员会要求在第 3 周末进行阶段性里程碑验收：必须将过去一周分散开发的 Prompt 安全、多轮会话记忆、工具调用与流式输出整合为统一核心引擎，并交付可重复运行的自动化评测基准。

### 核心痛点
- 各模块各自为战，缺乏统一的会话状态管理（Session Memory）与上下文滑窗裁剪，长对话容易撑爆 Token 预算。
- 工具调用和流式输出衔接不顺，前端不知道模型当前是「正在调用工具」还是「正在流式吐字」。
- 缺少端到端综合评测脚本，无法量化验证本周所有核心能力的回归通过率。

### 迭代目标
- 构建 `StarMindIntegratedEngine`，在一个统一流水线内整合：安全注入拦截 -> 多轮会话记忆滑窗 -> 工具调用调度 -> 分事件类型流式输出（`tool_start` / `tool_result` / `token` / `done`）。
- 构建第 3 周综合自动化评测套件 `WeeklyBenchmarkRunner`，覆盖安全防御、多轮上下文指代记忆、工具计算/查询、流式增量吐字与异常处理五大维度。
- 输出结构化周测成绩单与等级评定（A/B/C/FAIL），要求综合得分 >= 90 分方可通过验收。

### 验收标准
- [x] 会话窗口超过 `max_history_turns` 时自动裁剪最早对话，但始终牢牢保留 `system` 提示词。
- [x] 流式事件流能清晰区分工具执行状态事件与正文文本增量事件，方便 Day 22~24 前端展示「正在查询天气...」加载动效。
- [x] 周测评测集 5 大场景全部通过，自动化得分达到 100 分，pytest 回归全绿。

### 非功能指标
- 引擎无外网依赖，支持通过 `session_id` 隔离多员工并发对话状态。
- 评测脚本支持直接接入 GitLab CI 作为合并前质量门禁。

## 3. 架构设计与交付清单

把零散 Demo 升级为可被 FastAPI 直接挂载的核心引擎，关键在于定义清晰的**流式事件协议（Stream Event Protocol）**与**会话内存管理（Session Sliding Window）**：
1. **统一流式事件流**：现代 AI 产品（如 ChatGPT、DeepSeek 网页版）在回复时不仅吐字，还会先显示「正在调用计算器...」「正在查询内部制度...」。因此我们的引擎对外 `yield` 标准化事件对象 `StreamEvent(event_type, payload)`，包含 `security_blocked`、`tool_call`、`tool_result`、`delta`（增量正文）、`done`（含本次消耗统计与总轮次）。
2. **多轮记忆滑窗裁剪**：每个 `session_id` 维护独立的 `messages` 列表。当历史轮数超过 `max_history_turns` 时，保留索引 0 的 `system` 指令并仅保留最近 $2 \times \text{max\_history\_turns}$ 条 `user/assistant` 记录，防止 Token 账单无限膨胀。
3. **自动化基准测试（Benchmark Harness）**：将本周所有核心知识点抽象为可断言的端到端测试用例集，自动计算总分并划分等级，为后续接入 CI/CD 打下基础。

### 当日交付代码文件
- `src/day21_integrated_engine.py`：步骤一：实现多轮对话 + 安全过滤 + 工具调用 + 流式输出整合引擎
- `src/day21_benchmark_runner.py`：步骤二：实现第 3 周 Prompt + API 综合周测自动化评测平台

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
多会话隔离单测写得非常到位！很多新手把 `history` 写成全局变量，结果 A 用户问问题串出了 B 用户的聊天记录，那是 P0 级隐私事故。

### Reviewer：阿杰 (后端工程师)（Approved）
这个 `StreamEvent` 结构已经非常像标准 SSE 协议了，后天 Day 24 直接接 FastAPI `StreamingResponse` 几乎零改造！

### Reviewer：林产品 (产品经理)（Approved）
周测 100 分 A+ 通过！下周期待早点看到网页版星辰 ChatGPT 上线！

