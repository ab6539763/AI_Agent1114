# 星辰智脑 StarMind · Day 20 迭代快照（v0.20.0）

- **课程主题**：多模态与嵌入模型：视觉 API 封装、Embedding 向量与余弦相似度
- **企业任务**：打通图文理解与语义检索底座，构建星辰智脑多模态客户端与 FAQ 相似问题语义匹配引擎
- **GitLab 工单**：`STARMIND-020`
- **特性分支**：`feat/day20-multimodal-embedding`
- **标准提交**：`feat(day20): 实现多模态图像理解/生成API封装与基于余弦相似度的语义匹配引擎`

## 当日新增核心文件
- `src/day20_multimodal_client.py`
- `src/day20_semantic_matcher.py`

## 历史演进底座
- `starmind_evolution/` 目录完整保留了从 Day 01 截至 Day 20 的全部演进模块（当前累计 40 个核心模块），方便随时 `diff` 追踪系统从 0 到 1 的成长路径。

## 快速运行与验收命令
```bash
# 运行当日自动化单元测试
pytest versions/day20/tests/test_day20.py -v
```
