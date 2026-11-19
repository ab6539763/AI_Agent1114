# STARMIND-036 · Day 36 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 36 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 6 周：第6周：阶段项目二——企业级知识库问答系统实战与答辩） |
| **需求标题** | 阶段项目二(上)：企业级知识库问答系统——架构、多格式入库、混合检索与FastAPI服务 —— 从零搭建 StarMind-KB v2.0 生产级后端：文档解析入库 + BM25/向量混合检索 + Rerank + REST API |
| **GitLab 分支** | `feat/day36-project2-kb-backend-api` |
| **Commit 规范** | `feat(day36): 完成项目二(上)多格式文档入库管线、混合检索+Rerank引擎与FastAPI核心接口` |
| **配套课件** | `courseware/day36/index.html` |
| **配套 Notebook** | `notebooks/day36/day36_practice.ipynb` |
| **迭代快照** | `versions/day36/` |

## 1. 上下文衔接

- **承上（昨日基线）**：前两周（Day 25~35）我们把 LangChain、文档加载切分、向量检索、高级 RAG 混合检索+Rerank、Ragas 评估和 LlamaIndex 核心原理全部打通了。现在，是时候把所有零散积木拼装成一座真正可上线的企业级系统了！
- **启下（明日演进）**：明天（Day 37）我们将完成**阶段项目二（下）**：为 StarMind-KB v2.0 补齐多会话记忆、多轮指代消解改写、引用溯源 `<mark>` 高亮展示、SSE 打字机流式输出接口与全链路 TestClient 联调！

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科全员 800+ 员工急需统一的内部企业知识库问答平台（StarMind-KB v2.0），覆盖 HR 制度、财务报销、研发规范与运维排障四类多格式文档，并要求严格的部门数据权限隔离与可溯源回答。

### 核心痛点
- 公司制度文档散落在 Markdown 手册、CSV 费用标准表、JSON 故障码字典和 TXT 通知中，格式五花八门。
- 高管/财务敏感文档不能被普通研发人员搜到，缺少部门级元数据权限过滤（ACL）。
- 制度修订后，旧版本切片残留在索引里导致回答新旧打架，缺乏按 `doc_id` 幂等覆盖更新与删除能力。

### 迭代目标
- 构建 `MultiFormatParser`：统一解析 `md`、`txt`、`json`、`csv` 四种企业常见文档格式并切分保留 `section / department / chunk_index` 元数据。
- 构建 `EnterpriseKBEngine`：支持文档幂等 Upsert、按 `doc_id` 软/硬删除、部门 ACL 权限过滤、`BM25 + Dense RRF + Cross-Encoder Rerank` 精排与低分防幻觉拒答。
- 基于 FastAPI 构建生产级 REST API：`GET /health`、`POST /api/v1/documents/ingest`、`GET /api/v1/documents`、`DELETE /api/v1/documents/{doc_id}`、`POST /api/v1/qa/query`。

### 验收标准
- [x] 成功通过 HTTP API 分别入库 Markdown、JSON、CSV 文档，并支持相同 `doc_id` 重复入库时自动覆盖旧切片（不产生脏数据）。
- [x] 当 `department='rd'` 发起查询时，绝不返回 `department='finance'` 的机密文档切片（ACL 隔离 100% 生效）。
- [x] 针对库外无关提问（如「火星大气成分」）自动触发防幻觉拒答（`refused=True`）。
- [x] 使用 `fastapi.testclient.TestClient` 完成全接口集成测试，100% 通过。

### 非功能指标
- 所有接口输入输出均采用 Pydantic v2 BaseModel 强类型校验，返回字段包含 `latency_ms` 便于监控大盘采集。
- 服务层（`EnterpriseKBEngine`）与 Web 路由层（`FastAPI`）严格解耦，便于单元测试与后续横向扩展。

## 3. 架构设计与交付清单

StarMind-KB v2.0 后端严格遵循经典**三层整洁架构（API 路由层 -> 领域服务层 -> 索引存储层）**：
1. **多格式解析层（MultiFormatParser）**：
   - `md`：按二级标题 `## ` 自动识别章节 `section` 再滑动切分；
   - `json`：解析对象或列表，将结构化 KV（如故障码字典）转化为高可读自然语言条款；
   - `csv`：按表头+行记录逐行语义化拼接，避免表格切分丢表头；
   - `txt`：按段落边界切分。
2. **文档生命周期与幂等 Upsert**：每篇文档拥有唯一 `doc_id`。当业务更新文档重新上传时，引擎先清理该 `doc_id` 对应的全部旧切片再写入新切片，彻底杜绝「2025 旧报销标准和 2026 新标准同时被搜出来」的经典线上 Bug。
3. **安全优先的 ACL 过滤**：在检索打分前先按 `department in (user_dept, 'public')` 过滤候选集（Pre-Filtering），从根源阻断越权信息泄露。
4. **FastAPI 应用工厂模式（`create_app(engine=None)`）**：避免全局单例污染测试环境，方便 `pytest` 每次注入全新隔离实例并行测试。

### 当日交付代码文件
- `src/day36_kb_engine.py`：步骤一：实现多格式文档解析、ACL 权限过滤与混合精排引擎（EnterpriseKBEngine）
- `src/day36_kb_api.py`：步骤二：构建 StarMind-KB v2.0 FastAPI 后端服务与 Pydantic 强类型契约

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
幂等 Upsert 和部门 ACL Pre-Filtering 做得很漂亮！很多初级工程师只顾着写检索，上线一周就因为文档修订后旧切片没删被 HR 投诉。

### Reviewer：阿杰（Approved）
采用 `create_app()` 工厂函数让 TestClient 隔离性满分，后续对接 Docker/K8s 健康探针直接配 `/health` 即可。

