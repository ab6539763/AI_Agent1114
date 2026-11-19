# STARMIND-063 · Day 63 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 63 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 9 周：星辰智脑毕业设计全栈开发与上线） |
| **需求标题** | 毕业设计开发 Day 5：自动化测试、Ragas 评估报告、并发压测与 Token 成本优化 —— RAG 四维量化评测门禁、异步并发 P95/QPS 压测器与语义缓存+分级路由降本引擎 |
| **GitLab 分支** | `feat/day63-ragas-loadtest-costopt` |
| **Commit 规范** | `feat(day63): 实现Ragas四维评测报告、异步压测器与Token成本优化器` |
| **配套课件** | `courseware/day63/index.html` |
| **配套 Notebook** | `notebooks/day63/day63_practice.ipynb` |
| **迭代快照** | `versions/day63/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们打通了 FastAPI 全量 REST/SSE 接口并完成了前端流式联调，今天给系统做上线前的量化体检与降本增效。
- **启下（明日演进）**：明天（Day 64）进入毕业设计最后一天开发：Docker 容器化部署上线、健康检查巡检、演示脚本与交付文档。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑上线前需向技术评审委员会提交量化质量报告、高并发性能报告与 FinOps 成本优化方案，达到质量门禁后方可准予发布。

### 核心痛点
- 仅靠人工抽查问答无法衡量 RAG 幻觉率与召回覆盖度，迭代容易负优化。
- 不清楚系统在早高峰并发下的 P95/P99 延迟与错误率瓶颈。
- 所有简单 FAQ 都打向昂贵的旗舰云端大模型，月度 API 账单居高不下。

### 迭代目标
- 实现 Ragas 风格四维评测器（Faithfulness / Answer Relevancy / Context Precision / Context Recall）并输出 Markdown 评测报告与发布门禁判定。
- 实现基于 `asyncio` 的并发压测引擎，统计 QPS、P50/P95/P99 延迟与成功率。
- 实现语义缓存（Semantic Cache）+ 难度分级路由（7B 本地 vs 旗舰云 API）成本优化器并量化降本比例。

### 验收标准
- [x] Ragas 评估器准确区分高忠实度回答与编造幻觉回答，并依据门禁阈值输出 PASS/FAIL。
- [x] 并发压测器在 20+ 并发任务下正确计算 QPS 与分位延迟。
- [x] 成本优化器在含重复 FAQ 与简单问答的流量集上实现 >= 40% 的 Token 费用节省。

### 非功能指标
- 全套评估与压测脚本 100% 离线确定性运行，单测耗时 < 2s。

## 3. 架构设计与交付清单

上线前的质量与成本治理体系由三大自动化引擎构成：
1. **Ragas 四维评测门禁**：围绕 `(question, answer, retrieved_contexts, ground_truth)` 四元组，分别度量 **Faithfulness（答案中事实被检索上下文支撑的比例，防幻觉）**、**Answer Relevancy（答案切题度）**、**Context Precision（检索切片信噪比）** 与 **Context Recall（标准答案要点被召回的比例）**。
2. **异步压测引擎**：使用 `asyncio.Semaphore` 精确控制并发度，采集每次请求耗时与成功标记，计算 QPS 及 P50/P95/P99 分位延迟，快速暴露长尾瓶颈。
3. **双层 Token 降本引擎（Cache + Router）**：第一层拦截高频重复问题（缓存命中成本为 0）；第二层根据提问复杂度将简单 FAQ 路由至低成本 7B 模型，仅将复杂多步推理送往旗舰云端模型，综合降本 50%+。

### 当日交付代码文件
- `src/day63_ragas_evaluator.py`：步骤一：实现 Ragas 风格四维评测器与发布门禁报告生成器
- `src/day63_load_and_cost_opt.py`：步骤二：实现异步并发压测器与语义缓存+分级路由降本优化器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
这组量化数据太硬核了！答辩时把 Ragas 四维分 + 压测 P95 + 成本降幅三张卡片摆出来，基本就是高分锁定。

### Reviewer：阿杰（Approved）
建议上线后把缓存命中率和分级路由占比也打到 Prometheus 监控面板上，老板最爱看省了多少钱。

