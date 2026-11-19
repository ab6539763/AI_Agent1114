# 星辰智脑 StarMind · Day 18 迭代快照（v0.18.0）

- **课程主题**：Prompt 工程进阶：CoT 思维链、自一致性投票与提示词注入攻防
- **企业任务**：构筑星辰智脑安全防线，打造 CoT + Self-Consistency + JSON Mode 智能客服意图分类器
- **GitLab 工单**：`STARMIND-018`
- **特性分支**：`feat/day18-cot-security-intent`
- **标准提交**：`feat(day18): 实现提示词注入攻防网关与CoT+自一致性投票JSON Mode意图分类器`

## 当日新增核心文件
- `src/day18_prompt_guard.py`
- `src/day18_intent_classifier.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 18 的全部演进模块（当前累计 36 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day18/tests/test_day18.py -v
```
