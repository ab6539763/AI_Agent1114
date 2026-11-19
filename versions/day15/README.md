# 星辰智脑 StarMind · Day 15 迭代快照（v0.15.0）

- **课程主题**：大模型原理科普：NLP演进、Transformer注意力与Token成本核算
- **企业任务**：揭开大语言模型黑盒，为星辰智脑打造中英文混合 Token 分词估算器与财务成本预测引擎
- **GitLab 工单**：`STARMIND-015`
- **特性分支**：`feat/day15-llm-tokenizer-cost`
- **标准提交**：`feat(day15): 实现中英文Token分词估算器、注意力权重演示与大模型月度成本核算工具`

## 当日新增核心文件
- `src/day15_tokenizer.py`
- `src/day15_cost_estimator.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 15 的全部演进模块（当前累计 30 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day15/tests/test_day15.py -v
```
