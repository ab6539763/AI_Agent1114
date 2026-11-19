# STARMIND-053 · Day 53 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 53 / 70 |
| **所属阶段** | 第 5 阶段：第五阶段：模型微调与部署（第 8 周：模型微调、本地推理部署与安全合规） |
| **需求标题** | LLaMA-Factory 微调实战与 Loss 曲线诊断 —— Qwen2.5-7B LoRA YAML 配置生成、超参调优策略与训练过拟合自动诊断 |
| **GitLab 分支** | `feat/day53-llamafactory-yaml-loss` |
| **Commit 规范** | `feat(day53): 实现LLaMA-Factory微调YAML生成器与Loss曲线诊断引擎` |
| **配套课件** | `courseware/day53/index.html` |
| **配套 Notebook** | `notebooks/day53/day53_practice.ipynb` |
| **迭代快照** | `versions/day53/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们产出并质检了 500 条高纯度星辰客服微调语料（450 训练 + 50 验证），已经做好了入炉准备。
- **启下（明日演进）**：明天（Day 54）我们解决微调完之后的事：用自动化评测集对比微调前后效果，并学习如何将 LoRA 权重无损合并回底座，以及 GPTQ/AWQ/GGUF 量化部署原理。

## 2. 业务需求说明 (PRD)

### 业务背景
团队准备使用 LLaMA-Factory 对 Qwen2.5-7B-Instruct 执行 LoRA 微调。此前新人手工修改 YAML 配置常因 template 选错（如给 Qwen2.5 配了 llama3 模板）、learning_rate 过高（1e-3 导致乱码）或有效 batch_size 失衡导致训练失败。

### 核心痛点
- 手工维护 LLaMA-Factory YAML 易填错模型 chat template、cutoff_len 与学习率，浪费宝贵算力。
- 缺乏对 `trainer_log.jsonl` 中 train_loss / eval_loss 曲线的自动化健康诊断，难以判断最佳早停 checkpoint。

### 迭代目标
- 实现防呆的 LLaMA-Factory SFT LoRA YAML 生成器，自动匹配模型模板、计算全局有效 Batch Size 与总训练步数。
- 实现训练日志 Loss 曲线诊断器，自动识别正常收敛、过拟合（eval_loss 拐头上升）、欠拟合与学习率过大（NaN/震荡），并推荐最优 checkpoint 步数。

### 验收标准
- [x] 针对 Qwen2.5-7B 自动锁定 `template: qwen`，强制检查 LoRA 学习率在 `[1e-5, 5e-4]` 合理区间。
- [x] Loss 诊断器能准确区分健康收敛、过拟合、欠拟合与梯度发散四种曲线模式，并给出可执行的调参建议。
- [x] 纯 CPU 环境下 pytest 100% 通过。

### 非功能指标
- 生成的 YAML 严格符合 LLaMA-Factory v0.9+ 命令行 `llamafactory-cli train config.yaml` 规范。

## 3. 架构设计与交付清单

在企业级微调工程化落地中，WebUI 仅用于教学演示和快速探索，真正可复现、可审计的生产训练必须基于 **版本化的 YAML 配置文件 + 自动化指标监控**。

关键超参的工程经验基线（以 Qwen2.5-7B LoRA 为例）：
1. **Chat Template**：必须与底座严格一致（Qwen2.5 用 `qwen`），一旦配错特殊 Token（如 `<|im_start|>`），推理时模型会完全失智。
2. **学习率（Learning Rate）**：LoRA 可训练参数少，学习率通常比全量微调大一个数量级，推荐 `5e-5 ~ 2e-4`（首选 `1e-4`），搭配 `cosine` 退火与 `warmup_ratio: 0.1`。
3. **有效批量大小（Effective Batch Size）**：`EBS = per_device_batch_size × gradient_accumulation_steps × num_gpus`。对于 500 条中小数据集，建议 EBS 控制在 8~16，保证每个 Epoch 有 30~60 次权重更新，总 Epochs 设 3~5 轮即可。
4. **LoRA 挂载目标（lora_target）**：强烈建议设 `all`（覆盖 Attention 的 q/k/v/o 与 FFN 的 gate/up/down 全部线性层），比只挂 `q_proj,v_proj` 效果稳定高出一截。

在 Loss 诊断器设计上，我们同时追踪 `train_loss` 与 `eval_loss` 序列：当检测到 `NaN` 或连续大幅反弹时判为**梯度发散**；当 `train_loss` 持续下降但 `eval_loss` 在最低点之后连续上升超过阈值（如 +8%）时判为**过拟合**，并自动回溯推荐 `eval_loss` 最低处对应的 `best_checkpoint_step`；当两者都居高不下且降幅微弱时判为**欠拟合**。

### 当日交付代码文件
- `src/day53_llamafactory_config.py`：步骤一：实现防呆的 LLaMA-Factory LoRA 微调 YAML 配置生成器
- `src/day53_loss_diagnostics.py`：步骤二：实现训练 Loss 曲线自动诊断与早停推荐引擎

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
把 `load_best_model_at_end: true` 写进默认模板非常赞，这是救命配置。另外建议在训练完后把 `trainer_log.jsonl` 自动归档进 MLflow 或 GitLab Artifact。

### Reviewer：阿杰（Approved）
这个 Loss 诊断器直接挂到训练脚本的回调里，以后不用半夜爬起来看 TensorBoard 曲线了！

