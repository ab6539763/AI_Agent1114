# STARMIND-008 · Day 08 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 08 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 面向对象编程（上） —— 封装类、对象与三类方法，打造星辰智脑核心领域模型 ChatMessage 与会话管理器 |
| **GitLab 分支** | `feat/day08-oop-chat-message` |
| **Commit 规范** | `feat(day08): 使用OOP封装ChatMessage消息类与ChatSession会话记忆容器` |
| **配套课件** | `courseware/day08/index.html` |
| **配套 Notebook** | `notebooks/day08/day08_practice.ipynb` |
| **迭代快照** | `versions/day08/` |

## 1. 上下文衔接

- **承上（昨日基线）**：第一周咱们用字典和函数交付了企业通讯录系统。但随着业务变复杂，满天飞的裸字典没有强约束，少写一个字段直到运行才炸。
- **启下（明日演进）**：明天（Day 9）咱们继续深挖 OOP 进阶：继承、多态、super、魔术方法与 `@property`，亲手搭出 `BaseModel -> OpenAIModel / QwenModel` 多模型统一适配层！

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑对话引擎需要统一的消息领域对象，替代容易拼错键名的裸字典，并支持单会话多轮记忆管理、Token 统计与上下文窗口裁剪。

### 核心痛点
- 裸字典无法在创建时校验 `role` 是否属于 `system/user/assistant`。
- 每条消息的 Token 估算、时间戳记录、OpenAI 协议序列化逻辑散落在各处。
- 缺乏统一的会话容器来管理多轮消息追加、清空和超长历史裁剪。

### 迭代目标
- 理解类（Class）与实例（Instance）、`__init__` 构造方法与 `self` 绑定机制。
- 掌握实例方法、类方法（`@classmethod`）与静态方法（`@staticmethod`）的区别与应用场景。
- 完成 `ChatMessage` 与 `ChatSession` 两个核心领域类并通过单元测试。

### 验收标准
- [x] `ChatMessage` 在初始化时校验合法角色与非空内容，提供 `to_api_dict()` 与 `from_dict()` 工厂方法。
- [x] `ChatSession` 支持追加消息、保留 system prompt 的窗口裁剪、总 Token 统计及导出 OpenAI messages 列表。
- [x] 所有正常与异常用例通过 pytest。

### 非功能指标
- 类属性 `VALID_ROLES` 共享只读，实例属性互不干扰。
- 提供清晰可读的 `__repr__` 便于终端调试。

## 3. 架构设计与交付清单

在领域驱动设计（DDD）中，把「数据 + 围绕数据的行为」内聚成一个对象是消除面条代码的第一步：
1. **值对象 `ChatMessage`（day08_chat_message.py）**：封装 `role`、`content`、`created_at` 与估算 `tokens`，在 `__init__` 中立刻执行不变式校验（非法 role 直接抛 `ValueError`），并提供 `from_dict` 类方法作为统一反序列化工厂。
2. **聚合根 `ChatSession`（day08_chat_session.py）**：持有 `session_id`、可选 `system_prompt` 和 `messages: List[ChatMessage]`。当对话轮次超过 `max_history` 时，自动裁剪最早的 user/assistant 消息，同时永远保留开头的 `system` 角色设定——这是所有生产级多轮聊天机器人的标配内存管理机制。

### 当日交付代码文件
- `src/day08_chat_message.py`：步骤一：实现星辰智脑核心领域类 ChatMessage
- `src/day08_chat_session.py`：步骤二：实现多轮会话记忆容器 ChatSession

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
把 system_msg 独立保管避免滑动窗口误删，这是生产级多轮对话的标配细节！`from_dict` 用 `cls()` 很规范。

### Reviewer：阿杰 (QA 测试)（Approved）
验证了多会话实例隔离、非法角色拦截和 `/clear` 后保留人设，pytest 全绿。

