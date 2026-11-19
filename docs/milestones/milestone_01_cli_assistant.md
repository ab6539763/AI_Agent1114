# 阶段项目一交付文档：星辰智脑命令行多轮对话 AI 助手（Day 14 里程碑）

## 1. 项目定位与业务价值
本项目是星辰智脑（StarMind）平台的 **v0.14 底座版本**，标志着零基础学员完成了从 Python 语法入门到独立封装大模型对话服务的跨越。

## 2. 核心架构与技术特性
- **面向对象抽象**：基于 `BaseModel -> OpenAIModel / QwenModel / LocalMockModel` 的统一多厂商适配架构。
- **多轮对话记忆**：维护标准 `messages`（`system` / `user` / `assistant`）上下文列表，支持 `/clear`、`/save`、`/exit` 斜杠指令。
- **工程健壮性**：集成指数退避重试装饰器、超时控制、`.env` 密钥隔离以及 UTF-8 JSON 会话持久化。

## 3. 对应代码位置与验收方式
- 版本快照：`versions/day14/`
- 交互手册：`notebooks/day14/day14_practice.ipynb`
- 验收命令：`pytest versions/day14/tests/test_day14.py -v`
