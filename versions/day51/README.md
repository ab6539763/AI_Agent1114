# 星辰智脑 StarMind · Day 51 迭代快照（v0.51.0）

- **课程主题**：模型微调理论与显存精确估算
- **企业任务**：微调 vs RAG vs Prompt 决策树、LoRA/QLoRA 数学本质与 GPU 显存计算器
- **GitLab 工单**：`STARMIND-051`
- **特性分支**：`feat/day51-finetune-theory-vram-calc`
- **标准提交**：`feat(day51): 实现微调决策引擎与GPU显存精确估算工具`

## 当日新增核心文件
- `src/day51_strategy_advisor.py`
- `src/day51_vram_calculator.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 51 的全部演进模块（当前累计 102 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day51/tests/test_day51.py -v
```
