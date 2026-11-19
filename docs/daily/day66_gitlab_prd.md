# STARMIND-066 · Day 66 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 66 / 70 |
| **所属阶段** | 第 6 阶段：第六阶段：毕业设计与就业冲刺（第 10 周：毕业答辩、简历作品集与面试冲刺结业） |
| **需求标题** | 简历与作品集打磨：STAR 法则项目包装、GitHub 主页 README 与作品集生成器 —— 量化简历体检 Linter、STAR 黄金句式生成器与高转化率 GitHub 作品集主页构建 |
| **GitLab 分支** | `feat/day66-resume-portfolio-kit` |
| **Commit 规范** | `feat(day66): 实现STAR法则简历量化体检器与GitHub作品集README生成器` |
| **配套课件** | `courseware/day66/index.html` |
| **配套 Notebook** | `notebooks/day66/day66_practice.ipynb` |
| **迭代快照** | `versions/day66/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们高质量完成了星辰智脑毕业答辩，今天开始把这 65 天的硬核工程资产转化为能拿大厂面试邀约的王牌简历与 GitHub 作品集。
- **启下（明日演进）**：明天（Day 67）进入面试专题（一）——技术八股与手撕代码：手写 Attention、Top-P 采样、令牌桶限流与异步并发池。

## 2. 业务需求说明 (PRD)

### 业务背景
学员即将投递国内互联网大厂及 AI 独角兽的 AI 应用工程师 / Agent 开发工程师 / LLM 后端岗位，需将 70 天项目成果转化为高转化率简历与可点击验收的 GitHub 作品集。

### 核心痛点
- 简历项目描述多为'负责/参与/使用了某某框架'的流水账，缺少业务痛点与量化指标。
- 缺少 ATS 岗位核心关键词（如 Hybrid RAG / Rerank / LangGraph / MCP / vLLM / Ragas / SSE / Docker）。
- GitHub 仓库没有清晰 README、架构图与性能数据，面试官点进去 3 秒就关掉。

### 迭代目标
- 实现 STAR 法则项目经历生成器与简历体检 Linter：自动检测弱动词、缺失量化数字与 ATS 关键词覆盖率。
- 实现 GitHub 作品集 README 生成器：自动拼装项目亮点、核心技术栈、量化 Benchmark 表格与快速启动命令。

### 验收标准
- [x] 简历体检器能准确识别'流水账弱描述'并给出具体扣分与整改建议，对 STAR 量化描述评定高分。
- [x] GitHub README 生成器输出的 Markdown 包含技术徽章、架构模块清单、量化指标表与一键运行命令。
- [x] 纯 Python 离线运行，pytest 100% 通过。

### 非功能指标
- 生成的 Markdown 可直接复制到个人简历或 GitHub 仓库根目录使用。

## 3. 架构设计与交付清单

高转化率求职资产由 **结构化 STAR 简历引擎 + 可验证 GitHub 作品集** 双轮驱动：
1. **STAR 量化体检 Linter**：围绕四项硬指标自动给每一条项目经历打分：
   - **强行动动词**（主导/设计/重构/落地/优化，拒绝'负责/了解/参与'）；
   - **量化指标**（包含百分比、毫秒延迟、QPS、成本降幅或评测得分）；
   - **技术关键词密度**（命中目标 JD 高频工程词，如 RAG/Rerank/Agent/MCP/FastAPI/SSE/vLLM/Docker）；
   - **篇幅精炼度**（单条 45~140 字，信息密度最高）。
2. **GitHub 作品集 README 模板引擎**：将项目指标、模块目录、一键运行与 pytest 验收命令自动渲染为规范 Markdown，让面试官打开仓库 10 秒内就确信'这人真写过生产级代码'。

### 当日交付代码文件
- `src/day66_star_resume_builder.py`：步骤一：实现 STAR 法则项目经历生成器与简历体检 Linter
- `src/day66_portfolio_generator.py`：步骤二：实现高转化率 GitHub 作品集 README 生成器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
这个简历 Linter 非常毒辣，直接把'负责参与使用'这种流水账打成 0 分，逼着自己把工程动作和量化成果写透。

### Reviewer：林产品（Approved）
GitHub README 首屏放 Benchmark 表格太聪明了，技术负责人点开就能直接评估你的水平。

