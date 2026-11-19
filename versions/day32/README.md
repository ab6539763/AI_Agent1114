# 星辰智脑 StarMind · Day 32 迭代快照（v0.32.0）

- **课程主题**：高级RAG技术(上)：Query改写、Multi-Query、HyDE与上下文压缩
- **企业任务**：专治「员工问得太口语、公司文档太书面」的检索鸿沟，大幅拉升复杂提问召回率
- **GitLab 工单**：`STARMIND-032`
- **特性分支**：`feat/day32-advanced-rag-query-transform`
- **标准提交**：`feat(day32): 实现QueryRewriter、MultiQuery、HyDE与上下文压缩器并完成召回率对比实验`

## 当日新增核心文件
- `src/day32_query_transform.py`
- `src/day32_compression_eval.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 32 的全部演进模块（当前累计 64 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day32/tests/test_day32.py -v
```
