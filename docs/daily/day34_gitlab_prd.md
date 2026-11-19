# STARMIND-034 · Day 34 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 34 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 5 周：第5周：企业级 RAG 全链路、高级检索优化与评估） |
| **需求标题** | RAG 评估体系：Faithfulness、答案相关性、上下文精确率/召回率与类 Ragas 框架 —— 告别「肉眼拍脑袋看效果」，建立 CI 自动化 RAG 评测流水线与质量门禁 |
| **GitLab 分支** | `feat/day34-ragas-eval-framework` |
| **Commit 规范** | `feat(day34): 实现Faithfulness/AnswerRelevancy/ContextPrecision/ContextRecall四维评测器与Ragas风格报告` |
| **配套课件** | `courseware/day34/index.html` |
| **配套 Notebook** | `notebooks/day34/day34_practice.ipynb` |
| **迭代快照** | `versions/day34/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 33）我们上线了「BM25 + 向量 + RRF + Reranker + 父文档」超级检索引擎。但在评审会上，老板直接灵魂发问：「你们说新版本比 Naive RAG 强很多，到底强了多少？幻觉率降到多少了？有没有数据报告？上线后万一改了个 Prompt 把旧功能改坏了怎么兜底？」
- **启下（明日演进）**：明天（Day 35）我们将探索另一个企业级 RAG 顶流框架——LlamaIndex，拆解其 Document/Node/Index/QueryEngine 架构，并与 LangChain 路线做全面基准对比选型！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑 RAG 引擎即将进入项目二全量开发，团队需要一套自动化、可重复执行的 RAG 评估工具，对每次切片策略、Prompt、模型或检索器变更进行量化回归测试。

### 核心痛点
- 靠人工肉眼看 5~10 条问答主观打分，既耗时又容易漏掉隐蔽的「数字幻觉」（如把 600 元说成 800 元）。
- 当回答出错时，团队经常扯皮：到底是「检索没搜回来」还是「搜回来了但大模型瞎编」？缺乏分维度诊断。
- 缺乏 CI 质量门禁，一次不经意的 Prompt 修改可能导致历史高优场景退化。

### 迭代目标
- 实现 Ragas 核心四维评估指标：`compute_faithfulness`、`compute_answer_relevancy`、`compute_context_precision`、`compute_context_recall`。
- 实现 `MiniRagasEvaluator` 批量评测引擎：支持单样本诊断（精准定位「幻觉 / 漏召回 / 排序差 / 答非所问」）、CI 门禁校验与 Markdown 对比报告生成。
- 对比评测 `v1_naive_rag` 与 `v2_hybrid_rerank_rag` 两套系统在黄金测试集上的四维得分。

### 验收标准
- [x] 包含编造数字（如上下文写 600 元、回答写 800 元）的幻觉样本，`Faithfulness` 得分必须显著低于忠实样本（< 0.6）。
- [x] 相关上下文排在 Top-1 的样本，`Context Precision` 必须严格高于排在末尾的样本。
- [x] CI 门禁能准确拦截不达标版本（`gate_passed == False`），放行达标版本（`gate_passed == True`）。
- [x] 所有 pytest 自动化测试 100% 本地离线通过。

### 非功能指标
- 评测指标全部输出 `[0.0, 1.0]` 规范化浮点分，保留 4 位小数。
- 提供生产环境官方 `ragas` + `LLM-as-a-Judge` 接入代码对照。

## 3. 架构设计与交付清单

一套成熟的 RAG 评估体系必须将「检索质量」与「生成质量」彻底解耦，才能做到精准归因：
1. **Faithfulness（忠实度，防幻觉核心）**：不依赖人工标准答案（Reference-Free），只对比 `Answer` 与 `Retrieved Contexts`。先把回答拆成 $N$ 条独立原子陈述（Claims），逐条检查是否能从上下文中推导出来（重点核查数字、专有名词与核心谓词），$\text{Faithfulness} = \frac{N_{\text{supported}}}{N}$。
2. **Answer Relevancy（答案相关性）**：衡量回答是否直接回应了 `Question`（防止模型把检索到的无关制度整段背出来充数）。
3. **Context Precision（上下文精确率）**：采用信息检索经典的 **Average Precision (AP@K)** 公式：$\text{AP@K} = \frac{\sum_{k=1}^{K} P@k \cdot \text{rel}_k}{\sum_{k=1}^{K} \text{rel}_k}$。同样是 3 条上下文里有 1 条相关，排第 1 名得分 `1.0`，排第 3 名得分只有 `0.3333`——专门用来检验 Reranker 到底有没有起作用！
4. **Context Recall（上下文召回率）**：把人工标注的 `Ground Truth` 拆成核心事实点，计算其中有多少比例能在 `Retrieved Contexts` 里找到依据，专门用来检验切片和召回有没有漏掉关键条款。

### 当日交付代码文件
- `src/day34_rag_metrics.py`：步骤一：实现 Ragas 四维核心评估算法（Faithfulness / Relevancy / Precision / Recall）
- `src/day34_ragas_runner.py`：步骤二：实现类 Ragas 自动化评测框架（MiniRagasEvaluator）与 CI 质量门禁报告

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
对数字做强一致性校验非常贴合财务和运维制度场景！生产中哪怕只错一个小数点，业务部门就会彻底丧失对 AI 助手的信任。

### Reviewer：林产品（Approved）
这个 Markdown 对比表太直观了！周会汇报我直接截图贴 PPT，老板一眼就看懂研发投入的 ROI。

