# STARMIND-035 · Day 35 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 35 / 70 |
| **所属阶段** | 第 3 阶段：第三阶段：LangChain 与企业级 RAG 开发（第 5 周：第5周：企业级 RAG 全链路、高级检索优化与评估） |
| **需求标题** | LlamaIndex 核心架构与实战：Document/Node/Index/QueryEngine 与框架选型 —— 深入对比 LlamaIndex 与 LangChain 设计哲学，手写 LlamaIndex 风格索引引擎并量化基准评测 |
| **GitLab 分支** | `feat/day35-llamaindex-engine-benchmark` |
| **Commit 规范** | `feat(day35): 实现LlamaIndex核心抽象(Document/TextNode/VectorStoreIndex/QueryEngine)与双框架基准对比` |
| **配套课件** | `courseware/day35/index.html` |
| **配套 Notebook** | `notebooks/day35/day35_practice.ipynb` |
| **迭代快照** | `versions/day35/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 34）我们建好了类 Ragas 四维评估与 CI 门禁体系。但技术委员会在阶段项目二启动前抛来一个经典架构选型题：「做企业级知识库问答，到底是继续用 LangChain，还是换用专门为数据索引而生的 LlamaIndex？别空口白话，拿核心原理和基准数据说话！」
- **启下（明日演进）**：明天（Day 36）我们正式进入**阶段项目二（上）——企业级知识库问答系统 StarMind-KB v2.0**，完成架构设计、多格式文档入库、混合检索+Rerank 引擎与 FastAPI 核心 REST API！

## 2. 业务需求说明 (PRD)

### 业务背景
项目二「企业级知识库问答系统」启动前，架构评审组要求对 LangChain 路线与 LlamaIndex 路线进行原理剖析与小规模 PoC 基准测试，明确两者的适用场景与最终选型结论。

### 核心痛点
- 遇到「请总结一下《差旅报销制度》的核心要点」这类全局摘要提问时，传统 Top-K 向量检索只取回 2~3 个碎片切片，总结严重残缺。
- 普通扁平切片丢失了相邻段落的上下文关系（如「上述标准同样适用于实习生」的「上述」指代上一块）。
- 团队对 LlamaIndex 与 LangChain 的选型停留在网上营销号口水战，缺乏可复现的代码级对比。

### 迭代目标
- 完整实现 LlamaIndex 核心对象模型：`Document`、`TextNode`（含 `SOURCE / PREVIOUS / NEXT` 节点关系）、`SentenceNodeParser`。
- 实现双索引结构：`VectorStoreIndex`（细节精准检索 + 前后节点窗口自动扩展）与 `SummaryIndex`（全节点扫描摘要），并实现 `RouterQueryEngine` 自动路由。
- 编写基准测试脚本，对比 LlamaIndex 风格（Node 拓扑扩展）与 LangChain 风格（扁平切片管道）在上下文完整度、召回率、延迟与开发复杂度上的表现。

### 验收标准
- [x] `SentenceNodeParser` 生成的 `TextNode` 链表必须正确维护 `PREVIOUS` 与 `NEXT` 指针及 `SOURCE` 原文档 ID。
- [x] `RouterQueryEngine` 能自动将「总结/概览」类问题路由至 `SummaryIndex`，将「具体金额/流程」类问题路由至 `VectorStoreIndex`。
- [x] `ResponseSynthesizer` 支持 `compact` 与 `refine` 两种响应合成模式。
- [x] 所有 pytest 自动化测试 100% 本地离线通过。

### 非功能指标
- 给出清晰的官方 `llama-index-core` 生产代码对照与架构选型决策矩阵。

## 3. 架构设计与交付清单

LlamaIndex 的核心架构围绕「数据如何被高效组织、索引与查询」展开，分为 Ingestion（摄取）与 Querying（查询）两大闭环：
1. **Document -> TextNode（带拓扑关系的知识节点）**：与 LangChain 扁平的 `Document` 列表不同，LlamaIndex 的 `NodeParser` 切分后产出的是 `TextNode`，每个节点显式维护 `relationships` 字典（`SOURCE` 指向源文档、`PREVIOUS` 指向前一块、`NEXT` 指向后一块）。这使得检索命中某一块后，可以零成本顺着指针把前后相邻段落一并拉出，彻底解决跨段指代丢失问题。
2. **多态 Index 体系**：
   - `VectorStoreIndex`：将所有 Node 向量化，适合「查具体某一条规定」的点查（Needle-in-a-Haystack）；
   - `SummaryIndex`：遍历所有 Node 聚合上下文，适合「帮我总结这份制度全文讲了什么」的全局摘要查询。
3. **ResponseSynthesizer（响应合成器）**：提供 `compact`（拼装进单次 Prompt 省调用次数）和 `refine`（逐块迭代精炼答案，适合超长文档）等工业级合成策略。
4. **RouterQueryEngine（意图路由查询引擎）**：在最上层挂载多个 `QueryEngineTool`，根据用户问题意图自动把请求分发给 `VectorStoreIndex` 或 `SummaryIndex`，把单点查询和全局总结统一到一个入口！

### 当日交付代码文件
- `src/day35_llamaindex_core.py`：步骤一：手写 LlamaIndex 核心引擎（Document / TextNode 链表 / 双 Index / RouterQueryEngine）
- `src/day35_framework_benchmark.py`：步骤二：LlamaIndex vs LangChain 风格基准横评与架构选型器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
用不到 240 行把 LlamaIndex 最值钱的 `TextNode` 双向链表和 `RouterQueryEngine` 讲透了！很多只会调包的人干了一年都不知道 `PREVIOUS/NEXT` 指针是怎么工作的。

### Reviewer：阿杰（Approved）
基准对比里专门设计了「上述标准」这种跨段指代题，太有说服力了！真实公司制度文档里满屏都是「上述/前述/同上」。

