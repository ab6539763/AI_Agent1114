# STARMIND-059 · Day 59 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 59 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 9 周：星辰智脑毕业设计全栈开发与上线） |
| **需求标题** | 毕业设计开发 Day 1：项目骨架、配置中心与数据库底座 —— Pydantic Settings 配置中心、trace_id 结构化日志、统一异常与 SQLAlchemy 持久化 |
| **GitLab 分支** | `feat/day59-capstone-infra-base` |
| **Commit 规范** | `feat(day59): 搭建星辰智脑配置中心、统一异常日志与SQLAlchemy数据库底座` |
| **配套课件** | `courseware/day59/index.html` |
| **配套 Notebook** | `notebooks/day59/day59_practice.ipynb` |
| **迭代快照** | `versions/day59/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们冻结了《星辰智脑 v1.0》的 PRD 与六大模块架构评审，今天正式敲响毕业设计第一行生产代码。
- **启下（明日演进）**：明天（Day 60）我们在今天的数据库和日志底座之上，开发星辰智脑核心 RAG 知识库主链路：混合检索（BM25+向量）、Rerank 重排与强制引用溯源。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑 v1.0 需在开发首日完成工程底座建设，为后续 RAG、多 Agent、FastAPI 接口与运维监控提供统一的配置读取、全链路追踪日志、错误码规范及关系型数据持久化能力。

### 核心痛点
- 散落的环境变量读取导致线上缺配置直到运行期才崩溃（Fail Late）。
- 纯文本 print 日志无法按 `trace_id` 串联一次对话经过 RAG 和 Agent 的完整耗时。
- 缺少标准化数据持久化层，服务重启后历史会话与审批记录全部丢失。

### 迭代目标
- 基于 `pydantic-settings` 实现启动期强校验配置中心（支持 `.env` 与环境变量覆盖）。
- 实现自定义业务异常体系（`StarMindError` + 规范错误码）与 JSON 格式结构化日志器（支持 `trace_id` 注入）。
- 基于 `SQLAlchemy 2.0` 建立 `sessions`、`messages`、`audit_logs` 三张核心表及 Repository CRUD 封装。

### 验收标准
- [x] 配置中心对非法端口或超界阈值在初始化时立刻抛出 `ValidationError`。
- [x] 结构化日志器输出合法 JSON 字符串，包含 `timestamp`、`level`、`trace_id`、`event` 字段。
- [x] SQLAlchemy 底座在内存/本地 SQLite 上完整跑通会话创建、多轮消息写入与审计记录查询。

### 非功能指标
- 符合 Python 3.11 类型标注规范，零外部数据库服务依赖即可本地运行单测。

## 3. 架构设计与交付清单

优秀的后端工程底座遵循 **Fail-Fast（启动快速失败）+ 可观测性内置 + 存储解耦** 三大原则：
1. **配置中心**：所有密钥、模型地址、预算上限收口到 `StarMindSettings`，应用启动瞬间完成类型与范围校验。
2. **可观测性底座**：每次请求入口生成唯一 `trace_id`，日志以单行 JSON 输出（天然适配 ELK / 阿里云 SLS 日志服务），排查线上问题一条 `trace_id` 过滤就能看到从护栏 -> RAG -> Agent -> LLM 的全链路轨迹。
3. **Repository 模式**：业务层不直接写裸 SQL，而是调用 `StarMindRepository`，本地开发和单测用 SQLite 零配置秒跑，生产环境只需将 `DATABASE_URL` 改为 PostgreSQL 连接串即可无缝切换。

### 当日交付代码文件
- `src/day59_core_infra.py`：步骤一：实现强类型配置中心、统一异常体系与 JSON 结构化日志器
- `src/day59_db_repository.py`：步骤二：实现 SQLAlchemy 2.0 持久化模型与 Repository 仓储层

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
底座非常清爽，SQLAlchemy 2.0 写法标准，错误码和 JSON 日志一步到位。明天直接在这个底座上挂混合检索 RAG。

### Reviewer：阿杰（Approved）
把 `trace_id` 从底座就贯穿进去，以后联调排查慢请求爽太多了。

