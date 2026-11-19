# 星辰智脑 StarMind · Day 21 迭代快照（v0.21.0）

- **课程主题**：第3周周测与综合实战：多轮对话 + 工具调用 + 流式输出整合引擎
- **企业任务**：一周知识大阅兵！整合安全网关、多轮记忆裁剪、Function Calling 与流式推送，并通过自动化周测
- **GitLab 工单**：`STARMIND-021`
- **特性分支**：`feat/day21-weekly-exam-engine`
- **标准提交**：`feat(day21): 整合多轮对话+工具调用+流式输出综合引擎并完成第3周自动化周测评测`

## 当日新增核心文件
- `src/day21_integrated_engine.py`
- `src/day21_benchmark_runner.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 21 的全部演进模块（当前累计 42 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day21/tests/test_day21.py -v
```
