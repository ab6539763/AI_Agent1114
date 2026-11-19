# 星辰智脑 StarMind · Day 28 迭代快照（v0.28.0）

- **课程主题**：文档加载与分割(RAG第一步)：多格式解析器与中文递归分块调优
- **企业任务**：Garbage In, Garbage Out！攻克企业多格式文档清洗与中文语义无损切分
- **GitLab 工单**：`STARMIND-028`
- **特性分支**：`feat/day28-rag-loaders-chinese-splitter`
- **标准提交**：`feat(day28): 实现多格式文档加载器与中文RecursiveCharacterTextSplitter分块实验`

## 当日新增核心文件
- `src/day28_loaders.py`
- `src/day28_text_splitter.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 28 的全部演进模块（当前累计 56 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day28/tests/test_day28.py -v
```
