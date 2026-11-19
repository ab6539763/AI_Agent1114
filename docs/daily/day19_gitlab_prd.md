# STARMIND-019 · Day 19 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 19 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 3 周：第3周：大模型底层原理、Prompt 工程与工具调用实战） |
| **需求标题** | Function Calling / Tool Use 重点日：工具协议与纯 API 调用闭环 —— 给大模型装上双手！亲手打通天气查询、安全计算器与星辰内部知识库的 Function Calling 闭环 |
| **GitLab 分支** | `feat/day19-function-calling-loop` |
| **Commit 规范** | `feat(day19): 实现OpenAI规范Tool Schema注册中心与多步Function Calling执行闭环` |
| **配套课件** | `courseware/day19/index.html` |
| **配套 Notebook** | `notebooks/day19/day19_practice.ipynb` |
| **迭代快照** | `versions/day19/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 18）我们用 PromptGuard 守住了安全底线，用 CoT + JSON Mode 实现了高精度意图分类。但林产品提出一个直击灵魂的痛点：纯文本大模型既不知道今天杭州下不下雨，算 18750 * 0.13 税额偶尔会算错，也不知道咱们公司最新的报销差旅标准——它被困在训练截止日期的「鱼缸」里出不来！
- **启下（明日演进）**：明天（Day 20）我们将拓展大模型的「眼睛与语义记忆」：学习多模态图像理解/生成 API 封装，并手写 Embedding 向量化与余弦相似度语义匹配工具。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑内部助手需要能够回答员工的实时办公与计算需求，例如「今天杭州天气怎么样、顺便算一下 12800 元不含税金额（税率 6%）以及查一下杭州出差住宿报销上限」。单靠大模型静态记忆会产生严重幻觉。

### 核心痛点
- 大模型缺乏实时外部数据（天气、汇率、股价）与企业内部私有制度文档。
- 大模型做多位数精确财务计算极易出错，不能直接用于报销核算。
- 缺少标准化 Tool Schema 校验与异常隔离，一旦某个工具报错会导致整个对话崩溃。

### 迭代目标
- 实现符合 OpenAI Tools 规范的 `ToolRegistry` 工具注册中心，内置 `get_weather`、`safe_calculator`、`search_internal_kb` 三大企业工具。
- 使用 Python `ast` 模块实现防代码注入的安全数学计算器，彻底杜绝 `eval()` RCE 漏洞。
- 实现完整的 Function Calling 自动多步执行闭环（含并行多工具调用、`tool_call_id` 精确匹配、最大轮次熔断与轨迹审计）。

### 验收标准
- [x] `export_openai_tools()` 导出的 Schema 100% 符合 OpenAI `type='function'` 标准 JSON Schema 格式。
- [x] `safe_calculator` 能精确计算加减乘除与括号表达式，且对 `__import__('os').system(...)` 等恶意表达式直接拦截抛错。
- [x] 复合问题（同时触发天气 + 计算 + 知识库查询）能在一轮或多轮闭环内完整执行所有工具并整合出准确最终答案。

### 非功能指标
- 工具执行失败时不得抛出未捕获异常中断主循环，必须将错误信息规范封装进 `role='tool'` 返回给模型做优雅降级。
- 默认设置 `max_rounds=5` 防止无限工具调用死循环。

## 3. 架构设计与交付清单

Function Calling 是现代 Agent 架构的基石。很多新手把工具调用写成一堆 `if/else` 硬编码，导致每加一个工具都要改调度主循环。在星辰智脑中，我们采用「注册中心 + 契约校验 + 沙箱执行 + 状态机循环」四层架构：
1. **声明式工具注册中心（ToolRegistry）**：每个工具同时注册「元数据（name、description、JSON Schema parameters）」与「Python 可执行函数（handler）」。Schema 描述写得越清晰，模型填参准确率越高。
2. **安全沙箱执行（Safe Execution）**：工具参数来自模型输出，本质上属于**不可信输入**。因此 `safe_calculator` 严格采用 `ast.parse(..., mode='eval')` 白名单节点求值，只允许数字常量与加减乘除幂运算，任何属性访问、函数调用一律拒绝。
3. **标准闭环状态机（Tool Loop）**：
   - Round 1：发送 `messages + tools` 给模型 -> 模型返回 `assistant` 消息（含 `tool_calls: [{id, function: {name, arguments}}]`）；
   - 本地执行：遍历 `tool_calls`，逐个反序列化 `arguments`、执行工具，并将结果以 `{'role': 'tool', 'tool_call_id': call_id, 'name': name, 'content': json_str}` 追加到 `messages`；
   - Round 2：把包含工具观察结果的完整 `messages` 再次发给模型 -> 若无需再调工具，模型生成最终自然语言回复，循环终止！

### 当日交付代码文件
- `src/day19_tool_registry.py`：步骤一：实现 OpenAI 规范 ToolRegistry 与天气/AST计算器/内部知识库三大工具
- `src/day19_tool_loop_agent.py`：步骤二：实现纯 API Function Calling 多步闭环引擎（支持并行调用与熔断）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
用 AST 写安全计算器还防了大幂运算 DoS，且单测专门构造了 `InfiniteLoopModel` 验证熔断，非常有大厂味！

### Reviewer：阿杰 (后端工程师)（Approved）
`tool_invocations` 轨迹列表非常清晰，后面直接接 OpenTelemetry 或写入数据库就能做 Agent 链路追踪。

### Reviewer：林产品 (产品经理)（Approved）
员工问一句就能同时查天气、查差旅政策、算住宿费，这就是我们想要的星辰智脑！

