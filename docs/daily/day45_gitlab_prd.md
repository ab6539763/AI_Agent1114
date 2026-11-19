# STARMIND-045 · Day 45 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 45 / 70 |
| **所属阶段** | 第 4 阶段：第四阶段：Agent 智能体开发与多 Agent 协同（第 6 周：Agent 基础、工具调用与 LangGraph 状态机） |
| **需求标题** | 周测 + Dify/Coze 低代码平台 —— 第六周核心能力综合验收、Dify DSL 工作流解析引擎与低代码 vs 代码开发选型矩阵 |
| **GitLab 分支** | `feat/day45-weekly-exam-dify-dsl` |
| **Commit 规范** | `feat(day45): 实现类Dify声明式DSL工作流解析引擎、低代码选型矩阵与第六周自动评测` |
| **配套课件** | `courseware/day45/index.html` |
| **配套 Notebook** | `notebooks/day45/day45_practice.ipynb` |
| **迭代快照** | `versions/day45/` |

## 1. 上下文衔接

- **承上（昨日基线）**：前六天（Day 39 ~ 44）我们从零手写了 ReAct 引擎、`@tool` + `AgentExecutor`、LangGraph `StateGraph`、SQLite Checkpointer/HITL/并行写作、多 Agent Supervisor 团队以及 MCP Server/Client 与双层记忆。
- **启下（明日演进）**：明天（Day 46）我们进入第七周，正式向生产级稳定性开火：治理 Agent 死循环与幻觉参数、搭建类 LangSmith 的 Trace/Span 全链路观测体系、Guardrails 护栏以及语义缓存降本提速。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰数科运营部门用 Dify 拖拽了一个“客户工单自动分类与初审”工作流，希望研发团队评估能否直接上线，或将其导出的 DSL 迁移到星辰智脑内部统一托管运行。同时团队需要对第六周 Agent 核心知识点进行客观验收。

### 核心痛点
- 团队内部对“用 Dify/Coze 还是用 LangGraph 代码自研”常陷入无休止争论，缺乏量化选型维度。
- 运营在低代码平台拖出来的 DSL 流程缺少本地单元测试与 CI 回归能力，改动一个条件分支极易引发线上故障。
- 第六周知识点跨度大（ReAct / LangGraph / Multi-Agent / MCP），需要通过自动化周测定位知识盲区。

### 迭代目标
- 深度解析 Dify / Coze 声明式工作流 DSL 结构（节点类型、边连接、`{{#node_id.field#}}` 变量模板与条件分支）。
- 编写纯 Python 的 `DifyDSLRunner` 引擎，支持在本地离线执行类 Dify DSL 工作流并检测环路。
- 构建量化的“低代码 vs 代码自研”技术选型打分矩阵，并完成第六周核心知识点自动评分周测器。

### 验收标准
- [x] `DifyDSLRunner` 能正确解析变量插值 `{{#start.query#}}`、根据 `if_else` 条件动态选择分支节点并输出完整节点追踪。
- [x] DSL 存在非法环路或孤立节点时，`validate_dsl()` 能够提前拦截报错。
- [x] 选型评估器能根据业务复杂度、私有化部署、定制化并发与交付周期给出客观推荐方案（Dify / Coze / LangGraph），所有单测 100% 通过。

### 非功能指标
- DSL 执行器中的 `code` 节点必须受限于白名单安全表达式或预注册函数，严禁无约束 `exec`。
- 工作流执行日志需记录每个节点的输入、输出与耗时，便于与 Dify 控制台对齐排查。

## 3. 架构设计与交付清单

国内企业落地 AI 应用时，**低代码平台（Dify / Coze / FastGPT）** 与 **代码框架（LangGraph / 自研编排）** 绝不是非此即彼的对立关系，而是处于不同的工程演进象限：

1. **Dify / Coze 的底层本质**：你在画布上拖拽的每一个节点（`start`、`knowledge_retrieval`、`if_else`、`llm`、`http_request`、`end`），保存后都会序列化为一份声明式 **DSL（YAML/JSON）**。运行时引擎维护一个全局的 **Variable Pool（变量池）**，按节点拓扑顺序执行：读取上游变量 `{{#node_id.var_name#}}` -> 执行节点逻辑 -> 把结果写回变量池 -> 根据连线或条件分支句柄（`true` / `false`）推进下一节点。
2. **低代码 vs 代码开发选型六维矩阵**：
   - **优先选 Coze（扣子）**：C 端轻应用、飞书/微信快速机器人、运营人员主导、不要求私有化内网部署、追求 1 天内上线验证；
   - **优先选 Dify（开源私有化）**：B 端企业内部知识库问答、标准工单分流、需要私有化部署与可视化 Prompt 调试、研发人力有限；
   - **必须选 LangGraph 代码自研**：强事务/资金审批类复杂有环状态机、精细 RBAC 数据行级鉴权、高并发微服务集成、需要完整 Git 版本控制与自动化 `pytest` CI/CD 回归测试。

在星辰数科，我们的最佳实践是“**Dify 做前台快速试错，LangGraph 做中台核心沉淀**”——一旦某个 Dify 工作流流量暴涨或业务逻辑变得高度复杂，研发团队就直接参照其导出的 DSL 拓扑平移为 LangGraph 代码服务。

### 当日交付代码文件
- `src/day45_dify_dsl_runner.py`：步骤一：实现类 Dify 声明式 DSL 工作流解析与离线执行引擎
- `src/day45_platform_selector.py`：步骤二：低代码 vs 代码开发选型评估器与第六周实战周测评分器

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (AI 架构师)（Approved）
用 Kahn 拓扑排序给 Dify DSL 做静态环路校验这个点子很赞！很多运营同学在低代码画布上误连回路，能在 CI 里提前拦下来太省心了。

### Reviewer：阿杰 (后端工程师)（Approved）
变量池 `var_pool` 的设计非常清爽，今天看明白 Dify DSL 的执行原理后，以后跟产品经理沟通“低代码边界”底气足多了。

### Reviewer：林产品 (产品经理)（Approved）
选型评分矩阵太实用了，我直接截进下周的产品立项评审 PPT 里，以后新需求先跑一遍矩阵再决定用 Dify 还是排研发！

