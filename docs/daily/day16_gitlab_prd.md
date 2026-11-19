# STARMIND-016 · Day 16 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 16 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 3 周：第3周：大模型底层原理、Prompt 工程与工具调用实战） |
| **需求标题** | 大模型 API 核心参数详解：采样控制、对话角色协议与流式打字机 —— 吃透 temperature/top_p/max_tokens/frequency_penalty 底层数学与 stream=True 流式协议 |
| **GitLab 分支** | `feat/day16-llm-api-params-stream` |
| **Commit 规范** | `feat(day16): 实现LLM采样参数模拟器、多角色校验与SSE流式打字机对比实验引擎` |
| **配套课件** | `courseware/day16/index.html` |
| **配套 Notebook** | `notebooks/day16/day16_practice.ipynb` |
| **迭代快照** | `versions/day16/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 15）我们摸清了 Transformer 注意力机制与 Token 成本核算，把财务预算账算明白了。今天林产品提了个新问题：同样一个模型，为什么客服问答有时胡言乱语、有时又像复读机一样车轱辘话？而且用户反馈每次要干等 8 秒才蹦出一整段字，体验太差了！
- **启下（明日演进）**：明天（Day 17）我们将系统进入 Prompt 工程基础，掌握提示词四要素、Zero/Few-shot、XML 安全分隔符与 JSON 结构化约束，搭建星辰智脑 10 大企业场景模板库。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑内测期间，客服与文案两个业务线共用一套默认 API 参数，导致客服工单提取偶尔出现幻觉字段，文案生成又过于死板；同时同步阻塞接口导致长回答等待超过 6 秒，用户频繁刷新页面造成重复扣费。

### 核心痛点
- 研发对 `temperature` 与 `top_p` 理解模糊，经常凭感觉随便填。
- 长文本生成偶尔陷入复读机死循环，缺乏 `frequency_penalty` 与 `max_tokens` 双重兜底。
- 未启用 `stream=True` 流式输出，首字延迟（TTFT）等同于整句生成耗时，前端体验极差。

### 迭代目标
- 实现纯 Python 采样参数模拟器，直观演示 `temperature`、`top_p`、`frequency_penalty` 如何改变下一 Token 概率分布。
- 封装标准 `system` / `user` / `assistant` 三角色消息校验与参数合法性检查。
- 实现 `stream=True` 流式打字机引擎与多组参数对比实验报告生成器。

### 验收标准
- [x] 温度趋近 0 时，采样结果 100% 锁定概率最高的 Token（贪婪解码）；温度升高时概率分布明显趋平。
- [x] 核采样 `top_p` 过滤后剩余候选词的原始累积概率达到阈值且重新归一化之和为 1.0。
- [x] 流式客户端能按 OpenAI SSE chunk 结构逐步产出增量文本、准确记录 TTFT 耗时，并严格遵守 `max_tokens` 上限截断。

### 非功能指标
- 支持传入固定 `seed` 实现完全可复现的自动化单元测试。
- 对越界参数（如 `temperature < 0` 或 `top_p > 1`）在请求发出前即抛出 `ValueError`。

## 3. 架构设计与交付清单

大模型 API 调用看似只是一个 POST JSON 请求，但在企业级平台上，必须将「参数校验」「场景预设（Profile）」「流式通道」做成标准化中间件。

1. **采样解码管线（Sampling Pipeline）**：模型前向传播输出的原始分数叫 Logits。实际采样顺序为：先施加 `frequency_penalty`（按历史出现次数扣减对应词的 logit，抑制复读机） -> 再除以 `temperature`（小于 1 拉大差距更确定，大于 1 拉平差距更有创意） -> 经 Softmax 转为概率分布 -> 按 `top_p`（Nucleus Sampling）从高到低累加概率只保留核心候选池 -> 重新归一化后按概率抽样。
2. **三角色消息状态机**：`system` 是最高优先级的行为宪法（人设、边界、输出格式），`user` 是当前或历史提问，`assistant` 是模型历史回复。生产中必须校验角色合法性，防止前端恶意伪造 `system` 角色。
3. **流式协议（Streaming）**：开启 `stream=True` 后，服务端通过 HTTP Chunked / SSE 协议，每解码出 1~N 个 Token 就立刻推送一个 `delta` JSON 块，最后以 `finish_reason`（`stop` 正常结束 或 `length` 触达 `max_tokens` 截断）收尾。

### 当日交付代码文件
- `src/day16_sampling_simulator.py`：步骤一：实现采样参数校验与 Softmax/Temperature/Top-P/Penalty 数学模拟器
- `src/day16_stream_client.py`：步骤二：实现多角色对话协议、stream=True 流式打字机与参数对比实验

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
采样管线顺序（Penalty -> Temp -> Softmax -> Top-P）完全正确，而且给 `system` 角色做了位置校验，安全意识在线。

### Reviewer：阿杰 (后端工程师)（Approved）
流式输出在触发 `max_tokens` 时正确返回了 `finish_reason='length'`，以后前端就能弹窗提示用户点击「继续生成」。

### Reviewer：林产品 (产品经理)（Approved）
三套场景 Preset 太实用了，后续后台管理页直接做成下拉选项给运营同学选！

