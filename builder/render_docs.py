"""
星辰智脑 (StarMind) Markdown 辅助文档生成器。
生成：
1. 70 份每日 GitLab 需求文档 + 架构决策 + Code Review 日志 (`docs/daily/dayXX_gitlab_prd.md`)
2. 4 份企业级阶段项目交付里程碑报告 (`docs/milestones/milestone_01~04.md`)
"""

from pathlib import Path
from typing import Dict, List


def render_daily_markdown_docs(all_days: List[Dict], docs_root: Path) -> None:
    daily_dir = docs_root / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    for d in sorted(all_days, key=lambda x: x["day"]):
        day = d["day"]
        prd = d["business_prd"]
        pains = "\n".join(f"- {x}" for x in prd.get("pain_points", []))
        goals = "\n".join(f"- {x}" for x in prd.get("goals", []))
        ac = "\n".join(f"- [x] {x}" for x in prd.get("acceptance_criteria", []))
        nfr = "\n".join(f"- {x}" for x in prd.get("non_functional", []))
        reviews = "\n".join(
            f"### Reviewer：{r['reviewer']}（{r.get('status', 'Approved')}）\n{r['comment']}\n"
            for r in d["gitlab_review_log"]
        )
        files = "\n".join(f"- `{s['file_path']}`：{s['step_title']}" for s in d["code_steps"])

        content = (
            f"# {d['gitlab_ticket']} · Day {day:02d} 需求文档与 GitLab 迭代记录\n\n"
            f"| 字段 | 内容 |\n"
            f"|------|------|\n"
            f"| **迭代天数** | Day {day:02d} / 70 |\n"
            f"| **所属阶段** | 第 {d['stage']} 阶段：{d['stage_name']}（第 {d['week']} 周：{d['week_name']}） |\n"
            f"| **需求标题** | {d['title']} —— {d['subtitle']} |\n"
            f"| **GitLab 分支** | `{d['git_branch']}` |\n"
            f"| **Commit 规范** | `{d['git_commit']}` |\n"
            f"| **配套课件** | `courseware/day{day:02d}/index.html` |\n"
            f"| **配套 Notebook** | `notebooks/day{day:02d}/day{day:02d}_practice.ipynb` |\n"
            f"| **迭代快照** | `versions/day{day:02d}/` |\n\n"
            f"## 1. 上下文衔接\n\n"
            f"- **承上（昨日基线）**：{d['prev_recap']}\n"
            f"- **启下（明日演进）**：{d['next_preview']}\n\n"
            f"## 2. 业务需求说明 (PRD)\n\n"
            f"### 业务背景\n{prd.get('background', '')}\n\n"
            f"### 核心痛点\n{pains}\n\n"
            f"### 迭代目标\n{goals}\n\n"
            f"### 验收标准\n{ac}\n\n"
            f"### 非功能指标\n{nfr}\n\n"
            f"## 3. 架构设计与交付清单\n\n"
            f"{d['architecture_design']}\n\n"
            f"### 当日交付代码文件\n{files}\n\n"
            f"## 4. GitLab Merge Request Code Review 记录\n\n"
            f"{reviews}\n"
        )
        (daily_dir / f"day{day:02d}_gitlab_prd.md").write_text(content, encoding="utf-8")


