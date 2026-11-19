# STARMIND-039 · Day 39 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 39 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | Agent 概念与 ReAct 范式 —— 从固定流水线迈向自主决策：零框架手写企业级 ReAct 推理-行动循环 |
| **GitLab 分支** | `feat/day39-react-agent-from-scratch` |
| **Commit 规范** | `feat(day39): 零框架手写ReAct智能体引擎并接入企业检索与安全计算工具` |
| **配套课件** | `courseware/day39/index.html` |
| **配套 Notebook** | `notebooks/day39/day39_practice.ipynb` |
| **迭代快照** | `versions/day39/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 38）我们完成了阶段项目二「企业级 RAG 知识库问答系统」的答辩复盘。大家已经能够熟练搭建“检索 -> 重排 -> 生成”的固定链路（Chain），但在答辩中林产品提了一个尖锐问题：如果员工问“我下周去上海出差 3 天，按公司最新标准最多能报销多少住宿和餐补？”，单纯靠 RAG 只能搜出报销单价，大模型自己心算乘法经常算错，而且无法动态决定先查政策再算账。
- **启下（明日演进）**：明天（Day 40）我们会把手写 ReAct 的痛点（正则解析脆弱、工具参数缺强校验）彻底解决，深入 LangChain 的 `@tool` 装饰器、JSON Schema 自动提取、`ToolCallingAgent` 与 `AgentExecutor` 回调观测体系。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科行政与财务部每天收到 300+ 条员工关于差旅标准、补贴核算和年假折算的咨询。纯 RAG 问答只能返回静态条文，员工仍需手工计算天数和金额，体验割裂且易出错。

### 核心痛点
- 传统 Chain 流程写死，无法根据问题复杂度动态决定调用 0 次、1 次还是多次外部工具。
- 大模型原生算术能力不可靠，涉及多天差旅、税费折扣等精确数值计算时频现幻觉。
- 直接引入重型 Agent 框架导致新人难以排查 Prompt 解析失败、死循环等底层故障。

### 迭代目标
- 梳理 Chain 与 Agent 的架构差异，掌握感知-思考-行动（Observe-Think-Act）闭环原理。
- 零框架纯 Python 实现符合 ReAct 论文规范的推理引擎（Thought / Action / Action Input / Observation / Final Answer）。
- 接入企业内网制度搜索工具与安全四则运算工具，完成复合咨询问题的多步自动求解。

### 验收标准
- [x] 输入复合差旅核算问题时，Agent 至少完成“先检索制度、再调用计算器、最后给出精确结论”三步闭环。
- [x] 支持 `max_steps` 最大步数熔断机制，遇到未知工具名或格式异常时能向模型反馈纠偏信息而非崩溃。
- [x] 所有核心代码与 `pytest` 单元测试无需外网 API Key 即可在本地 100% 运行通过。

### 非功能指标
- 单步工具执行必须隔离异常，严禁使用不安全的原生 `eval` 执行未校验字符串。
- 完整记录每一步的推理轨迹（Trajectory），便于后续审计与 Bad Case 复盘。

## 3. 架构设计与交付清单

在企业级 AI 应用架构演进中，Chain（链）与 Agent（智能体）的分水岭在于“控制流（Control Flow）由谁决定”。在 Chain 中，控制流是程序员在代码里静态编排好的 DAG（有向无环图），模型只是图上的一个无状态文本生成节点；而在 Agent 中，模型本身充当了“动态路由器与规划器（Controller）”，每次根据当前上下文决定下一步是否调用外部工具、调用哪个工具、传什么参数，拿到环境返回的 `Observation` 后再次进入思考循环，直到满足终止条件。

ReAct（Reasoning + Acting，Yao et al., ICLR 2023）是工业界最经典的 Agent 范式。它的核心洞察在于：纯 CoT（思维链）容易脱离外部事实产生幻觉，纯 Act（仅输出动作）缺乏显式推理容易迷失目标；将 `Thought`（显式推理）与 `Action`（外部行动）交替写入上下文，既能让模型先拆解子任务，又能用真实工具返回的 `Observation` 锚定推理方向。

在零框架落地 ReAct 时，最核心的工程架构分为四层：1）**Prompt 模板层**：向模型注入可用工具清单（名称、用途、参数格式）与严格的停止词（Stop Sequence，如 `Observation:`，防止模型自己伪造工具输出）；2）**模型推理适配层**：抽象 `BaseLLM` 接口，生产环境对接 OpenAI/DeepSeek/Qwen，本地单测与 CI 对接可回放的确定性 Mock/Rule LLM；3）**协议解析与容错层**：用正则表达式提取 `Action` 和 `Action Input`，当模型输出走样时，不直接抛异常，而是将格式纠偏提示作为 `Observation` 塞回下一轮对话；4）**工具执行与熔断层**：统一注册表分发调用，强制 `max_steps` 上限和异常捕获，确保任何坏工具都不会拖垮主循环。

### 当日交付代码文件
- `src/day39_tools.py`：步骤一：构建企业工具注册表与 AST 安全计算器
- `src/day39_react_agent.py`：步骤二：零框架手写 ReAct 推理-行动循环引擎

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
AST 计算器加了指数上限保护非常细致！不过注意 `parse_react_output` 里 `Action Input` 目前只匹配单行 `[^\n]+`，后续如果工具需要传入多行 JSON，记得升级成结构化 Function Calling（明天重点讲）。

### Reviewer：阿杰 (后端工程师)（Approved）
`ReActAgent.run` 把每一步封装成 `AgentStep` 列表返回，前端做“思考过程折叠面板”时直接遍历渲染就行，数据结构很干净。

### Reviewer：林产品 (产品经理)（Approved）
上海出差 3 天报销的 Case 跑得很准！希望能再补充一个“杭州二线城市”的测试用例，明天给财务部同事演示。

