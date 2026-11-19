# 星辰智脑 StarMind · Day 25 迭代快照（v0.25.0）

- **课程主题**：LangChain入门：架构总览、ChatModel统一接口与Prompt模板工程
- **企业任务**：告别硬编码 HTTP 请求，构建星辰智脑统一模型抽象层与可复用提示词工厂
- **GitLab 工单**：`STARMIND-025`
- **特性分支**：`feat/day25-langchain-chatmodel-prompt`
- **标准提交**：`feat(day25): 实现LangChain风格ChatModel统一接口与ChatPromptTemplate模板引擎`

## 当日新增核心文件
- `src/day25_chat_model.py`
- `src/day25_prompt_template.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 25 的全部演进模块（当前累计 50 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day25/tests/test_day25.py -v
```
