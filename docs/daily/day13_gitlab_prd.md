# STARMIND-013 · Day 13 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 13 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 进阶语法与异步入门 —— 掌握装饰器、yield 生成器、typing、python-dotenv 与 asyncio 并发，为 AI 客户端打造重试与超时护盾 |
| **GitLab 分支** | `feat/day13-decorators-generators-asyncio` |
| **Commit 规范** | `feat(day13): 实现指数退避重试装饰器、yield流式生成器、dotenv配置加载与asyncio并发调度器` |
| **配套课件** | `courseware/day13/index.html` |
| **配套 Notebook** | `notebooks/day13/day13_practice.ipynb` |
| **迭代快照** | `versions/day13/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们成功封装了 OpenAI 兼容 HTTP 客户端并跑通了本地 Mock 降级命令行问答，还用 `httpx.MockTransport` 覆盖了 401/429 异常测试。
- **启下（明日演进）**：明天（Day 14）就是第一阶段收官大考！咱们要把前 13 天的全部内功融会贯通，独立交付阶段考核项目一——**命令行多轮对话 AI 助手（带上下文记忆、JSON 持久化与 `/clear` `/save` `/exit` 指令）**！

## 2. 业务需求说明 (PRD)

### 业务背景
随着星辰智脑开始对接外部大模型接口与批量文档分析任务，团队需要一套通用的底层可靠性与性能组件：避免密钥泄露、自动应对接口偶发抖动、支持流式分块输出以及多任务异步并发提速。

### 核心痛点
- 重试逻辑、耗时统计散落在各个业务函数里，代码重复臃肿。
- API Key 容易被误写进源码提交到 GitLab 造成安全事故。
- 批量调用大模型采用同步串行方式，总耗时随任务数线性暴涨，且缺少单任务超时熔断。

### 迭代目标
- 掌握 `functools.wraps` 编写带参数的指数退避重试装饰器与耗时统计装饰器。
- 掌握 `yield` 生成器实现低内存流式文本分块输出，配合 `typing` 清晰标注类型。
- 掌握 `python-dotenv` 安全读取 `.env` 配置，以及 `asyncio.gather`、`asyncio.wait_for`、`asyncio.Semaphore` 实现带超时与并发上限的异步调用。

### 验收标准
- [x] 重试装饰器能在函数前 N-1 次抛异常、第 N 次成功时自动恢复，超过上限后准确抛出原异常。
- [x] `.env` 配置加载器能读取本地 `.env` 文件且在文件缺失时安全回退到默认配置。
- [x] `yield` 流式生成器返回标准 `Generator` 对象，逐块输出不一次性占用多余内存。
- [x] 异步批量调度器能并发执行多个任务（总耗时远小于串行总和），并对超时的单个任务进行 `asyncio.TimeoutError` 隔离降级。

### 非功能指标
- 重试延迟与异步模拟延时在测试中使用毫秒级数值，确保单元测试 1 秒内跑完。
- 所有公共函数与装饰器具备完整 `typing` 类型注解与文档字符串。

## 3. 架构设计与交付清单

今天构建的是星辰智脑的基础设施工具箱（Infrastructure Toolkit），采用完全解耦的两个模块：
1. **配置与横切中间件模块（day13_decorators_and_env.py）**：
   - 使用 `dotenv.dotenv_values()` 解析 `.env` 文件并映射到强类型 `EnvSettings` 数据类，避免直接污染全局 `os.environ`，天然适配多环境隔离与单元测试。
   - 基于高阶函数闭包与 `@functools.wraps` 实现 `@retry_with_backoff`（指数退避重试）和 `@measure_latency`（耗时审计），实现业务逻辑与容错逻辑彻底解耦（AOP 思想）。
   - 使用 `yield` 实现 `stream_text_chunks()` 流式生成器，模拟大模型 SSE 打字机逐块输出。
2. **异步并发调度引擎（day13_async_llm_runner.py）**：
   - 基于 Python 原生 `asyncio` 事件循环，组合 `asyncio.Semaphore`（控制最大并发数防止把大模型 API 打爆触发 429）、`asyncio.wait_for`（单请求超时熔断）与 `asyncio.gather`（并发汇聚结果），在单线程内实现极高 I/O 吞吐。

### 当日交付代码文件
- `src/day13_decorators_and_env.py`：步骤一：实现 .env 配置加载、指数退避重试装饰器与 yield 流式生成器
- `src/day13_async_llm_runner.py`：步骤二：编写基于 asyncio 的并发大模型批量调用与超时控制引擎

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
`Semaphore` 并发限流 + `wait_for` 超时隔离 + `dotenv_values` 零污染加载，三板斧非常稳健，后面第二阶段写 FastAPI 异步网关可以直接搬过去！

### Reviewer：阿杰 (后端主程)（Approved）
单测里不仅测了功能正确性，还校验了并发耗时确实小于串行总耗时，这种带性能断言的异步测试很赞。

