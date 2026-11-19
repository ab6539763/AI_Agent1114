# 星辰智脑 StarMind · Day 33 迭代快照（v0.33.0）

- **课程主题**：高级RAG技术(下)：BM25混合检索、RRF融合、bge-reranker重排与父文档检索
- **企业任务**：攻克专有名词、工单号与长文上下文割裂难题，打造大厂标配两阶段精排召回引擎
- **GitLab 工单**：`STARMIND-033`
- **特性分支**：`feat/day33-hybrid-rerank-parent-doc`
- **标准提交**：`feat(day33): 实现BM25+向量RRF混合检索、交叉编码器重排序与ParentDocumentRetriever`

## 当日新增核心文件
- `src/day33_hybrid_rrf.py`
- `src/day33_rerank_parent.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 33 的全部演进模块（当前累计 66 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day33/tests/test_day33.py -v
```
