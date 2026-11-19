# 星辰智脑 StarMind · Day 12 迭代快照（v0.12.0）

- **课程主题**：网络请求与 API 调用
- **企业任务**：吃透 HTTP 协议与 OpenAI 兼容规范，封装支持本地 Mock 降级的 DeepSeek/通义千问命令行问答工具
- **GitLab 工单**：`STARMIND-012`
- **特性分支**：`feat/day12-http-llm-api-client`
- **标准提交**：`feat(day12): 封装OpenAI兼容HTTP大模型客户端与本地Mock降级命令行问答小程序`

## 当日新增核心文件
- `src/day12_llm_http_client.py`
- `src/day12_cli_qa.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 12 的全部演进模块（当前累计 24 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day12/tests/test_day12.py -v
```
