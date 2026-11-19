# STARMIND-047 · Day 47 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 47 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 7 周：Agent 工程化护栏、行业场景与多 Agent 办公助手实战） |
| **需求标题** | 实用 Agent 场景专题 —— Text-to-SQL 只读安全数据分析 Agent（真实 SQLite 销售库）与浏览器/代码助手架构实战 |
| **GitLab 分支** | `feat/day47-text2sql-browser-code-agents` |
| **Commit 规范** | `feat(day47): 实现连接真实SQLite销售库的只读防注入Text-to-SQL Agent及浏览器/代码助手原型` |
| **配套课件** | `courseware/day47/index.html` |
| **配套 Notebook** | `notebooks/day47/day47_practice.ipynb` |
| **迭代快照** | `versions/day47/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 46）我们为 Agent 装上了 Trace/Span 全链路观测、Guardrails 三道安全护栏、死循环熔断和分层降本路由。今天我们把这些硬核工程武器直接投入企业落地率最高的三类垂直 Agent 场景！
- **启下（明日演进）**：明天（Day 48）正式开启第四阶段压轴大戏——「阶段项目三（上）：多 Agent 智能办公助手」，我们将完成整体多 Agent 架构设计、专家角色划分，并一口气落地 5 大企业办公工具集。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科商业分析部每天接到业务线 80+ 个临时取数需求（如“华东区 Q3 销售额最高的 3 个产品是什么？”“各区域平均客单价对比”），数据分析师疲于写重复 SQL；同时研发团队也在探索安全可控的代码自动修复与网页巡检自动化 Agent。

### 核心痛点
- 直接把自然语言转 SQL 执行存在严重的 SQL 注入、写操作误删表以及全表扫描拖垮数据库的风险。
- 大模型偶尔会拼错表名或字段名，缺少将数据库报错回传自纠错的闭环机制。
- 浏览器原始 HTML 动辄数万 Token、代码助手直接覆盖整文件极易引入破坏性改动，亟需工程化架构范式。

### 迭代目标
- 构建真实 SQLite 销售数据库（含 `customers`、`products`、`sales_orders` 三张关联表），实现带 `SQLSafetyGuard` 双重只读保护的 Text-to-SQL 数据分析 Agent。
- 实现 SQL 语法/字段报错自动捕获与自纠错重试机制，并将查询结果自动格式化为业务洞察摘要。
- 实现浏览器自动化（DOM 精简快照 + 动作规划）与代码助手（代码检索 -> Unified Diff 补丁生成 -> 沙箱校验）核心架构原型。

### 验收标准
- [x] 自然语言提问“华东区总销售额”、“各区域销售额排名”或“最畅销商品”时，能生成正确 SQL 并在真实 SQLite 上查出精准数值。
- [x] 任何包含 `DROP/DELETE/UPDATE/INSERT/ALTER/PRAGMA` 或多语句分号 `;` 的 SQL 均被 `SQLSafetyGuard` 100% 拦截。
- [x] 缺少 `LIMIT` 的查询自动追加 `LIMIT 100`；代码助手原型能基于问题生成标准 Diff 并通过校验，所有单测本地 100% 通过。

### 非功能指标
- 数据库连接层强制开启 `PRAGMA query_only = ON`，实现应用层正则校验 + 数据库引擎只读模式双重纵深防御。
- Text-to-SQL 每次执行必须记录最终 SQL、返回行数与耗时，便于数据团队审计。

## 3. 架构设计与交付清单

垂直场景 Agent 能否在企业真正活下来，取决于**领域安全约束（Domain Safety）**与**环境感知压缩（Context Compression）**两大设计：

1. **Text-to-SQL 数据分析 Agent 四层安全架构**：
   - **Schema 精选层**：面对企业几百张表，先按业务域检索最相关的 3~5 张表 DDL 与枚举值样例注入 Prompt；
   - **应用层 `SQLSafetyGuard`**：只允许以 `SELECT` 或 `WITH` 开头的单条查询语句，严格禁止分号多语句注入、注释符混淆以及 `DROP/DELETE/UPDATE/INSERT/ALTER/ATTACH/PRAGMA` 等危险关键字，并自动为无 `LIMIT` 的查询补齐 `LIMIT 100` 防止百万行内存爆炸；
   - **数据库引擎物理只读层**：生产环境使用只读从库 + 只读账号，SQLite 层面显式执行 `PRAGMA query_only = ON`；
   - **自纠错闭环（Self-Correction）**：执行报 `OperationalError: no such column` 时，把错误信息和真实 Schema 回传给规划器自动修正 SQL 并重试（最多 2 次）。
2. **Browser Agent（浏览器自动化）**：千万别把 200KB 原始 DOM 源码扔给大模型！工业级方案（如 Browser-Use / Playwright MCP）只提取可交互元素（`button`、`input`、`a`）生成带编号 `[1] [2] [3]` 的精简 Accessibility Snapshot，模型只需输出 `click(id=2)` 或 `type(id=1, text='...')`。
3. **Coding Agent（代码研发助手）**：遵循“**先定位检索 -> 生成最小化 Unified Diff 补丁 -> 运行单测验证 -> 失败回滚或继续修**”的闭环，绝不盲目重写整个大文件。

### 当日交付代码文件
- `src/day47_text2sql_agent.py`：步骤一：连接真实 SQLite 销售库的只读安全 Text-to-SQL 数据分析 Agent
- `src/day47_browser_code_agent.py`：步骤二：浏览器自动化 DOM 压缩规划器与代码助手 Unified Diff 补丁引擎

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
`SQLSafetyGuard` + `PRAGMA query_only = ON` 双重纵深防御写得非常扎实！而且故意在样本库里放了一条 `CANCELLED` 退单来验证口径过滤，细节满分。

### Reviewer：阿杰 (后端工程师)（Approved）
用 `@pytest.mark.parametrize` 批量覆盖 5 种 SQL 注入和写操作攻击太爽了，以后加新规则只要往列表里追加一行用例就行。

### Reviewer：林产品 (产品经理)（Approved）
商业分析部负责人试跑了华东区销售额统计，看到自动排除取消订单后直接竖了大拇指！

