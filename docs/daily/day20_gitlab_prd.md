# STARMIND-020 · Day 20 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 20 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 3 周：第3周：大模型底层原理、Prompt 工程与工具调用实战） |
| **需求标题** | 多模态与嵌入模型：视觉 API 封装、Embedding 向量与余弦相似度 —— 打通图文理解与语义检索底座，构建星辰智脑多模态客户端与 FAQ 相似问题语义匹配引擎 |
| **GitLab 分支** | `feat/day20-multimodal-embedding` |
| **Commit 规范** | `feat(day20): 实现多模态图像理解/生成API封装与基于余弦相似度的语义匹配引擎` |
| **配套课件** | `courseware/day20/index.html` |
| **配套 Notebook** | `notebooks/day20/day20_practice.ipynb` |
| **迭代快照** | `versions/day20/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 19）我们通过 Function Calling 给大模型装上了双手，成功打通了天气、计算器与内部知识库调用闭环。但客服同学反馈了两个新难题：第一，很多客户遇到报错懒得打字，直接甩一张「报错截图」过来；第二，昨天咱们的知识库检索只能靠精确关键词匹配，员工问「出差住酒店能报多少钱」时，因为没出现「差旅」二字居然搜不到「差旅住宿报销标准」！
- **启下（明日演进）**：明天（Day 21）是第 3 周的周测 + 综合练习日，我们将把本周学的 Prompt、防注入、多轮对话、Function Calling 与流式输出全部拧成一股绳，打造综合引擎并通过自动化周测！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑客服与 IT 支持每天收到大量报错截图与口语化提问（如「住酒店报销上限」「电脑连不上公司内网」），纯文本与字面关键词检索召回率不足 60%。

### 核心痛点
- 客户上传截图后系统无法构建标准 Vision API 请求体，缺乏图片格式校验与 Base64 编码工具。
- 传统 `in` 或 SQL `LIKE` 检索遇到同义词（如「住酒店」vs「差旅住宿」、「连不上内网」vs「VPN 故障」）直接零召回。
- 缺乏相似度阈值控制，导致无关问题也会强行匹配出风马牛不相及的 FAQ 答案。

### 迭代目标
- 封装标准多模态客户端 `MultimodalClient`，支持图片 Base64 Data URI 编码、Vision 图像理解请求构造与文生图（Image Generation）参数封装。
- 实现纯 Python 语义向量化引擎（融合字符 n-gram 与企业同义词语义空间投影）及 L2 归一化、余弦相似度计算。
- 构建 FAQ 相似问题语义匹配器，支持 Top-K 召回与最低相似度阈值拒答（Fallback）。

### 验收标准
- [x] 多模态客户端严格校验 PNG/JPEG/WEBP 魔数或格式并拒绝非法超大负载，构造的 `messages` 100% 符合 OpenAI Vision 协议。
- [x] 相同向量余弦相似度为 `1.0`，正交向量为 `0.0`，反向向量为 `-1.0`；任意非零向量 L2 归一化后模长严格为 `1.0`。
- [x] 语义匹配器能准确将「出差住酒店最多报多少」匹配至「差旅住宿报销标准」，并将完全无关的闲聊（如「今晚吃火锅」）按阈值安全拒答。

### 非功能指标
- 纯 Python 离线可运行，单次 100 条 FAQ 语义检索耗时 < 10ms。
- 接口设计平滑兼容后续替换为 `text-embedding-v3` / `bge-m3` 真实向量模型。

## 3. 架构设计与交付清单

多模态与 Embedding 是打通非结构化企业数据的双引擎：
1. **多模态协议封装（Multimodal Gateway）**：在 OpenAI 兼容协议中，文本消息的 `content` 是字符串，而多模态消息的 `content` 是一个内容块数组：`[{'type': 'text', 'text': '...'}, {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,...', 'detail': 'high'}}]`。生产中必须在编码前校验图片格式（仅允许 `image/png`、`image/jpeg`、`image/webp`）与字节大小上限，防止 OOM。
2. **向量空间与余弦相似度（Cosine Similarity）**：给定两个向量 $A$ 和 $B$，余弦相似度定义为 $\cos(\theta) = \frac{A \cdot B}{\|A\| \cdot \|B\|}$。如果我们在入库前就对所有向量做 **L2 归一化**（即除以自身模长使 $\|A\| = 1$），那么在线检索时余弦相似度就退化为纯粹的点积 $A \cdot B$，省去大量开方计算！
3. **阈值拒答（Threshold Gating）**：任何向量检索都会强行返回 Top-K，哪怕最像的那条其实毫不相干。因此企业级语义匹配器必须设置 `min_score` 阈值（例如 0.35），低于阈值直接返回 `matched=False` 并引导转人工或走兜底策略。

### 当日交付代码文件
- `src/day20_multimodal_client.py`：步骤一：封装多模态图像理解与文生图 API 客户端（MultimodalClient）
- `src/day20_semantic_matcher.py`：步骤二：实现纯 Python Embedding 向量化、余弦相似度与 FAQ 语义匹配工具

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
把同义词检索和阈值拒答都用纯 Python 跑通了，学员理解向量检索原理后，下周切第三阶段 Chroma + BGE-M3 会毫无阻力。

### Reviewer：阿杰 (后端工程师)（Approved）
`MultimodalClient` 拦截了 `application/exe` 和超大图片，线上网关防 OOM 就得这么写。

### Reviewer：林产品 (产品经理)（Approved）
员工终于可以直接问口语化的「住酒店报多少」和甩报错截图了，满意度预计能涨一大截！

