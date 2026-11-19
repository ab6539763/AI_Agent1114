# 星辰智脑 StarMind · Day 31 迭代快照（v0.31.0）

- **课程主题**：周测 + RAG效果调优实验日：核心考点实战与多维消融基准报告
- **企业任务**：拒绝玄学调参！用 Hit@K、MRR 与消融实验量化 Chunk Size、Top-K 与 Embedding 效果
- **GitLab 工单**：`STARMIND-031`
- **特性分支**：`feat/day31-weekly-quiz-rag-ablation`
- **标准提交**：`feat(day31): 完成第4-5周实战周测评测引擎与RAG多维消融实验报告生成器`

## 当日新增核心文件
- `src/day31_weekly_quiz.py`
- `src/day31_rag_ablation.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 31 的全部演进模块（当前累计 62 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day31/tests/test_day31.py -v
```
