# 星辰智脑 StarMind · Day 01 迭代快照（v0.01.0）

- **课程主题**：开发环境与第一行代码
- **企业任务**：搭建星辰智脑标准开发环境，写出你的第一个企业员工数字名片 CLI
- **GitLab 工单**：`STARMIND-001`
- **特性分支**：`feat/day01-dev-env-profile`
- **标准提交**：`feat(day01): 初始化开发环境并完成星辰员工数字名片CLI工具`

## 当日新增核心文件
- `src/day01_env_check.py`
- `src/day01_profile_card.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 01 的全部演进模块（当前累计 2 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day01/tests/test_day01.py -v
```
