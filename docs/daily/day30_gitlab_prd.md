# STARMIND-030 · Day 30 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 30 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 5 周：第5周：企业级 RAG 全链路、高级检索优化与评估） |
| **需求标题** | 完整RAG系统搭建(核心日)：端到端全链路、引用溯源与防幻觉兜底 —— 打通「加载->分割->向量化->存储->检索->增强生成」闭环，打造可信企业知识库命令行助手 |
| **GitLab 分支** | `feat/day30-end-to-end-rag-system` |
| **Commit 规范** | `feat(day30): 组装端到端企业级RAG问答流水线，实现引用来源标注与低分拒答兜底` |
| **配套课件** | `courseware/day30/index.html` |
| **配套 Notebook** | `notebooks/day30/day30_practice.ipynb` |
| **迭代快照** | `versions/day30/` |

## 1. 上下文衔接

- **承上（昨日基线）**：过去 5 天，我们已经像造精密手表一样，把 ChatModel、LCEL 管道、多格式 Loader、中文递归 Splitter 和持久化向量数据库全部亲手打造完毕。今天，是把所有齿轮咬合在一起、让第一版「星辰企业知识库问答系统」真正转起来的核心里程碑日！
- **启下（明日演进）**：明天（Day 31）我们将迎来第 5 周的实战周测与 RAG 效果调优实验日，用量化指标（Hit@K / MRR）系统对比不同分块大小、Top-K 和 Embedding 方案的效果差异。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科新员工入职首月平均向 HR、财务、IT 咨询 15 个重复性制度问题。公司要求上线第一版内部知识库命令行/API 问答原型（Naive RAG v1.0），实现 24 小时自助精准答疑。

### 核心痛点
- 普通大模型不知道公司内部专属制度（如星辰数科年假天数、杭州差旅住宿标准、周五禁发红线），直接问会产生严重幻觉。
- 没有出处标注的回答员工不敢信，依然要找人工二次确认，降本增效落空。
- 用户问到知识库未覆盖的敏感或外部问题时，模型容易强行编造政策，引发劳资或合规风险。

### 迭代目标
- 串联 Day 28~29 组件，实现完整的离线索引构建（Indexing）与在线检索生成（Retrieval & Generation）双流水线。
- 设计强约束 RAG System Prompt，强制模型仅依据检索到的 `[来源1]`、`[来源2]` 作答并在答案末尾附带结构化引用列表。
- 实现基于相似度阈值（`score_threshold`）的「我不知道」兜底拒答机制，并交付星辰知识库 CLI 问答工具。

### 验收标准
- [x] 针对星辰知识库内制度问题（报销/年假/代码发布/VPN），能精准给出答案并标注正确 `[来源N]` 文档名与章节。
- [x] 针对库外无关问题（如「太阳系有几颗行星」或「星辰股票代码是多少」），触发低分阈值拒答，绝不编造。
- [x] 支持按部门 `dept` 过滤查询，命令行与 pytest 单元测试 100% 通过。

### 非功能指标
- 单次端到端检索+生成延迟 < 50ms（离线引擎）/ < 2.5s（云端大模型）。
- 返回结构化 `RAGResponse` 对象（含 `answer`、`citations`、`is_fallback`、`latency_ms`），方便后续直接暴露为 FastAPI 接口。

## 3. 架构设计与交付清单

标准企业级 RAG 系统由两条完全解耦的流水线构成：
1. **离线索引流水线（Offline Indexing Pipeline）**：`Raw Docs -> Loader -> RecursiveCharacterTextSplitter -> Embeddings -> VectorStore`。这条链路在文档上传或定时同步时运行，追求的是解析精度、去重干净与元数据完备。
2. **在线问答流水线（Online Query Pipeline）**：`User Query -> Embedding -> VectorStore.similarity_search_with_score(k, where) -> Score Threshold Gate -> Context Formatter ([来源1]...) -> Grounded Prompt -> ChatModel -> RAGResponse`。

其中最关键的工程护栏是 **双层防幻觉机制**：
- **硬护栏（代码层阈值门控）**：在调用大模型之前，先过滤掉相似度 `< score_threshold` 的噪音切片；如果过滤后候选集为空，直接短路返回标准拒答话术，连一次 LLM Token 都不浪费！
- **软护栏（Prompt 强约束）**：明确告知大模型「只能基于 `<context>` 中的 `[来源N]` 事实作答，每个关键结论后标注 `[来源N]`；如果参考资料不足以回答，请直接回复：知识库中暂未找到相关依据。」

### 当日交付代码文件
- `src/day30_rag_pipeline.py`：步骤一：组装端到端 EnterpriseRAGPipeline（含引用溯源与兜底拒答）
- `src/day30_kb_cli.py`：步骤二：打造星辰数科企业知识库命令行问答工具（CLI）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
全链路非常清晰！`is_fallback` 布尔标志和 `latency_ms` 埋点都考虑到了，上线后接 Prometheus 监控几乎零改动。记得明天做消融实验标定 `score_threshold`。

### Reviewer：林产品（Approved）
演示效果很惊艳！特别是问「食堂红烧肉多少钱」直接拒答没瞎编，老板看了很放心。后续希望前端能把引用原文里命中的关键词高亮出来。