def render_milestone_docs(docs_root: Path) -> None:
    ms_dir = docs_root / "milestones"
    ms_dir.mkdir(parents=True, exist_ok=True)

    milestones = [
        (
            "milestone_01_cli_assistant.md",
            """# 阶段项目一交付文档：星辰智脑命令行多轮对话 AI 助手（Day 14 里程碑）

## 1. 项目定位与业务价值
本项目是星辰智脑（StarMind）平台的 **v0.14 底座版本**，标志着零基础学员完成了从 Python 语法入门到独立封装大模型对话服务的跨越。

## 2. 核心架构与技术特性
- **面向对象抽象**：基于 `BaseModel -> OpenAIModel / QwenModel / LocalMockModel` 的统一多厂商适配架构。
- **多轮对话记忆**：维护标准 `messages`（`system` / `user` / `assistant`）上下文列表，支持 `/clear`、`/save`、`/exit` 斜杠指令。
- **工程健壮性**：集成指数退避重试装饰器、超时控制、`.env` 密钥隔离以及 UTF-8 JSON 会话持久化。

## 3. 对应代码位置与验收方式
- 版本快照：`versions/day14/`
- 交互手册：`notebooks/day14/day14_practice.ipynb`
- 验收命令：`pytest versions/day14/tests/test_day14.py -v`
""",
        ),
        (
            "milestone_02_enterprise_rag.md",
            """# 阶段项目二交付文档：星辰智脑企业级知识库问答系统（Day 36-38 里程碑）

## 1. 项目定位与业务价值
本项目是星辰智脑（StarMind）平台的 **v0.38 知识中台版本**，直击国内企业“文档分散、员工找不到制度、大模型一本正经胡说八道”三大核心痛点。

## 2. 核心技术链路
1. **文档解析与中文递归分块**：支持 Markdown/TXT/CSV/JSON 多格式加载，优先按段落、中文句号切分并保留 `chunk_overlap`。
2. **混合检索 + RRF + Rerank**：融合 BM25 精确关键词召回与语义向量召回，采用 RRF 倒数排名融合与重排序打分，显著提升 Top-K 召回质量。
3. **溯源引用与幻觉兜底**：所有答案均附带 `[文档名#片段ID]` 可验证锚点；置信度低于阈值时强制触发“知识库暂无相关依据，我不知道”安全兜底。
4. **Ragas 自动化评估**：内置忠实度、相关性、召回率评测基准，用数据驱动调优而非拍脑袋。

## 3. 对应代码位置与验收方式
- 版本快照：`versions/day36/`、`versions/day37/`、`versions/day38/`
- 生产引擎：`starmind_platform/app/rag/engine.py`
- 验收命令：`pytest versions/day37/tests/test_day37.py -v`
""",
        ),
        (
            "milestone_03_multi_agent_office.md",
            """# 阶段项目三交付文档：星辰智脑多 Agent 智能办公助手（Day 48-50 里程碑）

## 1. 项目定位与业务价值
本项目是星辰智脑（StarMind）平台的 **v0.50 智能体编排版本**，让 AI 从“只能问答的聊天框”进化为“能规划、能调工具、能人工审批、能协同交付报告的数字员工团队”。

## 2. 核心架构亮点
- **LangGraph 范式状态图引擎**：支持 State、Node、条件边、循环熔断、Checkpointer 断点持久化与 Human-in-the-loop 人工确认恢复。
- **Supervisor 多 Agent 协同**：由调度主管（Supervisor）统一协调研究检索员（Researcher）、数据分析师（Analyst）、报告撰写员（Writer）和审核员（Reviewer）。
- **企业工具箱 + MCP 协议 + Text-to-SQL**：提供日程、邮件草拟、文档 RAG、审批单、SQL 销售报表查询（严格只读防注入）及标准 JSON-RPC 2.0 MCP Server 接口。

## 3. 对应代码位置与验收方式
- 版本快照：`versions/day48/`、`versions/day49/`、`versions/day50/`
- 生产引擎：`starmind_platform/app/agent/engine.py`
- 验收命令：`pytest versions/day49/tests/test_day49.py -v`
""",
        ),
        (
            "milestone_04_enterprise_agent_platform.md",
            """# 毕业设计总交付文档：星辰智脑 StarMind v1.0.0 企业级 Agent 全栈平台（Day 58-70 里程碑）

## 1. 平台全景概览
历经 70 天持续迭代，星辰智脑（StarMind）已从 Day 1 的第一行 Python 变量脚本，演进为一套具备完整前后端、混合 RAG 知识库、多 Agent 编排、MCP 协议、Text-to-SQL、安全护栏、微调流水线与 Docker 容器化部署能力的企业级智能体平台。

## 2. 生产级目录结构
- `starmind_platform/app/main.py`：FastAPI 全栈应用入口与生命周期管理
- `starmind_platform/app/core/`：日志、异常、重试、Token 成本、安全护栏与 Trace 可观测性
- `starmind_platform/app/llm/`：DeepSeek / Qwen / OpenAI / Ollama / vLLM / LocalMock 统一适配层
- `starmind_platform/app/rag/`：混合检索 + RRF + Rerank + Ragas 评估引擎
- `starmind_platform/app/agent/`：ReAct + StateGraph + Multi-Agent + Text-to-SQL + MCP
- `starmind_platform/app/finetune/`：Alpaca/ShareGPT 数据构建与 LLaMA-Factory 微调配置流水线
- `starmind_platform/app/web/index.html`：企业级可视化 Web 控制台
- `Dockerfile` & `docker-compose.yml`：生产级多阶段容器化一键部署

## 3. 一键启动与全链路验收
```bash
# 运行企业级平台全量自动化测试
pytest starmind_platform/tests -v

# 启动企业级平台服务
uvicorn starmind_platform.app.main:app --host 0.0.0.0 --port 8000
```
""",
        ),
    ]
    for fname, body in milestones:
        (ms_dir / fname).write_text(body, encoding="utf-8")
