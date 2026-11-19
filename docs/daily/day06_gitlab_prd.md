# STARMIND-006 · Day 06 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 06 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 1 周：第 1 周：Python 核心语法与数据结构基石） |
| **需求标题** | 函数 —— 精通参数解包、lambda 与递归，将星辰智脑预处理脚本重构为高内聚函数式管道 |
| **GitLab 分支** | `feat/day06-functions-refactor` |
| **Commit 规范** | `feat(day06): 引入函数式管道、*args/**kwargs动态配置与递归树形目录解析` |
| **配套课件** | `courseware/day06/index.html` |
| **配套 Notebook** | `notebooks/day06/day06_practice.ipynb` |
| **迭代快照** | `versions/day06/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们攻克了嵌套字典和 JSON 序列化，已经能安全解析模拟大模型 API 返回的响应并落盘。
- **启下（明日演进）**：明天（Day 7）是第一周复习与周测日！咱们会把 Day 1~6 所有核心知识串成一张网，完成周测并独立交付「星辰企业通讯录管理系统 + JSON 持久化」。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑的文本预处理步骤越来越多（去噪、脱敏、截断、加前缀），硬编码串行调用难以按业务线灵活编排；同时知识库目录支持无限层级嵌套，需要递归统计文档清单。

### 核心痛点
- 不同业务线需要的文本处理步骤不同，复制粘贴代码导致维护成本飙升。
- 大模型调用参数繁多（temperature/top_p/stop 等），函数签名写死后极难扩展。
- 知识库文件夹树深度不固定，普通单层 for 循环无法遍历任意深度。

### 迭代目标
- 掌握位置/关键字/默认参数以及 `*args`、`**kwargs` 的透传封装模式。
- 熟练使用 `lambda` 配合 `sorted` / `filter` / `map` 完成数据排序与管道组合。
- 理解递归的终止条件与分解思路，安全遍历嵌套树形结构。

### 验收标准
- [x] 实现 `run_pipeline(text, *processors)`，支持按顺序动态组合任意数量的文本处理函数。
- [x] 实现 `build_chat_request(model, *messages, **extra_params)`，灵活组装 API 请求体。
- [x] 实现递归函数 `flatten_kb_tree(node)`，提取任意深度知识库树中的所有文档路径。

### 非功能指标
- 严禁使用可变默认参数（`items=[]`），统一采用 `None` 哨兵模式。
- 递归函数具备深度保护或清晰终止条件，防止栈溢出。

## 3. 架构设计与交付清单

今天我们在代码架构上迈出一大步，引入了两个在 LangChain / FastAPI 源码中随处可见的设计模式：
1. **可组合函数管道模式（day06_text_pipeline.py）**：利用 Python 中「函数是一等公民（First-class Citizen）」的特性，通过 `*processors` 接收任意多个单入单出的处理函数，按顺序接力执行，类似 Linux 管道 `cat | grep | sed`。
2. **递归分治树解析模式（day06_kb_tree.py）**：知识库目录节点天然是自相似结构（文件夹内可以包含文件和子文件夹）。递归函数只需处理「当前节点是文件（基准情况）」和「当前节点是文件夹（递归展开子节点）」两种情况，十行代码搞定任意层级。

### 当日交付代码文件
- `src/day06_text_pipeline.py`：步骤一：构建函数式文本管道与动态请求组装器
- `src/day06_kb_tree.py`：步骤二：使用递归与 lambda 排序遍历知识库嵌套目录树

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
多条件 lambda 排序 `(-doc['size_kb'], doc['path'])` 很老练，递归加 `max_depth` 护栏体现了安全意识。

### Reviewer：阿杰 (QA 测试)（Approved）
专门加了连续两次调用 `build_chat_request` 的隔离性测试，确认无可变默认参数污染。

