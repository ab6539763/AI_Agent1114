# STARMIND-015 · Day 15 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 15 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 3 周：第3周：大模型底层原理、Prompt 工程与工具调用实战） |
| **需求标题** | 大模型原理科普：NLP演进、Transformer注意力与Token成本核算 —— 揭开大语言模型黑盒，为星辰智脑打造中英文混合 Token 分词估算器与财务成本预测引擎 |
| **GitLab 分支** | `feat/day15-llm-tokenizer-cost` |
| **Commit 规范** | `feat(day15): 实现中英文Token分词估算器、注意力权重演示与大模型月度成本核算工具` |
| **配套课件** | `courseware/day15/index.html` |
| **配套 Notebook** | `notebooks/day15/day15_practice.ipynb` |
| **迭代快照** | `versions/day15/` |

## 1. 上下文衔接

- **承上（昨日基线）**：第一阶段（Day 01 ~ Day 14）我们打牢了 Python 工程基础、面向对象、异常处理、文件处理与 HTTP/API 调用技能，已经能把本地企业文档读写和基础脚本跑得非常顺溜。但昨天财务总监来问：如果把全公司 800 名员工接入星辰智脑，一个月到底要烧多少 API 钱？中文和英文按字算还是按 Token 算？为什么上下文一长模型就变笨？
- **启下（明日演进）**：明天（Day 16）我们将深入大模型 API 核心采样参数（temperature、top_p、max_tokens、frequency_penalty）与流式打字机原理，亲手用代码做参数对比实验。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科即将全员推广「星辰智脑」AI 助手，涵盖研发、客服、运营三个部门。技术委员会要求在正式采购 DeepSeek / 通义千问 / GLM 商业 API 额度前，先交付一套精准的 Token 估算与成本预测工具，并完成研发团队的大模型基础原理对齐。

### 核心痛点
- 业务方误以为 1 个汉字等于 1 个 Token，导致预算拍脑袋、实际账单偏差高达 40% 以上。
- 研发同学不了解上下文窗口（Context Window）和自注意力平方级复杂度，把整本 200 页 PDF 直接塞进 Prompt 导致延迟飙升。
- 不同厂商（DeepSeek-V3、Qwen2.5-Max、GLM-4-Plus、GPT-4o）的输入/输出单价差距悬殊，缺乏横向对比工具。

### 迭代目标
- 实现中英文混合 Token 分词与计数估算器，区分中文汉字、英文单词、数字与代码符号的不同分词倍率。
- 用纯 Python 实现简化版 Scaled Dot-Product Self-Attention 计算演示，直观展示 Token 间注意力权重分布。
- 实现多模型单次调用与月度企业预算核算引擎，支持超预算红线告警与选型建议输出。

### 验收标准
- [x] 中英文混合文本的 Token 估算误差控制在主流 BPE 分词器（如 tiktoken/cl100k_base）合理区间内，且零外网依赖。
- [x] 自注意力权重矩阵每一行之和严格等于 1.0（浮点误差 < 1e-6）。
- [x] 成本估算器支持至少 4 款主流国内外模型，能精准区分输入 Token（Input）与输出 Token（Output）的阶梯定价。

### 非功能指标
- 单次 10,000 字文本的 Token 估算耗时 < 5ms。
- 定价配置与计算逻辑解耦，方便后续随时更新厂商最新官网降价表。

## 3. 架构设计与交付清单

理解大模型底层原理是做好后续 Prompt 工程、RAG 和 Agent 架构的前提。很多工程师把 LLM 当成「会说话的魔法盒」，但从系统工程视角看，现代大语言模型本质上是一个**基于 Transformer Decoder 架构的自回归（Auto-regressive）下一词元概率预测机**。

在星辰智脑的技术设计中，我们重点把握三个核心原理与工程映射：
1. **Tokenizer（分词器）是输入输出的第一道网关**：模型不认识汉字也不认识英文字母，它只认识整数 ID（Token ID）。主流 BPE（Byte-Pair Encoding）词表中，常见英文单词往往是 1 个 Token，而中文汉字通常在 0.6 ~ 1.5 Token/字之间（取决于词表对中文语料的覆盖率，如 Qwen/DeepSeek 对中文优化极佳，约 0.6~0.8 Token/字，而早期 GPT 词表约 1.5~2 Token/字）。因此在系统进入 LLM 前，必须有本地轻量的 Token 估算器做长度守门员。
2. **Self-Attention（自注意力）决定上下文成本**：每个 Token 都会生成 Query（我在找什么）、Key（我有什么特征）、Value（我的实际信息），通过 `softmax(Q·K^T / sqrt(d_k)) · V` 计算全局关联。正因为要两两计算关联，计算复杂度随上下文长度 $N$ 呈 $O(N^2)$ 增长，KV Cache 显存占用线性暴涨——这就是为什么我们不能无脑把所有历史记录全塞给模型。
3. **FinOps 成本治理前置**：企业生产环境中，Output Token 的单价通常是 Input Token 的 2~4 倍（因为 Decode 阶段是串行逐字生成，受限于显存带宽）。我们在架构层引入 `CostEstimator`，把模型单价表配置化，在立项和网关层提前把预算管住。

### 当日交付代码文件
- `src/day15_tokenizer.py`：步骤一：实现中英文混合 Token 分词估算器与简化版 Self-Attention 权重演示
- `src/day15_cost_estimator.py`：步骤二：实现多模型企业级 API 成本估算器与月度预算告警引擎

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
把 `ModelPricing` 设计成 frozen dataclass 很规范，Softmax 里做了减最大值防溢出也是教科书级细节。

### Reviewer：阿杰 (后端工程师)（Approved）
建议在 `estimate_single_cost` 中对负数 Token 做参数拦截，防止上游日志解析异常算出负账单。

### Reviewer：林产品 (产品经理)（Approved）
财务总监看了对比表很满意！下周我们还要加上「上下文缓存命中折扣（Prompt Caching）」的测算项。

