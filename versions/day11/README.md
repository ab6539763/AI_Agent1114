# 星辰智脑 StarMind · Day 11 迭代快照（v0.11.0）

- **课程主题**：文件操作与常用标准库
- **企业任务**：精通 pathlib/csv/json/datetime/re，打造星辰知识库批量文档扫描与关键词统计引擎
- **GitLab 工单**：`STARMIND-011`
- **特性分支**：`feat/day11-files-stdlib-kb-scanner`
- **标准提交**：`feat(day11): 实现基于pathlib/re/csv/datetime的批量文档读取与关键词统计导出工具`

## 当日新增核心文件
- `src/day11_regex_extractor.py`
- `src/day11_doc_scanner.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 11 的全部演进模块（当前累计 22 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day11/tests/test_day11.py -v
```
