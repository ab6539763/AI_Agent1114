# 星辰智脑 StarMind · Day 29 迭代快照（v0.29.0）

- **课程主题**：向量数据库：ANN与HNSW检索原理、主流选型对比与本地持久化实现
- **企业任务**：从暴力扫描到分层导航小世界，亲手打造支持元数据过滤与磁盘持久化的类 Chroma 向量库
- **GitLab 工单**：`STARMIND-029`
- **特性分支**：`feat/day29-vector-db-hnsw-chroma`
- **标准提交**：`feat(day29): 实现中文语义Embedding、教学级HNSW索引与支持where过滤的持久化向量库`

## 当日新增核心文件
- `src/day29_embeddings_hnsw.py`
- `src/day29_vector_store.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 29 的全部演进模块（当前累计 58 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day29/tests/test_day29.py -v
```
