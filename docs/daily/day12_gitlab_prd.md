# STARMIND-012 · Day 12 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 12 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 网络请求与 API 调用 —— 吃透 HTTP 协议与 OpenAI 兼容规范，封装支持本地 Mock 降级的 DeepSeek/通义千问命令行问答工具 |
| **GitLab 分支** | `feat/day12-http-llm-api-client` |
| **Commit 规范** | `feat(day12): 封装OpenAI兼容HTTP大模型客户端与本地Mock降级命令行问答小程序` |
| **配套课件** | `courseware/day12/index.html` |
| **配套 Notebook** | `notebooks/day12/day12_practice.ipynb` |
| **迭代快照** | `versions/day12/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们用 `pathlib`、`re`、`csv`、`datetime` 撸完了星辰知识库批量文档扫描与报表导出工具，本地文件处理这一关已经彻底打通。
- **启下（明日演进）**：明天（Day 13）咱们进入 Python 工程化进阶语法——装饰器、生成器 `yield`、`python-dotenv` 密钥管理与 `asyncio` 异步并发，给今天刚调通的 API 客户端加上自动重试、超时控制与流式输出！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑项目需要正式打通大模型推理能力，首期计划接入 DeepSeek 与通义千问（OpenAI 兼容接口）。但在内网开发和自动化测试环境下无法保证随时拥有外网 API Key，需要客户端具备平滑的本地 Mock 降级能力。

### 核心痛点
- 新手直接裸拼 HTTP 请求容易漏掉 `Authorization: Bearer` 请求头或忘记设置 `timeout` 导致进程永久卡死。
- 直接硬编码某一家大模型 SDK，后期切换 DeepSeek/通义千问成本极高。
- 本地开发和 CI 流水线没有外网 API Key 时无法运行和验证问答主流程。

### 迭代目标
- 理解 HTTP 协议核心要素（URL、POST Method、Headers、JSON Body、状态码 200/401/429/5xx）。
- 掌握 `httpx` / `urllib` / `requests` 的区别与 OpenAI 兼容协议 `/chat/completions` 报文封装。
- 交付具备「真实 HTTP 调用 + 无 Key 自动本地 Mock 降级」的客户端类与第一版命令行 AI 问答小程序。

### 验收标准
- [x] 当 `api_key` 为空或开启 `mock_mode=True` 时，自动返回符合 OpenAI 协议格式的本地 Mock 回复且不发起任何外网请求。
- [x] 当传入 `api_key` 时，能按标准格式组装 `Authorization: Bearer ...` 与 JSON 请求体并发送 POST 请求，正确解析 `choices[0].message.content` 与 `usage`。
- [x] 能准确拦截 401 鉴权失败、429 触发限流、5xx 服务端异常，并给出清晰中文错误提示；通过 `httpx.MockTransport` 离线单测。

### 非功能指标
- 所有网络请求必须显式设置 `timeout` 超时时间，严禁无限等待。
- 命令行问答入口函数支持脚本化输入参数，确保自动化测试不阻塞在 `input()`。

## 3. 架构设计与交付清单

本模块采用「协议与传输解耦 + 本地降级」的清晰两层架构，为后续接入任意 OpenAI 兼容模型打下基石：
1. **大模型 HTTP 客户端层（day12_llm_http_client.py）**：
   - 使用 `@dataclass` 定义强类型的 `LLMRequestConfig` 与 `LLMResponse`，彻底告别散落的字典 key 拼写错误。
   - 将 `build_chat_payload()`（请求体构建）与 `parse_chat_response()`（响应体解析）抽离为纯函数，无论数据来自远程 HTTPS 还是本地 Mock，走的是同一套校验与解析管线。
   - 底层默认使用现代异步/同步通吃的 `httpx.Client`，并支持注入自定义 `transport`（测试时直接注入 `httpx.MockTransport`，不发真实网络包也能覆盖 100% HTTP 分支逻辑）。
2. **命令行 AI 问答交互层（day12_cli_qa.py）**：
   - 封装 `ask_once()` 单轮提问与 `run_cli_qa()` 交互循环，支持通过 `inputs` 参数注入测试脚本，彻底规避顶层阻塞 `input()` 的工程坏习惯。

### 当日交付代码文件
- `src/day12_llm_http_client.py`：步骤一：封装 OpenAI 兼容 HTTP 大模型客户端（含本地 Mock 降级）
- `src/day12_cli_qa.py`：步骤二：组装第一版命令行 AI 问答小程序（支持脚本化非阻塞测试）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
用 `httpx.MockTransport` 把 200/401/429 三条 HTTP 分支全测透了，还不花一分钱 Token，这才是大厂写 API 客户端的标准姿势！

### Reviewer：阿杰 (后端主程)（Approved）
`run_cli_qa` 把 `inputs` 参数化做得很好，CI 流水线跑测试完全不会卡死在 `input()` 上。

