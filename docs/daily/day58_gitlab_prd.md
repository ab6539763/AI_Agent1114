# STARMIND-058 · Day 58 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 58 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 9 周：星辰智脑毕业设计全栈开发与上线） |
| **需求标题** | 毕业设计启动：8 大选题矩阵与星辰智脑架构评审 —— 企业级毕业设计选题评估矩阵、星辰智脑 v1.0 PRD 冻结与架构评审门禁 |
| **GitLab 分支** | `feat/day58-capstone-prd-arch-review` |
| **Commit 规范** | `feat(day58): 完成毕业设计8大选题评分矩阵与星辰智脑架构评审工具` |
| **配套课件** | `courseware/day58/index.html` |
| **配套 Notebook** | `notebooks/day58/day58_practice.ipynb` |
| **迭代快照** | `versions/day58/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们高分通过了第五阶段周测，给星辰智脑补齐了双向安全护栏和 Token 成本熔断防线。至此，Python工程、Prompt、RAG、Agent、微调部署五大核心模块全部学完。
- **启下（明日演进）**：明天（Day 59）正式进入毕业设计开发 Day 1：搭建星辰智脑企业级项目骨架、Pydantic 配置中心、统一异常/结构化日志与 SQLite/SQLAlchemy 持久化底座。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科需要整合前期各模块成果，在 6 个研发日内交付可独立演示、可容器化部署、带完整评估报告的企业级 AI 平台《星辰智脑 v1.0》，作为学员毕业答辩与求职核心作品集。

### 核心痛点
- 学员选毕业设计常陷入'套壳聊天框'（太水）或'从零训练百亿模型'（根本做不完）两个极端。
- 缺少明确的接口契约与里程碑拆分，做到第 4 天发现 RAG 和 Agent 数据结构对不上，联调崩溃。

### 迭代目标
- 构建 8 大 AI 应用毕业设计方向加权评估器，结合个人背景推荐最优选题与差异化亮点。
- 建立《星辰智脑 v1.0》架构评审门禁检查器，校验核心模块契约、SLO 指标与 6 天排期依赖完整性。

### 验收标准
- [x] 选题评估器覆盖 8 大主流落地方向（企业知识库RAG、多Agent工作流、NL2SQL问数、智能客服微调、代码审查Agent、合同风控审计、多模态文档解析、AI研发效能平台）。
- [x] 架构评审器能检测缺失核心层（护栏/评估/容器部署）并输出评审结论。

### 非功能指标
- 100% 遵循可本地离线验证原则，所有设计评审可生成结构化 Markdown/JSON 归档。

## 3. 架构设计与交付清单

《星辰智脑 v1.0》采用清晰的分层微服务化单体（Modular Monolith）架构，既具备大厂生产级的代码隔离度，又能在单机 6 天内高质量交付：

- **接入与安全层（Gateway & Guardrail）**：Nginx SSE 反向代理 + FastAPI 路由 + 双向内容安全护栏 + Token 预算熔断器。
- **智能编排层（Orchestration）**：LangGraph 多 Agent 状态机（Intent Router -> RAG Specialist / MCP Tool Specialist / HITL Approval -> Synthesizer）+ 会话级多轮记忆。
- **检索与知识层（Hybrid RAG）**：文档切分 + BM25 词法检索 + 稠密向量检索 + RRF 融合 + Rerank 重排 + 强制 `[doc_id]` 引用溯源。
- **基础底座层（Core Infra）**：Pydantic Settings 配置中心 + JSON 结构化日志（带 `trace_id`）+ SQLAlchemy 持久化 + 统一错误码体系。
- **质量与交付层（Eval & DevOps）**：Pytest 自动化测试 + Ragas 离线评估门禁 + 异步并发压测 + 多阶段 Dockerfile / Compose 一键部署。

### 当日交付代码文件
- `src/day58_topic_matrix.py`：步骤一：实现 8 大 AI 毕业设计选题加权评估与推荐矩阵
- `src/day58_arch_review.py`：步骤二：实现星辰智脑 v1.0 架构评审门禁检查器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
PRD 与 6 天里程碑清晰无歧义，明天开始每天下班前以单测通过 + MR 合并为准，冲！

### Reviewer：林产品（Approved）
验收红线 Recall@5 >= 90%、P95 TTFT <= 1200ms 已经同步给业务方了，期待 Day 64 正式演示！

