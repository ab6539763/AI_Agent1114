# 星辰智脑 StarMind · Day 36 迭代快照（v0.36.0）

- **课程主题**：阶段项目二(上)：企业级知识库问答系统——架构、多格式入库、混合检索与FastAPI服务
- **企业任务**：从零搭建 StarMind-KB v2.0 生产级后端：文档解析入库 + BM25/向量混合检索 + Rerank + REST API
- **GitLab 工单**：`STARMIND-036`
- **特性分支**：`feat/day36-project2-kb-backend-api`
- **标准提交**：`feat(day36): 完成项目二(上)多格式文档入库管线、混合检索+Rerank引擎与FastAPI核心接口`

## 当日新增核心文件
- `src/day36_kb_engine.py`
- `src/day36_kb_api.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 36 的全部演进模块（当前累计 72 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day36/tests/test_day36.py -v
```
