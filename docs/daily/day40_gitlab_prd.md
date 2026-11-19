# STARMIND-040 · Day 40 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 40 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | LangChain Agent 与工具 —— 从脆弱正则升级到结构化 Tool Calling：@tool 装饰器、JSON Schema 提取与安全工具箱 |
| **GitLab 分支** | `feat/day40-tool-calling-executor` |
| **Commit 规范** | `feat(day40): 实现@tool装饰器JSON Schema自动提取与AgentExecutor回调观测引擎` |
| **配套课件** | `courseware/day40/index.html` |
| **配套 Notebook** | `notebooks/day40/day40_practice.ipynb` |
| **迭代快照** | `versions/day40/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 39）我们零框架手写了基于文本正则解析的 ReAct Agent，体验了“思考-行动-观察”闭环，同时也暴露了单字符串 `Action Input` 难以传递多参数、缺乏类型强校验的痛点。
- **启下（明日演进）**：明天（Day 41）我们正式进入本阶段最核心的框架——LangGraph 状态图。你会发现 `AgentExecutor` 黑盒循环在复杂业务（例如“先审核再发邮件”）面前力不从心，而状态机图编排将彻底解放控制权。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科研发效能组希望星辰智脑不仅能回答问题，还能帮研发同学检索文档、执行受控的数据计算脚本，并在指定工作区自动生成周报 Markdown 文件。

### 核心痛点
- 手写工具 JSON Schema 既繁琐又容易与 Python 函数签名脱节，改个参数名就要同步改 Prompt。
- 大模型传入的参数类型经常漂移（例如把整数 `3` 传成字符串 `'three'`），缺少自动校验与清晰报错。
- 研发同学担心开放文件读写和代码执行工具引发路径穿越（`../../etc/passwd`）或恶意命令执行。

### 迭代目标
- 实现与 LangChain `@tool` 原理 1:1 对齐的装饰器，自动从函数签名、类型注解与 docstring 生成 JSON Schema 与 Pydantic 校验模型。
- 开发企业级安全三件套工具：内网搜索、AST 沙箱计算器、受限沙箱目录文件读写工具。
- 实现 `ToolCallingAgent`、`AgentExecutor` 与 `CallbackHandler` 观测机制，完整捕获 `intermediate_steps`。

### 验收标准
- [x] `@tool` 装饰任意带类型注解的函数后，可导出标准 OpenAI `function` JSON Schema，且调用前自动触发 Pydantic 类型校验。
- [x] 文件读写工具严格拦截任何试图逃逸沙箱目录的相对/绝对路径，代码执行工具拦截危险模块导入。
- [x] `AgentExecutor` 执行结束后返回 `output` 和完整的 `intermediate_steps`，且所有回调事件按序触发。

### 非功能指标
- 工具参数校验失败需转化为结构化错误 Observation，不得导致整个 Agent 进程崩溃。
- 所有文件操作限定在临时测试工作区，测试完成后不污染项目根目录。

## 3. 架构设计与交付清单

在 LangChain 0.2/0.3 现代架构中，官方已经全面主推 `ToolCallingAgent` 取代老旧的正则 ReAct Agent。它的底层核心是 **Schema-Driven Tool Invocation（基于 Schema 驱动的工具调用）**：

1. **自动 Schema 提取层（`@tool`）**：利用 Python 标准库 `inspect.signature` 抽取函数的所有形参、类型注解和默认值，动态调用 `pydantic.create_model` 生成一个专属的 `args_schema` 模型类，再调用 `args_schema.model_json_schema()` 一键输出标准的 JSON Schema。这样既保证了“代码即文档”，又免费获得了 Pydantic 的运行时强类型校验与类型强制转换能力（如把 `'42'` 自动转成 `int(42)`）。
2. **安全边界隔离层（Sandbox Guard）**：工具是 Agent 伸向物理世界的“手”。对于文件读写工具，必须通过 `Path(workspace).resolve()` 计算规范绝对路径，并用 `target.is_relative_to(base_dir)` 防止 `../` 路径穿越；对于代码/表达式执行工具，必须限制在受控 AST 白名单或隔离容器（如 E2B / Docker 沙箱）内执行。
3. **执行器与观测层（`AgentExecutor` + `CallbackHandler`）**：Agent 本身只负责“看历史消息 -> 决定下一步 `ToolCall` 或 `AgentFinish`”，而 `AgentExecutor` 负责外层的 `while` 循环、错误重试、步数控制，并在关键生命周期节点（`on_agent_action`、`on_tool_start`、`on_tool_end`、`on_agent_finish`）广播回调事件。这种“决策与执行解耦”的设计，让日志、监控、前端流式展示都能以插件形式零侵入接入。

### 当日交付代码文件
- `src/day40_tool_schema.py`：步骤一：手写 @tool 装饰器与企业安全工具三件套
- `src/day40_agent_executor.py`：步骤二：实现 ToolCallingAgent、AgentExecutor 与回调观测体系

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
`@tool` 装饰器对缺少 docstring 直接抛 `ValueError` 的做法非常到位，团队里以前有人偷懒不写注释，导致大模型死活不调那个工具。

### Reviewer：阿杰 (后端工程师)（Approved）
文件写入工具建议后续加一个单文件大小限制（比如 1MB），防止大模型抽风吐出几万行重复文本把磁盘写爆。

### Reviewer：林产品 (产品经理)（Approved）
前端同事看了 `TraceCallbackHandler` 的事件流格式，说直接按 `tool_start`/`tool_end` 就能做出酷炫的“AI 正在翻阅文档...”动画效果！

