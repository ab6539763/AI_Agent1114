# STARMIND-054 · Day 54 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 54 / 70 |
| **所属阶段** | 第 5 阶段：第五阶段：模型微调与部署（第 8 周：模型微调、本地推理部署与安全合规） |
| **需求标题** | 微调效果自动评测、LoRA 权重合并与量化原理 —— 微调前后 A/B 量化对比、矩阵无损合并验证与 GPTQ/AWQ/GGUF 量化选型 |
| **GitLab 分支** | `feat/day54-eval-merge-quant` |
| **Commit 规范** | `feat(day54): 实现微调前后自动评测对比器与LoRA权重合并量化配置器` |
| **配套课件** | `courseware/day54/index.html` |
| **配套 Notebook** | `notebooks/day54/day54_practice.ipynb` |
| **迭代快照** | `versions/day54/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们用防呆 YAML 生成器配好了 Qwen2.5-7B LoRA 训练脚本，并用 Loss 诊断器定位到了验证集最低点的最优 checkpoint-120。
- **启下（明日演进）**：明天（Day 55）我们把今天合并量化好的模型真正拉起来对外提供服务：对比 Ollama 与 vLLM 推理架构，并手写 TTFT/吞吐量并发压测基准工具。

## 2. 业务需求说明 (PRD)

### 业务背景
微调产出的 LoRA 权重上线前必须通过严格的上线门禁（Quality Gate）：既要证明领域指标显著提升，又要保证通用能力不退化，并产出面向不同部署目标（vLLM GPU 集群 / Ollama CPU+GPU 边缘机）的合并与量化方案。

### 核心痛点
- 靠人工肉眼聊三五句主观评价微调效果，缺乏客观指标（ROUGE/关键词覆盖/格式合规/通用回归），经常上线后才发现退化。
- 对 GPTQ、AWQ、GGUF 三种量化格式的适用推理引擎（vLLM vs llama.cpp/Ollama）概念混淆，导出错格式无法加载。

### 迭代目标
- 构建微调前后 A/B 自动评测引擎：计算领域关键词命中率、结构化格式合规率、SLA 承诺准确率与通用能力回归保持率，输出上线门禁判定。
- 实现纯 Python LoRA 权重无损合并数学验证器（验证 `W_merged = W0 + (alpha/r) * B @ A` 推理等价性）及 LLaMA-Factory `export` + 量化选型配置生成器。

### 验收标准
- [x] 评测器能自动对比 baseline 与 finetuned 两组输出并给出 PASS/REJECT 门禁结论（要求领域提升 >= 15% 且通用能力下降 <= 5%）。
- [x] 矩阵合并验证器证明合并前旁路前向与合并后单矩阵前向输出误差 < 1e-9。
- [x] 量化选型器准确映射：vLLM GPU 高并发 -> AWQ/GPTQ，Ollama/端侧 CPU+GPU 混合 -> GGUF Q4_K_M。

### 非功能指标
- 不依赖 PyTorch/NumPy，纯 Python 即可完成数学合并验证与完整评测流水线。

## 3. 架构设计与交付清单

模型微调绝不是 `train` 结束就完事，真正的工业级发布流水线是 **Eval Gate（评测门禁） -> Merge（无损合并） -> Quantize（按需量化）**：

1. **双轨评测门禁（Dual-Track Eval Gate）**：
   - **领域专项轨**：在 Day 52 隔离出的 50 条 eval 集上检查三项硬指标——排查步骤完整度、SLA 时效承诺命中率、结构化编号合规率。
   - **通用回归轨**：用 20 道逻辑推理、代码生成、常识问答测试微调后是否出现灾难性遗忘。只有同时满足'领域显著提升且通用几乎无退化'才放行合并。

2. **LoRA 无损合并（Weight Merging）**：
   推理阶段如果动态挂 LoRA，每次前向都要多算两次矩阵乘并加一次残差；通过 `W_merged = W_0 + (alpha / r) * (B @ A)` 提前合并成标准 Safetensors 权重，可实现 **零额外推理延迟**。

3. **三大主流量化格式选型矩阵**：
   - **AWQ (Activation-aware Weight Quantization, 4-bit)**：保护约 1% 对激活值影响最大的显著权重通道不量化，精度损失极小且在 vLLM 上推理速度最快，**GPU 生产服务器首选**。
   - **GPTQ (4-bit)**：基于校准集的二阶近似逐层量化，生态成熟但校准耗时略长，适合 vLLM/ExLlamaV2。
   - **GGUF (Q4_K_M / Q5_K_M / Q8_0)**：llama.cpp 与 Ollama 专属单文件格式，支持 CPU + GPU 分层卸载（Offload），**本地开发机、Mac M 系列与边缘离线部署首选**。

### 当日交付代码文件
- `src/day54_eval_gate.py`：步骤一：实现微调前后自动化 A/B 评测与上线门禁引擎
- `src/day54_merge_and_quant.py`：步骤二：实现 LoRA 矩阵合并数学验证器与量化导出配置器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
双轨门禁设计得非常到位，特别是把'灾难性遗忘'做成自动化拦截项，这在大厂模型发布评审会（Go/No-Go）上是必查项。

### Reviewer：阿杰（Approved）
终于彻底分清 AWQ 给 vLLM 用、GGUF 给 Ollama 用了，之前一直纳闷为什么 vLLM 加载不了 .gguf 里的某些变体。

