# 星辰智脑 StarMind · Day 34 迭代快照（v0.34.0）

- **课程主题**：RAG 评估体系：Faithfulness、答案相关性、上下文精确率/召回率与类 Ragas 框架
- **企业任务**：告别「肉眼拍脑袋看效果」，建立 CI 自动化 RAG 评测流水线与质量门禁
- **GitLab 工单**：`STARMIND-034`
- **特性分支**：`feat/day34-ragas-eval-framework`
- **标准提交**：`feat(day34): 实现Faithfulness/AnswerRelevancy/ContextPrecision/ContextRecall四维评测器与Ragas风格报告`

## 当日新增核心文件
- `src/day34_rag_metrics.py`
- `src/day34_ragas_runner.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 34 的全部演进模块（当前累计 68 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day34/tests/test_day34.py -v
```
