# STARMIND-022 · Day 22 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 22 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 4 周：第4周：全栈 Web 聊天应用与 FastAPI 后端工程） |
| **需求标题** | 前端速成：HTML/CSS/JS 基础、fetch 通信与企业聊天界面工程 —— AI 工程师也能写体面的交互界面！用 Python 生成并自动化校验星辰智脑企业级聊天前端 |
| **GitLab 分支** | `feat/day22-frontend-chat-ui` |
| **Commit 规范** | `feat(day22): 实现星辰智脑静态企业聊天前端生成器与HTML/CSS/JS安全结构校验器` |
| **配套课件** | `courseware/day22/index.html` |
| **配套 Notebook** | `notebooks/day22/day22_practice.ipynb` |
| **迭代快照** | `versions/day22/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 21）咱们以 100 分 A+ 通过了第 3 周综合周测，把多轮记忆、安全过滤、工具调用和流式事件引擎全部打磨完毕。但林产品发来灵魂拷问：公司 800 个非技术同事不可能打开终端敲 `python main.py` 来用星辰智脑，我们必须有一个打开浏览器就能聊天的 Web 界面！
- **启下（明日演进）**：明天（Day 23）我们正式进入 FastAPI 后端开发（上）：掌握路由、路径/查询参数、Pydantic v2 强类型校验，把 AI 对话封装成标准 REST API 并用 `TestClient` 自动化测试。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑需要一套零重型构建依赖（无需 npm/webpack 也能直接被 FastAPI 托管）的企业级 Web 聊天前端，包含侧边会话栏、消息气泡区、工具状态徽章、输入框与 `fetch` 异步/流式接口对接逻辑。

### 核心痛点
- 后端同学手写 HTML 经常漏写闭合标签、CSS 布局错乱或手机端溢出。
- 直接用 `innerHTML` 拼接用户/模型输出存在严重 XSS 安全漏洞。
- 前端 `fetch` 请求路径、JSON 字段名与后端 FastAPI 契约容易写歪，联调时频繁 404/422。

### 迭代目标
- 编写 `day22_frontend_builder.py`，生成结构清晰、暗亮色变量规范、响应式布局的企业聊天前端三件套（`index.html`、`styles.css`、`chat_app.js`）。
- 在 `chat_app.js` 中使用现代 `async/await` + `fetch('/api/v1/chat/stream', {method: 'POST'})` 与 `ReadableStream` 处理流式响应，且严格使用 `textContent` 防止 XSS。
- 编写 `day22_frontend_validator.py`，基于 Python 标准库 `html.parser` 自动校验标签闭合、DOM 必需 ID、API 端点契约与 XSS 安全规范。

### 验收标准
- [x] 一键生成的 `index.html`、`styles.css`、`chat_app.js` 全部落盘可读且字节非空。
- [x] HTML 校验器验证所有非自闭合标签 100% 匹配闭合，包含聊天容器、表单、输入框和发送按钮关键元素。
- [x] JS 安全校验器确认包含 `fetch` 调用、目标端点 `/api/v1/chat/stream` 且零不安全 `innerHTML` 赋值。

### 非功能指标
- 生成的纯原生 HTML/CSS/JS 不依赖外部 CDN，离线内网环境秒开。
- CSS 使用 `:root` 自定义属性统一品牌色，方便后续换肤。

## 3. 架构设计与交付清单

在企业内部 AI 工具研发中，「FastAPI + 轻量原生静态前端」是极高人效的黄金组合——不需要维护庞大的 `node_modules`，部署只需一个 Python 容器。
1. **三层关注点分离**：`index.html` 专注语义骨架与可访问性（`<aside>` 侧边栏、`<main>` 对话区、`<form>` 输入区）；`styles.css` 用 CSS Variables 与 Flexbox 实现自适应布局；`chat_app.js` 封装状态管理、`fetch` 请求和流式渲染。
2. **防 XSS 安全渲染**：大模型输出极可能包含 `<script>` 或恶意 HTML 标签。我们在 `chat_app.js` 中强制使用 `document.createElement` + `el.textContent = text` 来渲染消息气泡，浏览器会自动把所有尖括号当作纯文本转义。
3. **前端契约自动化校验**：将前端结构与 API 路径检查纳入 Python `pytest` 体系，一旦有人改坏 DOM ID 或写错 `fetch` 路径，CI 立刻红灯告警。

### 当日交付代码文件
- `src/day22_frontend_builder.py`：步骤一：用 Python 生成星辰智脑企业级静态聊天前端（HTML/CSS/JS）
- `src/day22_frontend_validator.py`：步骤二：实现静态前端 DOM 结构、CSS 规范与 JS 安全自动校验器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
用 Python `HTMLParser` + 栈校验把前端结构与防 XSS 规则直接纳入 pytest，全栈工程规范拉满！

### Reviewer：阿杰 (后端工程师)（Approved）
`chat_app.js` 里专门处理了流式分片跨行缓冲 `buffer = lines.pop() || ''`，老手才懂这个坑。

### Reviewer：林产品 (产品经理)（Approved）
界面简洁清爽，侧边栏和状态徽章很有企业工作台的质感！

