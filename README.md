# 星辰智脑（StarMind）零基础大模型应用开发 70 天企业级实战课程与 Agent 平台

> 模拟高级 AI 应用开发工程师的真实成长路径，以「杭州星辰数科 · AI 平台工程部」真实企业业务需求驱动，严格遵循国内团队 GitLab 每日迭代协作流（Issue → 分支开发 → 单元测试 → CI 门禁 → Code Review → 合并发布），用 70 天从 0 到 1 打造并部署一套生产级企业 Agent 平台。

---

## 一、核心交付物全景

| 交付形态 | 存放路径 | 说明 |
|---|---|---|
| **70 天互动 HTML5 课件** | [`index.html`](./index.html) & `courseware/day01/index.html` ~ `day70/index.html` | 离线 100% 可打开，内置浅色/护眼/暗黑三主题、高清原生 SVG 流程图/架构图/示意图、老陈旁白、企业 PRD、逐行源码解析、GitLab MR 记录、生产排障、大厂面试延伸与课后梯度作业答案（每篇 ≥ 20,000 字） |
| **70 份 Jupyter Notebook 实操手册** | `notebooks/day01/day01_practice.ipynb` ~ `day70/day70_practice.ipynb` | 代码实操与中文深度注释一体化交付，零外网 API Key 即可逐格一键运行通过 |
| **70 天迭代版本快照** | `versions/day01/` ~ `versions/day70/` | 每天保留独立可运行的迭代快照（含 `starmind_evolution/` 历史演进代码、`tests/test_dayXX.py` 单元测试与作业参考代码），方便任意两天 `diff` 追踪系统成长轨迹 |
| **最终形态企业级 Agent 平台** | `starmind_platform/` | 生产级全栈企业智能体中台：FastAPI + SSE 流式对话 + 混合 RAG（BM25+向量+RRF+Rerank+Ragas）+ LangGraph 范式状态图（人工审批中断/恢复）+ Supervisor 多 Agent + Text-to-SQL + MCP Server/Client + 安全护栏 + 微调流水线 + Web 控制台 |
| **Markdown 辅助文档体系** | `docs/` | 含 70 份每日 GitLab PRD 文档（`docs/daily/`）、4 大企业级阶段项目交付报告（`docs/milestones/`）、10 周思维导图（`docs/weekly_mindmaps/`）、200 道高频面试题库与 STAR 简历指南（`docs/career/`） |
| **容器化与工程脚本** | `Dockerfile`、`docker-compose.yml`、`Makefile`、`scripts/verify_all.py` | 支持多阶段 Docker 镜像构建、一键编排部署与全链路自动化验收 |

---

## 二、70 天六阶段演进路线

1. **第一阶段（Day 01 - Day 14）：Python 编程基础**
   - 开发环境与清华镜像源、字符串与 f-string Prompt 模板、流程控制、列表/字典/JSON、面向对象抽象、模块包与异常、HTTP/API 调用、异步与重试装饰器。
   - **里程碑项目一（Day 14）**：命令行多轮对话 AI 助手（多厂商模型适配、上下文记忆、JSON 持久化、斜杠指令）。
2. **第二阶段（Day 15 - Day 24）：大模型原理、Prompt 工程与 FastAPI Web 基础**
   - Transformer 通俗原理与 Token 成本核算、采样参数调优、CoT/ToT/防注入、Function Calling 手写实战、Embedding 余弦相似度、HTML/CSS/JS 前端、FastAPI + SSE + SQLAlchemy。
   - **阶段成果（Day 24）**：前后端联调网页版流式对话系统（带 SQLite 会话持久化）。
3. **第三阶段（Day 25 - Day 38）：LangChain / LlamaIndex 与企业级 RAG 开发**
   - LCEL 管道与 Runnable、多会话记忆隔离、中文递归文档分块、向量数据库与 HNSW、查询改写/HyDE、BM25+向量混合检索、RRF 融合与 Rerank 重排、Ragas 自动化评估、LlamaIndex 对比。
   - **里程碑项目二（Day 36-38）**：企业级知识库问答系统（混合检索 + 重排 + 引用溯源 + “我不知道”兜底 + 答辩评审）。
4. **第四阶段（Day 39 - Day 50）：Agent 智能体与多 Agent 协作平台**
   - 手写 ReAct 范式、Tool Schema 注册、LangGraph 状态图/条件边/Checkpointer/Human-in-the-loop、Supervisor 多 Agent 研究团队、MCP（Model Context Protocol）服务端开发、Dify 低代码选型边界、链路追踪与护栏、Text-to-SQL 数据分析 Agent。
   - **里程碑项目三（Day 48-50）**：多 Agent 智能办公助手（多角色协作 + 5+ 工具 + 人工审批中断恢复）。
5. **第五阶段（Day 51 - Day 57）：模型微调、量化与容器化部署**
   - 微调/RAG/Prompt 决策树、LoRA/QLoRA 与显存估算、Alpaca/ShareGPT 数据清洗合成、LLaMA-Factory 微调与过拟合诊断、模型合并与 GPTQ/AWQ/GGUF 量化、Ollama/vLLM 高吞吐部署与压测、Docker/Compose 上线、安全脱敏与国内备案合规。
6. **第六阶段（Day 58 - Day 70）：毕业设计与大厂就业冲刺**
   - **里程碑项目四（Day 58-65）**：星辰智脑 `StarMind v1.0.0` 企业级 Agent 平台全栈整合、压测上线与答辩。
   - **就业冲刺（Day 66-70）**：STAR 简历与 GitHub 作品集、200 道高频面试八股、日活十万级系统设计、全真模拟面试与结业发布。

---

## 三、快速开始（国内环境 3 分钟跑通）

### 1. 环境准备（使用国内清华镜像源）

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 一键启动星辰智脑企业级 Agent 平台

```bash
# 默认启用内置智能本地引擎（local_mock），无需外网 API Key 即可体验全套功能
# 若需接入真实大模型，可设置环境变量：
# export STARMIND_LLM_PROVIDER=deepseek
# export DEEPSEEK_API_KEY=sk-xxxxxxxx
uvicorn starmind_platform.app.main:app --host 0.0.0.0 --port 8000
```

启动后访问：
- 企业级 Web 控制台：`http://127.0.0.1:8000/`
- Swagger 在线接口文档：`http://127.0.0.1:8000/docs`
- 健康检查接口：`http://127.0.0.1:8000/api/v1/health`

### 3. Docker 一键容器化部署

```bash
docker compose up -d --build
```

### 4. 运行全链路自动化验收测试

```bash
# 仅跑企业级平台测试
pytest starmind_platform/tests -v

# 全量校验（70天文件完整性 + 2万字校验 + 10万行代码校验 + 70天版本单测 + Notebook执行）
python scripts/verify_all.py --all
```
