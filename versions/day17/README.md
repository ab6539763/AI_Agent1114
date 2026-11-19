# 星辰智脑 StarMind · Day 17 迭代快照（v0.17.0）

- **课程主题**：Prompt 工程基础：四要素框架、少样本学习与10场景模板库评测
- **企业任务**：告别随缘玄学提问，构建星辰智脑 10 大企业场景结构化 Prompt 模板库与自动评测器
- **GitLab 工单**：`STARMIND-017`
- **特性分支**：`feat/day17-prompt-templates-eval`
- **标准提交**：`feat(day17): 实现企业10场景Prompt模板库、XML分隔符防护与Zero/Few-shot自动评测器`

## 当日新增核心文件
- `src/day17_prompt_library.py`
- `src/day17_prompt_evaluator.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 17 的全部演进模块（当前累计 34 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day17/tests/test_day17.py -v
```
