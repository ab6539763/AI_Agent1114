# 星辰智脑 StarMind · Day 35 迭代快照（v0.35.0）

- **课程主题**：LlamaIndex 核心架构与实战：Document/Node/Index/QueryEngine 与框架选型
- **企业任务**：深入对比 LlamaIndex 与 LangChain 设计哲学，手写 LlamaIndex 风格索引引擎并量化基准评测
- **GitLab 工单**：`STARMIND-035`
- **特性分支**：`feat/day35-llamaindex-engine-benchmark`
- **标准提交**：`feat(day35): 实现LlamaIndex核心抽象(Document/TextNode/VectorStoreIndex/QueryEngine)与双框架基准对比`

## 当日新增核心文件
- `src/day35_llamaindex_core.py`
- `src/day35_framework_benchmark.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 35 的全部演进模块（当前累计 70 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day35/tests/test_day35.py -v
```
