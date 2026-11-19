# STARMIND-009 · Day 09 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 09 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 面向对象编程（下） —— 精通继承、多态、魔术方法与 @property，构建星辰智脑统一模型适配层 BaseModel |
| **GitLab 分支** | `feat/day09-oop-model-adapter` |
| **Commit 规范** | `feat(day09): 实现BaseModel抽象基类、OpenAIModel/QwenModel多态适配与@property安全校验` |
| **配套课件** | `courseware/day09/index.html` |
| **配套 Notebook** | `notebooks/day09/day09_practice.ipynb` |
| **迭代快照** | `versions/day09/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们封装了 ChatMessage 与 ChatSession 领域对象，解决了裸字典无校验的痛点。
- **启下（明日演进）**：明天（Day 10）咱们把单文件脚本拆分成多文件工程包（Package），引入自定义异常体系与 venv 依赖管理。

## 2. 业务需求说明 (PRD)

### 业务背景
企业 AI 平台需同时接入多家大模型供应商以实现高可用容灾与成本优化，但各家接口细节与计费参数不同，需要统一的抽象适配层屏蔽差异。

### 核心痛点
- 业务代码里充斥大量 `if vendor == 'openai': ... elif vendor == 'qwen': ...`，每接入一个新模型就得改几十个文件。
- 外部可以直接把 `model.temperature = 999` 改爆，缺少属性写入拦截校验。
- 模型对象缺乏统一的字符串展示与便捷调用方式。

### 迭代目标
- 掌握继承、`super()`、抽象基类（`abc.ABC` / `@abstractmethod`）与多态分发。
- 熟练使用 `@property` 与 `@xxx.setter` 实现带范围校验的安全属性。
- 理解高频魔术方法 `__str__`、`__repr__`、`__len__`、`__call__` 的工程用法。

### 验收标准
- [x] 定义 `BaseModel` 抽象基类，禁止直接实例化，强制子类实现 `generate()` 方法。
- [x] 实现 `OpenAIModel` 与 `QwenModel` 两个子类，重写各自请求头构造与本地模拟生成逻辑。
- [x] 通过 `@property` 限制 `temperature` 必须在 `[0.0, 2.0]` 之间，越界抛 `ValueError`；pytest 全绿。

### 非功能指标
- 全离线本地模拟生成，零外部 API Key 依赖。
- 新增第三家厂商（如 DeepSeekModel）只需新增子类，无需修改路由器代码（开闭原则）。

## 3. 架构设计与交付清单

今天的 `BaseModel` 设计就是业界著名的**模板方法 + 策略多态模式**（LangChain 的 `BaseChatModel` 和 LlamaIndex 的 `LLM` 基类都是这个套路）：
1. **抽象基类 `BaseModel`（day09_base_model.py）**：统一保管 `model_name`、`temperature`（带 `@property` 范围校验）和调用次数统计 `_call_count`，并定义抽象方法 `generate(prompt)` 与公共魔术方法 `__call__`（让对象可以直接像函数一样 `model('你好')` 调用！）。
2. **多态子类与路由层（day09_model_providers.py）**：`OpenAIModel` 和 `QwenModel` 各自通过 `super().__init__()` 复用父类初始化，仅重写厂商专属的鉴权头格式与回复生成逻辑。上层 `ModelRouter` 只面向 `BaseModel` 编程，彻底消灭 `if/elif` 供应商判断。

### 当日交付代码文件
- `src/day09_base_model.py`：步骤一：定义星辰智脑抽象基类 BaseModel（含 @property 与魔术方法）
- `src/day09_model_providers.py`：步骤二：实现 OpenAIModel / QwenModel 多态子类与 ModelRouter

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
这套 `BaseModel -> OpenAIModel / QwenModel` + `ModelRouter` 已经非常接近生产级 LLM 网关骨架了！模板方法和只读 `call_count` 属性设计得很扎实。

### Reviewer：阿杰 (QA 测试)（Approved）
确认直接实例化 `BaseModel` 会抛 `TypeError`，温度超界会抛 `ValueError`，多态切换无副作用。

