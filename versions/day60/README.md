# 星辰智脑 StarMind · Day 60 迭代快照（v0.60.0）

- **课程主题**：毕业设计开发 Day 2：企业级混合检索 RAG + Rerank + 引用溯源
- **企业任务**：BM25 词法 + 向量语义双路召回、RRF 倒数秩融合、精排重排与强制 [doc_id] 溯源
- **GitLab 工单**：`STARMIND-060`
- **特性分支**：`feat/day60-capstone-hybrid-rag`
- **标准提交**：`feat(day60): 实现星辰智脑混合检索RAG引擎(BM25+向量+RRF+Rerank+引用溯源)`

## 当日新增核心文件
- `src/day60_hybrid_retriever.py`
- `src/day60_rag_pipeline.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 60 的全部演进模块（当前累计 120 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day60/tests/test_day60.py -v
```
