# STARMIND-032 · Day 32 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 32 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 5 周：第5周：企业级 RAG 全链路、高级检索优化与评估） |
| **需求标题** | 高级RAG技术(上)：Query改写、Multi-Query、HyDE与上下文压缩 —— 专治「员工问得太口语、公司文档太书面」的检索鸿沟，大幅拉升复杂提问召回率 |
| **GitLab 分支** | `feat/day32-advanced-rag-query-transform` |
| **Commit 规范** | `feat(day32): 实现QueryRewriter、MultiQuery、HyDE与上下文压缩器并完成召回率对比实验` |
| **配套课件** | `courseware/day32/index.html` |
| **配套 Notebook** | `notebooks/day32/day32_practice.ipynb` |
| **迭代快照** | `versions/day32/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 31）我们用消融实验摸清了 Naive RAG 的最佳参数。但产品经理把第一批员工内测日志发过来，大家一看傻眼了：员工根本不按制度原文提问！他们问的是「去魔都出差住店能报多少？」「礼拜五下班前能不能推线上？」「电脑连不上公司内网咋整？」。这种口语/简称提问，单路 Naive 检索召回率直接掉了一大截。
- **启下（明日演进）**：明天（Day 33）我们将进入高级 RAG 技术（下）：攻克专有名词和精确编号检索难题，亲手实现 BM25 + 向量混合检索、RRF 倒数排名融合、bge-reranker 重排序与父文档检索器！

## 2. 业务需求说明 (PRD)

### 业务背景
内测期间统计发现，约 35% 的员工提问存在地域别称（如魔都/帝都）、口语化表达（推线上/住店/请病假条）或复合多意图提问，导致 Naive RAG 单次直接检索漏召回。

### 核心痛点
- 用户口语/公司黑话与正式规章制度措辞差异大，直接做向量检索相似度偏低。
- 复合问题（如「出差住宿和吃饭怎么报？」）单次查询容易只召回住宿而漏掉餐补。
- Top-4 检索结果中往往夹杂大量与当前提问无关的相邻条款，浪费 LLM Token 且分散注意力。

### 迭代目标
- 实现 `QueryRewriter`（术语规范化与口语改写）、`MultiQueryRetriever`（多视角扩展 + 去重合并）和 `HyDERetriever`（假设性文档嵌入检索）。
- 实现 `ContextualCompressor`（句子级相关性提纯，过滤低相关噪音句并统计压缩率）。
- 在口语化/黑话测试集上运行 Baseline vs QueryRewrite vs Multi-Query vs HyDE 召回率对比实验。

### 验收标准
- [x] 针对「魔都住店」「礼拜五推线上」等口语难题，QueryRewrite / Multi-Query / HyDE 的召回率显著高于 Naive 基线。
- [x] 上下文压缩器在保留核心答案句子的前提下，平均压缩掉至少 35% 的冗余字符。
- [x] 所有 pytest 单元测试与对比实验脚本 100% 通过。

### 非功能指标
- Multi-Query 支持多查询结果去重（保留最高分），避免重复切片污染 Top-K。
- 提供清晰的生产级 LangChain `MultiQueryRetriever` / `ContextualCompressionRetriever` 代码对照。

## 3. 架构设计与交付清单

高级 RAG 的核心思想是「把原本一次性的向量查找，升级为多阶段智能检索流水线」：
1. **Query Rewriting（查询改写）**：在检索前加一道极轻量的改写层（生产可用企业同义词词典 + 7B 小模型），将「魔都住店」规范化为「上海 一线城市 出差 酒店 住宿报销标准」，延迟增加极小（<100ms），ROI 最高。
2. **Multi-Query（多路查询扩展）**：面对复合问题或歧义问题，生成 3 个不同表述的子查询并发检索向量库，再按文档指纹去重取最高分合并，显著提升 Recall（召回率）。
3. **HyDE（Hypothetical Document Embeddings，假设性文档嵌入）**：用户问句通常很短（10 字）且是疑问句，而知识库切片是长陈述句（200 字），两者在向量空间天然存在分布偏移。HyDE 先让 LLM 根据问题生成一段「假设性的制度说明文档」，再对这段假设文档做 Embedding 去检索真实知识库——即使假设文档里的数字是编的，它的句式、领域词和语义结构与真实制度高度一致，从而实现「以文档搜文档」的精准命中！
4. **Contextual Compression（上下文压缩）**：检索出候选切片后，按句切分并计算每句与 Query 的相关度，剔除无关背景句，既省 Token 又减少大模型注意力分散。

### 当日交付代码文件
- `src/day32_query_transform.py`：步骤一：实现 QueryRewriter、MultiQueryRetriever 与 HyDERetriever
- `src/day32_compression_eval.py`：步骤二：实现上下文压缩器（ContextualCompressor）与召回率量化对比实验

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
压缩后按原始句子下标 `idx` 恢复语序这个细节很专业！否则把「但是…」排在「原则上…」前面会让大模型理解反了。

### Reviewer：阿杰（Approved）
企业同义词词典 `TERM_MAPPING` 后续可以做成 YAML/数据库热加载，运维同学随时加新黑话不用发版。

