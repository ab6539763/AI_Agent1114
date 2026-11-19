# STARMIND-031 · Day 31 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 31 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 5 周：第5周：企业级 RAG 全链路、高级检索优化与评估） |
| **需求标题** | 周测 + RAG效果调优实验日：核心考点实战与多维消融基准报告 —— 拒绝玄学调参！用 Hit@K、MRR 与消融实验量化 Chunk Size、Top-K 与 Embedding 效果 |
| **GitLab 分支** | `feat/day31-weekly-quiz-rag-ablation` |
| **Commit 规范** | `feat(day31): 完成第4-5周实战周测评测引擎与RAG多维消融实验报告生成器` |
| **配套课件** | `courseware/day31/index.html` |
| **配套 Notebook** | `notebooks/day31/day31_practice.ipynb` |
| **迭代快照** | `versions/day31/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 30）我们跑通了端到端 Naive RAG 知识库问答系统。但在内部试用会上，产品经理林姐问了一个灵魂问题：「老陈，你们把 `chunk_size` 设成 180、`top_k` 设成 3，这是拍脑袋定的还是实测出来的？如果把 `chunk_size` 改成 80 或 300，效果会更好还是更差？」
- **启下（明日演进）**：明天（Day 32）我们正式进入高级 RAG 技术（上）：通过 Query Rewriting、Multi-Query、HyDE 假设性文档嵌入和上下文压缩，正面攻克口语化、模糊提问的召回难题！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑知识库 V1.0 准备向全员开放，但在全量发布前需要通过研发周测验收，并给出一份基于黄金测试集的 RAG 超参数调优基准报告（确定线上默认的 `chunk_size`、`top_k` 与 Embedding 策略）。

### 核心痛点
- 团队成员对 LCEL、Memory 隔离与 RAG 边界条件掌握参差不齐，需要自动化周测检验。
- RAG 超参数（chunk_size / overlap / top_k / embedding）长期靠拍脑袋设定，缺乏量化指标支撑。
- 每次改完检索策略靠人工肉眼测两三个问题，容易「修好一个 Case、弄坏十个 Case」。

### 迭代目标
- 构建覆盖 Day 25~30 五大核心考点的自动化编程周测评测器并 100% 通关。
- 实现检索核心评估指标：Hit@K（命中率）、MRR（平均倒数排名）与平均检索延迟。
- 构建多组超参数网格消融实验引擎（`chunk_size` x `top_k` x `embedding_mode`），自动产出量化对比表与最优配置推荐。

### 验收标准
- [x] 周测 5 道核心实战检查点全部自动验收通过（得分 100/100）。
- [x] 消融实验覆盖至少 6 组不同配置，能准确计算每组的 Hit@K、MRR、切片数和平均耗时。
- [x] 自动输出 Markdown 格式实验对比表格与最优配置结论，pytest 100% 通过。

### 非功能指标
- 消融实验框架可复用于 Day 32~34 的高级 RAG 策略横评。
- 实验结果 100% 确定性可复现。

## 3. 架构设计与交付清单

在企业级 RAG 研发流程中，**「先建评估基线，再做优化迭代」**是铁律。今天我们引入信息检索（IR）领域最经典的两个量化指标来衡量检索器（Retriever）的好坏：
1. **Hit Rate @ K（Top-K 命中率）**：对于测试集中的 $N$ 个问题，只要正确参考文档出现在检索返回的前 $K$ 条结果中就记为 1，否则为 0：
   $$\text{Hit@K} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{I}(\text{gold}_i \in \text{TopK}_i)$$
2. **MRR（Mean Reciprocal Rank，平均倒数排名）**：不仅看有没有命中，还看排在第几位！排第 1 得 $1.0$ 分，排第 2 得 $0.5$ 分，排第 3 得 $0.333$ 分，未命中得 $0$ 分：
   $$\text{MRR} = \frac{1}{N} \sum_{i=1}^{N} \frac{1}{\text{rank}_i}$$

在消融实验中，我们严格遵循「控制变量法」，将语料库和黄金评测集固定，系统性地扫描 `(chunk_size, chunk_overlap, top_k, embedding_mode)` 四维参数空间，把每一次实验的 `Hit@K`、`MRR`、`Chunks` 数量和 `Avg Latency` 全部打成结构化表格，从而科学选出最优线上配置。

### 当日交付代码文件
- `src/day31_weekly_quiz.py`：步骤一：第 4-5 周综合实战周测自动评测引擎
- `src/day31_rag_ablation.py`：步骤二：多维 RAG 消融实验框架（Chunk Size / Top-K / Embedding 量化报告）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
同时校验 `expected_source` 和 `expected_keyword` 是非常严谨的做法！很多初级工程师只校验文件名，结果同一份 50 页手册里召回错了章节还以为自己 Hit@1=100%。

### Reviewer：林产品（Approved）
这个 Markdown 对比表可以直接贴进我们的立项评审文档！建议后面加上「失败样本明细（Bad Case List）」打印，方便我们人工优化知识库原文。

