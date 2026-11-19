# STARMIND-017 · Day 17 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 17 / 70 |
| **所属阶段** | 第 2 阶段：第二阶段：大模型核心原理、Prompt工程与全栈 Web API（第 3 周：第3周：大模型底层原理、Prompt 工程与工具调用实战） |
| **需求标题** | Prompt 工程基础：四要素框架、少样本学习与10场景模板库评测 —— 告别随缘玄学提问，构建星辰智脑 10 大企业场景结构化 Prompt 模板库与自动评测器 |
| **GitLab 分支** | `feat/day17-prompt-templates-eval` |
| **Commit 规范** | `feat(day17): 实现企业10场景Prompt模板库、XML分隔符防护与Zero/Few-shot自动评测器` |
| **配套课件** | `courseware/day17/index.html` |
| **配套 Notebook** | `notebooks/day17/day17_practice.ipynb` |
| **迭代快照** | `versions/day17/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天（Day 16）我们把 API 采样参数和 `stream=True` 流式打字机调顺了。但今天运营、客服、法务、研发四个部门把各自写的提示词交上来，老陈一看差点晕倒：有的只有一句「帮我看看这个合同」，有的把用户输入和指令全粘在一起，还有的要求返回 JSON 却总带一堆 Markdown 废话，解析全挂！
- **启下（明日演进）**：明天（Day 18）我们将进入 Prompt 工程进阶：CoT 思维链、Self-Consistency 多路投票、ToT 思维树、提示词注入攻防以及严格 JSON Mode 意图分类器。

## 2. 业务需求说明 (PRD)

### 业务背景
杭州星辰数科各业务线正在快速接入大模型，涵盖智能客服、IT 工单、周报总结、合同审查、SQL 生成等 10 大高频场景。但当前提示词散落在个人文档里，质量参差不齐，输出格式经常漂移导致下游系统报错。

### 核心痛点
- 提示词缺少明确角色、约束与输出格式定义，模型回复冗长且不稳定。
- 直接用字符串拼接用户输入，用户文本中的标点或指令句经常干扰系统指令。
- 缺乏量化评测手段，改一版 Prompt 只能靠肉眼抽查三五条，极易「改好一条、改坏十条」。

### 迭代目标
- 建立基于「四要素（Role/Task/Context/Format）+ XML 分隔符 + Few-shot 示例」的企业级 Prompt 装配引擎。
- 内置 10 大典型企业业务场景的标准 Prompt 模板库，支持一键切换 Zero-shot / One-shot / Few-shot 模式。
- 实现自动化 Prompt 质量评测器，从 JSON 合法性、必填字段覆盖率、长度合规度三维度量化打分。

### 验收标准
- [x] 模板库完整覆盖 10 个企业场景，每个场景均包含角色设定、任务说明、JSON 输出契约及至少 2 组 Few-shot 示例。
- [x] 所有用户输入自动经过 XML 标签 `<user_input>...</user_input>` 隔离与标签转义，防止结构破坏。
- [x] 评测器能客观对比 Zero-shot 与 Few-shot 输出，Few-shot 综合得分显著高于未加约束的基线。

### 非功能指标
- 模板渲染纯内存操作，10 个场景批量渲染耗时 < 2ms。
- 模板配置结构清晰，支持后续轻松迁移至 YAML / 数据库做版本管理。

## 3. 架构设计与交付清单

把 Prompt 当成「软件工程的一等公民」来管理，需要解决三大架构问题：
1. **结构化装配（Structured Assembly）**：将散乱的长字符串拆解为 `role`（身份与专业视角）、`task`（明确动作与禁令）、`output_schema`（JSON 字段契约）、`examples`（Few-shot 输入输出对）和 `user_input`（运行时数据）。
2. **数据与指令边界隔离（Delimiter Isolation）**：使用 `<user_input>` XML 标签包裹外部输入，并在渲染前把用户输入里可能伪造的 `</user_input>` 做转义替换，避免模型分不清「哪里是系统命令，哪里是待处理文本」。
3. **评估驱动开发（Eval-Driven Prompting）**：Prompt 调优绝不能靠感觉。我们引入 `PromptEvaluator`，对候选输出自动提取 JSON、核验 `required_keys` 完整性、校验字数限制与禁词，形成可回归的自动化质量门禁。

### 当日交付代码文件
- `src/day17_prompt_library.py`：步骤一：构建星辰智脑 10 大企业场景 Prompt 模板库与安全渲染器
- `src/day17_prompt_evaluator.py`：步骤二：实现 Prompt 输出自动评测器（JSON 合法性、字段完整性与策略对比）

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
10 个企业场景覆盖非常全面，`sanitize_xml_payload` 提前堵住了分隔符逃逸漏洞，点赞。

### Reviewer：阿杰 (后端工程师)（Approved）
评测器把「纯净 JSON」和「带 Markdown 围栏 JSON」区分打分很实用，能帮我们快速挑出爱说废话的模型。

### Reviewer：林产品 (产品经理)（Approved）
合同审查和面试评估模板正好能给法务和 HR 部门先用起来！

