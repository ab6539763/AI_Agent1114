# STARMIND-014 · Day 14 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 14 / 70 |
| **所属阶段** | 第 1 阶段：第一阶段：Python 编程基础（第 2 周：第 2 周：面向对象、工程化与命令行 AI 助手实战） |
| **需求标题** | 阶段考核项目一——命令行多轮对话 AI 助手 —— 综合运用 OOP、JSON 持久化、异常处理与斜杠指令系统，交付星辰智脑 CLI 多轮对话助手 v1.0 |
| **GitLab 分支** | `feat/day14-milestone1-cli-chat-assistant` |
| **Commit 规范** | `feat(day14): 交付阶段考核项目一——支持多轮记忆、JSON持久化与斜杠指令的命令行AI助手v1.0` |
| **配套课件** | `courseware/day14/index.html` |
| **配套 Notebook** | `notebooks/day14/day14_practice.ipynb` |
| **迭代快照** | `versions/day14/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天咱们拿下了装饰器、`yield` 生成器、`python-dotenv` 和 `asyncio` 异步并发，第一阶段所有的核心技术拼图已经全部集齐。
- **启下（明日演进）**：恭喜通关第一阶段（14 天 Python 工程基础）！下周一（Day 15，第二阶段：Web 后端与数据库工程）咱们将把今天这个命令行助手正式升级成企业级 **FastAPI + 数据库持久化** 的多人在线 Web 服务！

## 2. 业务需求说明 (PRD)

### 业务背景
作为星辰智脑第一阶段里程碑考核交付物，研发团队需要交付一个可独立运行、可测试、具备完整多轮对话体验的命令行 AI 助手 v1.0，作为后续 Web 版与 Agent 版的最小可行内核（MVP）。

### 核心痛点
- Day 12 的单轮问答工具没有记忆，用户追问「刚才那个流程要几天？」时模型完全不知道上下文。
- 终端一关闭，有价值的问答记录全部丢失，无法归档或下次续聊。
- 用户缺少快捷管理指令（清屏重置话题、查看 Token 消耗、导出存档），且模型异常时容易留下残缺的孤立 user 消息污染上下文。

### 迭代目标
- 实现 `ConversationMemory` 类：管理 `system` 人设、`messages` 多轮历史、滑动窗口裁剪、Token 估算与 JSON 持久化读写。
- 实现 `StarMindCLIAssistant` 类：内置斜杠指令路由（`/help`、`/history`、`/stats`、`/clear`、`/save`、`/exit`）与可替换的对话后端接口。
- 实现异常事务回滚机制：模型调用失败时不崩溃退出，并自动撤销本次未完成的 `user` 消息。

### 验收标准
- [x] 连续多轮提问时，后端能接收到完整历史 `messages`（含首条 `system` 消息），且超出窗口上限时自动保留最新 N 条对话。
- [x] `/clear` 清空对话历史但保留 `system_prompt`；`/save` 成功落盘 UTF-8 JSON 并可通过 `load_from_json` 完整还原。
- [x] 模型后端抛出异常时，助手返回友好错误提示、不崩溃，且记忆中不会残留失败的 `user` 消息。
- [x] 全部核心类与斜杠指令通过无阻塞 `pytest` 自动化验收测试。

### 非功能指标
- 零外网依赖即可运行完整多轮演示与测试，同时通过 `BaseChatBackend` 接口无缝兼容 Day 12 的真实 HTTP 大模型客户端。
- JSON 持久化文件使用 `utf-8` 编码与 `ensure_ascii=False` 缩进格式化，人类可直接阅读。

## 3. 架构设计与交付清单

阶段考核项目一严格践行「关注点分离（Separation of Concerns）」的面向对象架构，拆分为两个高内聚低耦合模块：
1. **对话记忆与持久化层（day14_session_memory.py）**：
   - `ChatMessage` 封装单条消息的角色（`user`/`assistant`）、正文与 UTC 时间戳。
   - `ConversationMemory` 负责维护多轮上下文状态，提供 `build_payload_messages()` 自动将 `system` 置顶并按 `max_history_messages` 执行滑动窗口截断；提供 `rollback_last_user_message()` 保证异常时对话状态原子一致；提供 `save_to_json()` / `load_from_json()` 实现跨进程会话恢复。
2. **命令行助手主控与后端适配层（day14_cli_assistant.py）**：
   - `BaseChatBackend` 定义极简抽象接口 `complete(messages) -> str`，既可接入内置的 `LocalSmartMockBackend`（能够真实读取历史 `messages` 演示多轮记忆），也可直接包装 Day 12 的 `StarMindHTTPClient` 接入 DeepSeek/通义千问。
   - `StarMindCLIAssistant` 将输入行统一分发至 `handle_line()`，清晰隔离斜杠指令处理与普通对话处理，`run_repl(input_lines=...)` 既支持终端真人交互也支持自动化脚本回放。

### 当日交付代码文件
- `src/day14_session_memory.py`：步骤一：实现多轮对话记忆引擎与 JSON 持久化模块
- `src/day14_cli_assistant.py`：步骤二：实现支持斜杠指令与异常回滚的命令行多轮 AI 助手 v1.0

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈 (架构师)（Approved）
第一阶段毕业考核满分通过！记忆管理、指令路由、后端抽象三层边界清晰，异常回滚和 `/save` 防路径穿越这种生产细节都考虑到了，完全具备进入第二阶段 FastAPI 后端开发的功底！

### Reviewer：林产品 (PM)（Approved）
亲测多轮记忆、`/save` 导出 JSON、`/clear` 重置话题和 `/exit` 退出全部符合 PRD 验收标准，下周咱们就给它套上 Web 页面和数据库！

