# STARMIND-033 · Day 33 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 33 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 5 周：第5周：企业级 RAG 全链路、高级检索优化与评估） |
| **需求标题** | 高级RAG技术(下)：BM25混合检索、RRF融合、bge-reranker重排与父文档检索 —— 攻克专有名词、工单号与长文上下文割裂难题，打造大厂标配两阶段精排召回引擎 |
| **GitLab 分支** | `feat/day33-hybrid-rerank-parent-doc` |
| **Commit 规范** | `feat(day33): 实现BM25+向量RRF混合检索、交叉编码器重排序与ParentDocumentRetriever` |
| **配套课件** | `courseware/day33/index.html` |
| **配套 Notebook** | `notebooks/day33/day33_practice.ipynb` |
| **迭代快照** | `versions/day33/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 32）我们用 Query Rewriting、Multi-Query、HyDE 和上下文压缩解决了「员工口语黑话」的表达鸿沟。但测试同学一测研发故障库又报了新 Bug：员工直接搜「ERR-5042 报错怎么排查」或「天枢项目审批流程」，纯向量检索居然把完全不沾边的文档排在前面——因为向量模型压根不认识公司内部代号和错误码！
- **启下（明日演进）**：明天（Day 34）我们将从「调优」跨入「科学评测」：构建企业级 RAG 自动化评测框架（Faithfulness、答案相关性、上下文精确率/召回率），把 RAG 质量变成 CI 流水线里的硬门禁！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑知识库即将接入研发运维故障排查手册（含大量错误码如 ERR-5042、接口名、项目代号如「天枢项目」）与长篇制度全文。纯向量检索在精确编码匹配与长文档上下文完整性上暴露严重短板。

### 核心痛点
- 纯向量检索对错误码（ERR-5042）、内部项目代号（天枢/瑶光）、人名工号等字面精确查询召回率极低。
- BM25 得分范围在 `[0, +∞)` 而余弦相似度在 `[-1, 1]`，直接加权相加极易被单一通路主导。
- 双塔 Embedding（Bi-Encoder）在检索时 Query 与 Doc 互不可见，Top-3 排序精度遇到天花板。
- 切片太小丢上下文、切片太大向量被稀释，传统单粒度切分陷入两难。

### 迭代目标
- 实现支持中文二元词元 + 英文/错误码精确切分的 `BM25Index` 与 `DenseVectorIndex`，并基于 RRF 实现 `HybridRRFRetriever`。
- 实现类 `bge-reranker` 的交叉交互重排器 `BGERerankerSimulator`，完成两阶段「粗排 -> 精排」流水线。
- 实现 `ParentDocumentRetriever`：子切片检索 + 按 `parent_id` 去重回溯完整父文档。

### 验收标准
- [x] 针对「ERR-5042 排查」「天枢项目审批」等精确实体查询，Hybrid RRF 的 Top-1 命中率达到 100%。
- [x] Reranker 精排后，混淆候选文档中的核心答案切片排位显著前移。
- [x] ParentDocumentRetriever 检索命中同一父文档多个子块时能自动去重，并完整返回父文档正文。
- [x] 所有 pytest 自动化单元测试 100% 本地离线通过。

### 非功能指标
- RRF 常数 `k=60` 可配置，支持为 BM25 与向量两路设置权重（默认 `0.5 / 0.5`）。
- 代码结构与生产 `FlagEmbedding` (`BAAI/bge-reranker-v2-m3`) 及 LangChain `ParentDocumentRetriever` 接口保持高度一致。

## 3. 架构设计与交付清单

工业级 RAG 检索引擎普遍采用「两阶段漏斗 + 索引/生成解耦」架构：
1. **第一阶段：多路并行粗排（Recall Stage）**：同时触发 **BM25 倒排索引**（专治错误码、型号、人名、专有名词）和 **Dense 向量索引**（专治同义表达、口语语义），各自召回 Top-10~20 候选集。
2. **RRF（Reciprocal Rank Fusion）无参融合**：抛弃量纲不一致的原始打分，只看每条文档在各路召回中的名次 $r_i(d)$：$\text{RRF}(d) = \sum_i \frac{w_i}{k + r_i(d)}$（工业默认 $k=60$）。如果一篇文档在 BM25 和向量两路都排前列，它的 RRF 得分会断层领先。
3. **第二阶段：Cross-Encoder 精排（Rerank Stage）**：双塔 Embedding（Bi-Encoder）为了速度把 Query 和 Doc 分开编码，丢掉了词级细粒度交互；而 `bge-reranker-v2-m3` 这类 Cross-Encoder 把 `[CLS] Query [SEP] Doc [SEP]` 拼接输入 Transformer，让每个查询词与文档词做全连接自注意力，对 Top-10 候选重新打分截断至 Top-3，精度暴涨且耗时可控（GPU 上 10 对文档仅 ~30ms）。
4. **索引与生成解耦（ParentDocumentRetriever）**：检索时用 60~150 字的小子块（Child Chunk）保证向量表征纯粹；命中后通过 `parent_id` 从 DocStore 取出 600~1000 字的完整父文档（Parent Document）送给 LLM，彻底根治「只搜到半句话、上下文断层」顽疾。

### 当日交付代码文件
- `src/day33_hybrid_rrf.py`：步骤一：实现中英混合分词器、Okapi BM25、Dense 向量索引与 RRF 混合检索器
- `src/day33_rerank_parent.py`：步骤二：实现 Cross-Encoder 重排器（bge-reranker 原理）与 ParentDocumentRetriever

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
中英混合分词器把 `ERR-5042` 单独正则提取出来做得非常扎实，这是企业运维知识库落地的必杀细节。

### Reviewer：阿杰（Approved）
父文档回溯时记得按 `parent_id` 去重并保留子块最高分，不然同一篇长文档如果命中 3 个子块，会把 Top-3 全占满。

