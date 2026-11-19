# STARMIND-025 · Day 25 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 25 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 4 周：第4周：LangChain 核心架构与 RAG 文档预处理） |
| **需求标题** | LangChain入门：架构总览、ChatModel统一接口与Prompt模板工程 —— 告别硬编码 HTTP 请求，构建星辰智脑统一模型抽象层与可复用提示词工厂 |
| **GitLab 分支** | `feat/day25-langchain-chatmodel-prompt` |
| **Commit 规范** | `feat(day25): 实现LangChain风格ChatModel统一接口与ChatPromptTemplate模板引擎` |
| **配套课件** | `courseware/day25/index.html` |
| **配套 Notebook** | `notebooks/day25/day25_practice.ipynb` |
| **迭代快照** | `versions/day25/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 24）我们完成了阶段项目一「智能客服与工单助手」的验收复盘，大家已经能熟练手写 OpenAI SDK 调用、Function Calling 与 Prompt 调优。但项目评审时阿杰吐槽：代码里混着 DeepSeek、通义千问、GLM 三套 HTTP 调用逻辑，提示词全是 f-string 硬拼，换个模型改半天。
- **启下（明日演进）**：明天（Day 26）我们将深入 LangChain 最核心的编排引擎——LCEL 表达式语言，亲手揭开管道符 `|` 和 `Runnable` 协议的底层源码秘密，并搭建多步骤串联与并行处理链。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科内部正在建设「星辰智脑」AI 中台，目前研发、客服、HR 三个业务线分别对接了 DeepSeek、通义千问和私有化 vLLM，导致提示词散落各处、Token 统计口径不统一、切换模型成本极高。

### 核心痛点
- 各业务线直接拼装 raw dict 调不同厂商接口，消息格式和异常处理五花八门。
- Prompt 字符串写死在业务逻辑里，产品经理林姐改一句措辞都要发版。
- 缺乏统一的 Token 计量、耗时追踪和离线单测 Mock 能力，CI 流水线跑不通。

### 迭代目标
- 设计并实现符合 LangChain 核心规范的消息协议（SystemMessage / HumanMessage / AIMessage）与 BaseChatModel 统一接口。
- 实现 PromptTemplate 与 ChatPromptTemplate，支持变量校验、部分填充（partial）与 Few-Shot 示例注入。
- 提供星辰数科 IT 工单分类与知识问答两个标准模板，支持零外网依赖的本地单元测试。

### 验收标准
- [x] 同一套业务代码可在 StarMindChatModel（离线/规则路由）与 OpenAI 兼容网关模式间无缝切换，无需修改调用方。
- [x] 模板渲染缺失必填变量时抛出明确的 ValueError，严禁静默输出 `{variable}` 占位符到生产。
- [x] 所有调用自动记录 prompt_tokens、completion_tokens 与 latency_ms，单元测试覆盖率 100% 通过。

### 非功能指标
- 单次模板渲染耗时 < 1ms。
- 代码严格遵循类型注解（Type Hints），无第三方重型 C++ 扩展强依赖。

## 3. 架构设计与交付清单

在企业级 AI 应用架构中，绝不能让上层业务逻辑（如客服问答、合同审核、RAG 检索）直接依赖具体厂商的 SDK。LangChain 在 0.2/0.3 版本中完成了至关重要的「核心瘦身」：将最基础的抽象接口抽离到 `langchain-core`（包含 `BaseMessage`、`BaseChatModel`、`BasePromptTemplate`、`Runnable`），而把各厂商适配器下沉到独立的 `langchain-openai`、`langchain-deepseek`、`langchain-community` 等集成包中。

在星辰智脑的架构落地上，我们采用「适配器模式 + 模板方法模式」：
1. **统一消息信封（Message Envelope）**：将所有对话统一抽象为 `SystemMessage`、`HumanMessage`、`AIMessage`，并携带 `response_metadata`（模型名、Token 消耗、耗时、请求 ID），方便后续接入 LangSmith 或内部 Prometheus 监控。
2. **模型网关抽象（BaseChatModel）**：对外暴露统一的 `invoke(messages)` 接口，内部按配置路由到 DeepSeek API、通义千问 DashScope、内网 vLLM 或本地确定性测试桩（Mock/Offline 引擎），彻底解决 CI/CD 跑单测需要真实 API Key 烧钱的问题。
3. **提示词资产化（PromptTemplate）**：将 Prompt 视为代码与配置之间的独立资产，支持严格变量提取校验、partial 局部固化（例如先把 `company_name='杭州星辰数科'` 注入）以及多轮 Few-Shot 示例装配。

### 当日交付代码文件
- `src/day25_chat_model.py`：步骤一：实现统一消息协议与 BaseChatModel 抽象层
- `src/day25_prompt_template.py`：步骤二：实现 PromptTemplate、ChatPromptTemplate 与 Few-Shot 装配

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
用 `string.Formatter` 解析变量非常加分！上次实习生用 `re.findall(r'{(.*?)}', s)`，结果 Prompt 里一写 JSON 示例就报 KeyError。建议再加个单测覆盖 `{{}}` 转义场景。

### Reviewer：阿杰（Approved）
`BaseChatModel.invoke` 支持传 `str` 和 `List[BaseMessage]` 很贴心，如果传入空列表 `[]` 要明确抛异常，别在 `messages[-1]` 报 IndexError。

