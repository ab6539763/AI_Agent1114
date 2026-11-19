# STARMIND-067 · Day 67 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 67 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 10 周：毕业答辩、简历作品集与面试冲刺结业） |
| **需求标题** | 面试专题(一)——技术八股：Transformer / RAG / Agent / Python 工程高频笔试与手撕代码 —— 纯 Python 手撕 Scaled Dot-Product Attention + 因果掩码 + Top-P 采样，以及令牌桶限流与带 TTL 的 LRU 缓存 |
| **GitLab 分支** | `feat/day67-interview-coding-fundamentals` |
| **Commit 规范** | `feat(day67): 完成面试高频手撕代码(Attention/Top-P/令牌桶限流/TTL-LRU缓存)` |
| **配套课件** | `courseware/day67/index.html` |
| **配套 Notebook** | `notebooks/day67/day67_practice.ipynb` |
| **迭代快照** | `versions/day67/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们用 STAR 法则打磨好了简历并生成了高转化率 GitHub 作品集，今天进入大厂一面最硬核的'技术八股 + 白板手撕代码'专项特训！
- **启下（明日演进）**：明天（Day 68）进入面试专题（二）：项目深挖防问穿与日活十万级企业知识库系统设计及容量估算。

## 2. 业务需求说明 (PRD)

### 业务背景
AI 应用研发岗位一面普遍考察候选人对 Transformer 基础原理、解码采样策略、RAG/Agent 机制以及 Python 高并发后端基础设施的底层手写能力。

### 核心痛点
- 平时只会调 PyTorch/LangChain 高层 API，面试要求白板纯手写 Attention 或 Top-P 采样时卡壳。
- 只背了限流和缓存概念，手写令牌桶（Token Bucket）或带 TTL 的 LRU 缓存时容易漏掉边界条件与时间复杂度退化。

### 迭代目标
- 纯 Python 手撕数值稳定的 Softmax、Scaled Dot-Product Attention（支持 Causal Mask）与 Top-K/Top-P 核采样。
- 纯 Python 手撕 O(1) 复杂度的 TTL-LRU 缓存（基于 `OrderedDict`）与令牌桶限流器（Token Bucket）。

### 验收标准
- [x] Attention 输出权重每行严格归一化和为 1，开启 Causal Mask 后上三角未来位置权重严格为 0。
- [x] Top-P 核采样正确截断尾部低概率 token 并重新归一化。
- [x] TTL-LRU 缓存正确执行过期淘汰与容量淘汰；令牌桶按速率补充并拦截超额突发流量。

### 非功能指标
- 零第三方科学计算库依赖（纯 Python 标准库），pytest 100% 通过。

## 3. 架构设计与交付清单

一面技术八股与手撕的核心在于 **讲清数学直觉 + 写出边界无漏洞的干净代码**：
1. **Scaled Dot-Product Attention 为什么除以 $\sqrt{d_k}$？**
   假设 $q, k$ 各分量独立同分布均值为 0、方差为 1，则点积 $q \cdot k$ 的方差为 $d_k$。维度大时点积绝对值极大，送入 Softmax 会进入梯度几乎为 0 的饱和区导致梯度消失；除以 $\sqrt{d_k}$ 将方差拉回 1，维持训练与数值稳定。
2. **数值稳定 Softmax**：计算 `exp(x_i - max(x))` 避免 `math.exp(1000)` 溢出 `OverflowError`。
3. **Top-P（Nucleus Sampling）**：先按概率降序排列，累加前缀概率直到首次达到阈值 `p`，仅保留最小核心集合并重新归一化，动态适应模型置信度高低。
4. **TTL-LRU 与令牌桶**：`OrderedDict` 借助双向链表 + 哈希表实现 O(1) `move_to_end` 与 `popitem(last=False)`；令牌桶按 `(now - last_ts) * refill_rate` 懒加载补充令牌，无需后台定时线程。

### 当日交付代码文件
- `src/day67_handwritten_transformer.py`：步骤一：纯 Python 手撕 Scaled Dot-Product Attention、因果掩码与 Top-P 采样
- `src/day67_engineering_interview.py`：步骤二：纯 Python 手撕令牌桶限流器与 O(1) TTL-LRU 缓存

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
手撕代码能想到注入 `clock_fn` 用 `time.monotonic` 并且测大数 Softmax 防溢出，面试官直接给你打工程意识满分！

### Reviewer：阿杰（Approved）
`OrderedDict` 手撕 O(1) TTL-LRU 非常简洁，比现场手写双向链表不容易出指针 bug。

