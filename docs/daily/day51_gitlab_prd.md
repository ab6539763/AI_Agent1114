# STARMIND-051 · Day 51 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 51 / 70 |
| **所属阶段** | 第 5 阶段：第五阶段：模型微调与部署（第 8 周：模型微调、本地推理部署与安全合规） |
| **需求标题** | 模型微调理论与显存精确估算 —— 微调 vs RAG vs Prompt 决策树、LoRA/QLoRA 数学本质与 GPU 显存计算器 |
| **GitLab 分支** | `feat/day51-finetune-theory-vram-calc` |
| **Commit 规范** | `feat(day51): 实现微调决策引擎与GPU显存精确估算工具` |
| **配套课件** | `courseware/day51/index.html` |
| **配套 Notebook** | `notebooks/day51/day51_practice.ipynb` |
| **迭代快照** | `versions/day51/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们完成了第四阶段多 Agent 协作与 MCP 工具生态的周测验收，星辰智脑已经能通过调外部 API 跑通复杂业务流。但财务部和法务部反馈：通用大模型对公司内部《政企招投标术语》和《星辰ERP单据规范》老是答偏，而且按 Token 计费月底账单已经破万。
- **启下（明日演进）**：明天（Day 52）我们正式进入数据工程实战，手写清洗、去重、质量过滤与 Self-Instruct 合成流水线，给 Qwen2.5-7B 造出 500 条高质量星辰客服微调语料。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科智能客服与政企标书辅助场景面临两大痛点：通用闭源 API 成本居高不下（月均 1.8 万元），且在特定话术格式、内部专有缩写理解上不稳定。团队计划评估私有化微调 Qwen2.5-7B-Instruct 的可行性与算力预算。

### 核心痛点
- 业务方动辄要求'微调一个专属大模型'，缺乏量化的技术选型标准，容易陷入高成本低收益陷阱。
- 研发同学租用云端 GPU（AutoDL 4090 / A800 / 魔搭）时仅凭感觉估显存，频繁触发 CUDA OOM 导致训练中断浪费算力费。
- 对全量微调、LoRA、QLoRA 在参数量、优化器状态、激活值显存占用上的差异缺乏直观计算工具。

### 迭代目标
- 构建可量化的 Prompt / RAG / Fine-Tuning 三维决策评估器，输出推荐路线与理由。
- 实现高精度 GPU 显存估算器，覆盖模型权重、梯度、AdamW 优化器状态、LoRA 旁路矩阵与 KV/激活值开销。
- 内置国内主流算力平台（AutoDL 4090 24G、A100 80G、魔搭免费实例等）推荐匹配与成本预估。

### 验收标准
- [x] 决策引擎针对'实时知识更新'场景推荐 RAG，针对'固定JSON风格/领域话术'推荐 LoRA 微调。
- [x] 显存计算器对 Qwen2.5-7B 在 FP16 全量微调（>110GB）、FP16 LoRA（~18-22GB）、4-bit QLoRA（~9-12GB）的估算误差在工程可接受区间内。
- [x] 所有核心函数具备完整单元测试且在纯 CPU 环境下 100% 通过。

### 非功能指标
- 纯 Python 3.11 实现，不依赖 PyTorch 或真实 GPU 驱动即可完成精确预算核算。
- 支持 CLI 与模块导入双模式，便于后续接入 CI 算力审批流程。

## 3. 架构设计与交付清单

在企业级大模型落地中，技术选型失误的代价远高于代码 Bug。我们采用'先诊断、后算账、再动手'的两段式架构：

第一段是 **微调选型决策引擎（StrategyAdvisor）**。它接收业务场景的 5 个核心维度指标：知识更新频率（daily/monthly/static）、输出格式与风格严格度（1~5）、自有高质量标注数据量（条数）、私有化数据合规要求（bool）、推理延迟与成本敏感度（1~5）。通过加权规则树与冲突检测（例如：知识每天变但强行要求微调，系统会直接标红警告'微调无法解决实时知识幻觉，请优先 RAG'），输出主推方案（Prompt / RAG / LoRA / RAG+LoRA 混合架构）与实施路径。

第二段是 **显存与算力预算器（VRAMCalculator）**。训练时显存消耗由四大部分组成：
1. 模型权重（Weights）：FP16/BF16 占 2 Bytes/参数，NF4（QLoRA）约占 0.55 Bytes/参数（含量化缩放因子）。
2. 梯度（Gradients）：全量微调对全部参数存梯度（2~4 Bytes/参数），LoRA/QLoRA 仅对可训练低秩矩阵存梯度（通常不到总参数的 1%~2%）。
3. 优化器状态（Optimizer States）：标准 AdamW 维护 FP32 主权重副本 + 一阶动量 + 二阶动量，全量微调高达 12 Bytes/参数；而 LoRA 仅针对可训练参数维护 AdamW，8-bit Paged AdamW 更可进一步压缩至 2 Bytes/可训练参数。
4. 激活值与框架缓冲（Activations & Overhead）：与 batch_size、seq_len、层数、隐藏层维度正相关，开启 Gradient Checkpointing 可将激活显存压低约 65%~75%。
结合国内 AutoDL（RTX 4090 24G 约 2.0 元/时、A800 80G 约 9.5 元/时）与魔搭免费算力池，系统能自动推荐最具性价比的显卡配置。

### 当日交付代码文件
- `src/day51_strategy_advisor.py`：步骤一：实现微调 vs RAG vs Prompt 企业选型决策引擎
- `src/day51_vram_calculator.py`：步骤二：实现 GPU 显存精确估算器与国内算力平台推荐器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
显存计算器里把 `gradient_checkpointing` 对激活值的影响独立拆出来了，这点非常实用。建议后续在 README 里补上实测 4090 跑 LLaMA-Factory 的 nvidia-smi 截图对照。

### Reviewer：阿杰（Approved）
以前总觉得 7B 模型 14G 权重，24G 卡肯定能全量训，看完优化器状态占 85G 才彻底明白为什么之前一跑就炸显存。

### Reviewer：林产品（Approved）
决策报告输出很清晰，我拿去给业务总监汇报了：咱先保留现有 RAG，再花 4 块钱租 2 小时 4090 试一版 Qwen2.5-7B LoRA 客服话术！

