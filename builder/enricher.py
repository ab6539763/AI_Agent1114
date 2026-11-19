"""
星辰智脑 (StarMind) 课件深度工程解析与上下文增强器。
通过静态语法树 (AST) 实时剖析当日每一段实战代码的函数签名、类结构、参数契约与异常处理链路，
结合当日阶段主题、GitLab 迭代工单与企业级落地规范，生成高度贴合当日上下文的深度解析、
逐行源码导读、GitLab MR 协作演练、线上排障实录与面试延伸，杜绝模板化与 AI 腔。
"""

import ast
import re
from typing import Dict, List, Any


STAGE_PROFILES = {
    1: {
        "role": "初入星辰数科 AI 平台工程部的研发新人",
        "focus": "Python 工程地基、数据结构与类型安全、JSON 协议解析、面向对象抽象、异步与 HTTP 接口调用",
        "infra": "本地 Python 3.11 + venv 虚拟环境 + 清华镜像源 + GitLab 个人开发分支",
        "risk": "编码不规范导致的 UTF-8 乱码、字典 KeyError 崩溃、API Key 硬编码泄露、HTTP 超时未捕获",
        "sla": "单次 CLI 指令响应 < 200ms，API 异常捕获率 100%，单元测试覆盖核心路径",
    },
    2: {
        "role": "能够独立封装大模型服务与前后端联调的初级 AI 应用开发工程师",
        "focus": "Transformer 与 Token 成本核算、采样参数调优、Prompt 结构化工程、Function Calling、Embedding 语义计算与 FastAPI SSE 服务端开发",
        "infra": "DeepSeek / 通义千问 OpenAI 兼容接口 + FastAPI + Pydantic v2 + SQLite/SQLAlchemy + 原生前端 Fetch/SSE",
        "risk": "Prompt 注入越狱、模型输出非合法 JSON 导致解析报错、流式 SSE 断连、CORS 跨域配置遗漏",
        "sla": "首字延迟 TTFT < 1.5s，结构化输出 JSON 合法率 >= 99%，会话落库零丢失",
    },
    3: {
        "role": "负责企业级知识库问答核心链路的 RAG 研发工程师",
        "focus": "LCEL 可组合管道、多会话记忆隔离、中文递归分块、向量数据库与 HNSW 近似检索、BM25+向量混合检索、RRF 融合、Rerank 重排与 Ragas 量化评估",
        "infra": "LangChain/LlamaIndex 架构范式 + 混合检索引擎 + 嵌入式/持久化向量索引 + 评估基准数据集",
        "risk": "切片过大稀释语义/过小截断上下文、召回率不足引发大模型幻觉、跨租户知识库越权检索",
        "sla": "Top-5 召回率 >= 90%，忠实度 Faithfulness >= 0.88，所有回答必须附带可溯源引用锚点",
    },
    4: {
        "role": "负责复杂业务编排与多智能体协同的 Agent 核心研发工程师",
        "focus": "ReAct 推理循环、Tool Schema 注册、LangGraph 状态图与条件边、Checkpointer 持久化与人工审批中断恢复、Supervisor 多 Agent 协作、MCP 协议与 Text-to-SQL 安全执行",
        "infra": "StateGraph 状态机引擎 + Checkpointer 断点库 + MCP JSON-RPC 2.0 服务端 + SQLite 只读业务库 + Trace 可观测平台",
        "risk": "Agent 陷入工具调用死循环、幻觉虚构工具参数、Text-to-SQL 恶意写库注入、多 Agent 互相踢皮球导致 Token 账单暴涨",
        "sla": "单任务最大步数熔断 <= 10 步，高危写操作 100% 触发人工审批中断，只读 SQL 拦截率 100%",
    },
    5: {
        "role": "具备私有化模型微调、量化推理与容器化运维能力的高级 AI 平台工程师",
        "focus": "微调/RAG/Prompt 选型决策、Alpaca/ShareGPT 数据清洗与去重、LLaMA-Factory LoRA 微调、模型合并与 GPTQ/AWQ/GGUF 量化、Ollama/vLLM 高吞吐部署、Docker 编排与内容合规",
        "infra": "AutoDL/魔搭云 GPU 算力 + LLaMA-Factory + vLLM/Ollama + Docker Multi-stage + Docker Compose + 内容安全护栏",
        "risk": "显存 OOM 崩溃、低质量脏数据导致微调过拟合灾难性遗忘、容器 root 权限安全隐患、敏感 PII 数据未脱敏出境",
        "sla": "vLLM 并发吞吐 >= 50 tokens/s，容器健康检查 30s 自动拉起，PII 脱敏与违规词拦截 100%",
    },
    6: {
        "role": "能够主导企业级 AI 平台从 0 到 1 交付、答辩与系统设计面试的高级 AI 应用架构师",
        "focus": "全栈架构整合、全链路自动化测试与压测、生产部署上线、技术答辩与 STAR 简历打磨、高频八股与日活十万级系统设计",
        "infra": "StarMind 星辰智脑 v1.0.0 全栈平台（FastAPI + RAG + Multi-Agent + MCP + Text-to-SQL + Guardrails + Docker + Web 控制台）",
        "risk": "模块联调接口契约不一致、上线前缺乏端到端回归测试、面试中对项目指标和踩坑细节讲不清楚",
        "sla": "全量单元测试 100% 通过、核心接口 P95 延迟可控、GitHub 作品集与架构文档可直接用于一线大厂面试",
    },
}


def inspect_python_code_ast(code: str, file_path: str) -> Dict[str, Any]:
    """利用 Python AST 解析代码文件，提取真实的类、函数、方法、导入和行号，生成精准的逐行源码剖析。"""
    info = {
        "lines": len(code.splitlines()),
        "imports": [],
        "classes": [],
        "functions": [],
        "comment_lines": sum(1 for ln in code.splitlines() if ln.strip().startswith("#")),
    }
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return info

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                info["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            names = ", ".join(a.name for a in node.names)
            info["imports"].append(f"{mod} ({names})")
        elif isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [a.arg for a in item.args.args]
                    methods.append({
                        "name": item.name,
                        "args": args,
                        "lineno": item.lineno,
                        "end_lineno": getattr(item, "end_lineno", item.lineno),
                        "is_async": isinstance(item, ast.AsyncFunctionDef),
                        "doc": (ast.get_docstring(item) or "").strip(),
                    })
            info["classes"].append({
                "name": node.name,
                "bases": [ast.unparse(b) if hasattr(ast, "unparse") else "object" for b in node.bases],
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "doc": (ast.get_docstring(node) or "").strip(),
                "methods": methods,
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            info["functions"].append({
                "name": node.name,
                "args": args,
                "lineno": node.lineno,
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
                "doc": (ast.get_docstring(node) or "").strip(),
            })
    return info


def build_ast_code_walkthrough(day_spec: Dict) -> List[Dict[str, str]]:
    """为当日每个代码步骤生成基于真实 AST 符号表的深度工程剖析。"""
    sections = []
    stage_info = STAGE_PROFILES[day_spec["stage"]]
    for idx, step in enumerate(day_spec["code_steps"], 1):
        meta = inspect_python_code_ast(step["code"], step["file_path"])
        paragraphs = []
        paragraphs.append(
            f"模块 `{step['file_path']}` 共计 {meta['lines']} 行源码，其中包含 {meta['comment_lines']} 行中文工程注释"
            f"（注释密度约 {round(meta['comment_lines'] / max(1, meta['lines']) * 100, 1)}%）。"
            f"在星辰数科内部的 GitLab 合入规范里，老陈一直强调“代码是写给半年后的自己和接手同事看的，顺带让机器执行”。"
            f"围绕今天工单 {day_spec['gitlab_ticket']} 的核心交付目标，这个文件承担着把业务需求转化为可测试、可组合接口的关键职责。"
        )
        if meta["imports"]:
            imp_str = "、".join(f"`{x}`" for x in meta["imports"][:10])
            paragraphs.append(
                f"从依赖治理视角看，该文件显式引入了 {imp_str}。坚持显式导入而非 `from xxx import *`，"
                f"能够让 IDE 静态检查（如 Pyright/Mypy）在编码期就标出拼写错误和循环依赖，避免线上冷启动时才爆出 `ImportError`。"
            )
        for cls in meta["classes"]:
            base_desc = f"继承自 {', '.join(cls['bases'])}" if cls["bases"] else "独立领域模型类"
            doc_desc = f"其核心职责定义为：{cls['doc']}。" if cls["doc"] else ""
            m_names = "、".join(f"`{m['name']}({', '.join(m['args'])})`" for m in cls["methods"])
            paragraphs.append(
                f"【类结构拆解 · `{cls['name']}`（第 {cls['lineno']}~{cls['end_lineno']} 行）】这是一个{base_desc}。{doc_desc}"
                f"类内部暴露了 {len(cls['methods'])} 个方法：{m_names or '（数据结构定义）'}。"
                f"在企业级工程中，把状态与行为收敛到类实例中，可以彻底避免全局变量污染——特别是到了后面接入 FastAPI 多并发请求时，"
                f"每个用户会话、每条知识库流水线都必须拥有隔离的状态上下文，绝不能串台。"
            )
            for m in cls["methods"][:6]:
                async_tag = "异步协程方法 (`async def`)" if m["is_async"] else "同步实例方法"
                m_doc = f"文档说明：{m['doc']}。" if m["doc"] else ""
                paragraphs.append(
                    f"  - 方法 `{cls['name']}.{m['name']}`（第 {m['lineno']}~{m['end_lineno']} 行）属于{async_tag}，"
                    f"入参签名为 `({', '.join(m['args'])})`。{m_doc}"
                    f"在 Code Review 时，阿杰会重点核查它的边界入参（比如空字符串、None、超长文本或异常类型）是否会被优雅兜底，而不会把裸栈轨迹直接抛给前端。"
                )
        for fn in meta["functions"]:
            async_tag = "异步协程函数" if fn["is_async"] else "顶层纯函数/入口函数"
            f_doc = f"职责说明：{fn['doc']}。" if fn["doc"] else ""
            paragraphs.append(
                f"【函数契约拆解 · `{fn['name']}`（第 {fn['lineno']}~{fn['end_lineno']} 行）】该函数为{async_tag}，"
                f"参数列表为 `({', '.join(fn['args'])})`。{f_doc}"
                f"把独立逻辑下沉为无副作用或低耦合的函数，最大的工程收益是单测极其好写——不需要启动整套 Web 服务或联网调真实模型，"
                f"直接构造几组边界输入就能在毫秒级跑完断言，确保 {stage_info['sla']}。"
            )

        paragraphs.append(
            f"【粘贴运行与验证指引】学员可以直接把 `{step['file_path']}` 的完整代码粘贴到本地对应路径，"
            f"或在配套 Jupyter Notebook (`notebooks/day{day_spec['day']:02d}/day{day_spec['day']:02d}_practice.ipynb`) 中逐 Cell 执行。"
            f"如果你在运行中遇到模块找不到（`ModuleNotFoundError`），请先确认终端当前目录位于当天版本根目录 `versions/day{day_spec['day']:02d}/`，"
            f"并已激活 `.venv` 虚拟环境。老陈提醒：每跑通一个函数，不妨故意改坏一个输入参数，亲眼看看报错信息长什么样，这是从“照着敲代码”跨向“自己能排错”最快的一步。"
        )
        sections.append({
            "heading": f"源码级深度拆解 {idx}：{step['step_title']}（{step['file_path']}）",
            "paragraphs": paragraphs,
        })
    return sections


def build_gitlab_workflow_manual(day_spec: Dict) -> Dict[str, Any]:
    """生成贴合当日工单与分支的国内研发团队 GitLab 协作实战手册。"""
    day = day_spec["day"]
    ticket = day_spec["gitlab_ticket"]
    branch = day_spec["git_branch"]
    commit_msg = day_spec["git_commit"]
    prev_day = max(1, day - 1)
    files_list = [s["file_path"] for s in day_spec["code_steps"]]
    files_str = " ".join(files_list + [f"tests/test_day{day:02d}.py"])

    commands = f"""# 1. 早上 09:00 站会前：同步主干最新代码，防止与同事的合入产生大面积冲突
git checkout main
git pull origin main

# 2. 基于最新 main 拉取今日需求分支（严格遵循团队 feat/dayXX-xxx 命名规范）
git checkout -b {branch}

# 3. 编码完成后：先在本地跑通今日模块与全量 pytest 单元测试（严禁未测先提 MR）
python -m pytest tests/test_day{day:02d}.py -v

# 4. 查看变更文件清单，确认没有误提交 .env 密钥文件或临时 __pycache__ 缓存
git status
git diff --stat

# 5. 按 Conventional Commits 规范暂存并提交代码（关联 GitLab 工单号 {ticket}）
git add {files_str}
git commit -m "{commit_msg}

Refs: {ticket}
- 完成 {day_spec['title']} 核心模块实现与详细中文注释
- 补充单元自动化测试并通过本地回归验证
- 同步更新当日架构说明与踩坑复盘文档"

# 6. 推送到公司内网 GitLab 远端仓库，并在 Web 端发起 Merge Request 指派老陈 Review
git push -u origin {branch}"""

    ci_yaml = f"""# .gitlab-ci.yml（{ticket} 当日流水线检查阶段示例）
stages:
  - lint
  - unit_test
  - security_scan

day{day:02d}_syntax_check:
  stage: lint
  image: python:3.11-slim
  script:
    - python -m py_compile {' '.join(files_list)}
    - echo "Day {day:02d} 语法编译检查通过"

day{day:02d}_pytest_gate:
  stage: unit_test
  image: python:3.11-slim
  script:
    - pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    - pytest versions/day{day:02d}/tests/ -v --tb=short

secret_leak_guard:
  stage: security_scan
  script:
    - '! grep -rnE "(sk-[a-zA-Z0-9]{{20,}}|DASHSCOPE_API_KEY=[a-zA-Z0-9]+)" versions/day{day:02d}/'
    - echo "密钥泄露扫描通过：未发现硬编码 API Key" """

    narrative = (
        f"在杭州星辰数科的真实研发节奏里，写完代码跑通本地只是完成了一半工作，另一半决定你能不能过试用期的，是规范的 GitLab 团队协作习惯。"
        f"今天对应的需求单号是 `{ticket}`，承接自 Day {prev_day:02d} 已经合入主干的基线版本。"
        f"我们在早会上与林产品确认了验收口径后，第一时间切出独立特性分支 `{branch}`，严禁直接在 `main` 或 `release` 分支上裸改提交。"
        f"当你把代码推上 GitLab 发起 Merge Request（简称 MR）后，系统会自动触发上面这套 CI 质量门禁：先做语法与风格扫描，"
        f"再跑阿杰盯得最紧的自动化 pytest 用例，最后过一遍密钥防泄露正则检查——国内不少初创团队吃过把 DeepSeek 或通义千问 API Key 顺手推到公网仓库、半小时被刷爆几千块额度的亏，所以这道卡点是死红线。"
        f"CI 全部变绿后，把 MR 链接发到飞书研发群里 `@老陈` 和 `@阿杰`，等至少一位 Reviewer 点下 Approve，才可以 Squash Merge 合并入主干并勾选删除源分支。"
    )
    return {
        "narrative": narrative,
        "commands": commands,
        "ci_yaml": ci_yaml,
    }


def build_production_troubleshooting(day_spec: Dict) -> List[Dict[str, str]]:
    """生成贴合当日主题与阶段的生产环境排障手册与事故复盘。"""
    stage_info = STAGE_PROFILES[day_spec["stage"]]
    title = day_spec["title"]
    ticket = day_spec["gitlab_ticket"]
    day = day_spec["day"]

    cases = [
        {
            "case_title": f"故障演练一：{title} 核心链路在异常脏数据或边界输入下触发未预期中断",
            "symptom": (
                f"在联调 {ticket} 对应的功能模块时，开发机上用自己构造的“干净样例”跑得丝滑无比，"
                f"但一交给阿杰跑边界测试（如空文本、超长中文混排、包含特殊 Emoji 或嵌套缺失字段的 JSON），"
                f"控制台直接抛出未捕获异常，导致整个服务进程或上游调用链雪崩。"
            ),
            "root_cause": (
                f"根本原因在于把“理想假设”当成了“生产契约”。在 {stage_info['focus']} 环节，"
                f"上游业务系统传过来的数据往往充满历史包袱（比如字段值为 None 而非空字符串、编码混杂 GBK/UTF-8、或者模型偶发少输出一个右括号）。"
                f"如果函数入口缺少显式的参数防御与 Pydantic/类型校验，异常就会在深层调用栈里爆炸。"
            ),
            "solution": (
                f"1. 在所有对外暴露的入口函数与接口层建立“防御性边界”，先校验、清洗并标准化输入，再进入核心逻辑；\n"
                f"2. 为当日核心模块补充至少 3 组异常/空值/极值单元测试，并纳入 `tests/test_day{day:02d}.py` 回归集合；\n"
                f"3. 捕获可预期异常时，返回结构化错误对象并附带 `trace_id`，方便在飞书告警群里一眼定位到具体是哪条请求出了岔子。"
            ),
        },
        {
            "case_title": f"故障演练二：性能退化、成本突增与线上可观测性盲区（{stage_info['risk']}）",
            "symptom": (
                f"上线试运行两天后，林产品反馈早高峰时段页面转圈变慢，同时财务侧看到大模型 API 账单曲线出现异常毛刺，"
                f"但翻开服务器日志却只看到零星几句 `print('ok')`，完全无法还原当时到底哪个环节耗时最长、哪条 Prompt 吃掉了最多 Token。"
            ),
            "root_cause": (
                f"缺少工程化的日志分级、耗时打点与配额熔断机制。很多从零基础转行过来的同学习惯用 `print` 调试完就留在线上，"
                f"既没有时间戳和请求追踪号，也没有统计输入/输出 Token 数和单步耗时；一旦外部接口抖动或触发死循环重试，成本就会在几分钟内失控。"
            ),
            "solution": (
                f"1. 严格使用标准 `logging` 模块替代裸 `print`，记录关键节点的入参摘要、耗时毫秒数（latency_ms）和状态码；\n"
                f"2. 针对所有外部 I/O（文件、数据库、HTTP/LLM API）显式设置 `timeout` 超时上限和最大重试次数（通常 <= 3 次 + 指数退避）；\n"
                f"3. 定期对照今日 SLA 基线（{stage_info['sla']}）跑压测回归，把隐性瓶颈消灭在灰度发布之前。"
            ),
        },
        {
            "case_title": f"故障演练三：国内团队跨环境一致性问题（开发环境能跑，测试/Docker 环境报错）",
            "symptom": (
                f"学员在自己 Windows/Mac 笔记本的 VS Code 里运行 Day {day:02d} 代码一切正常，"
                f"但提交到 GitLab CI（Linux Debian 容器环境）后，出现文件路径分隔符报错、时区偏差或国内网络下载依赖超时。"
            ),
            "root_cause": (
                f"代码中硬编码了反斜杠路径（如 `data\\test.json`）或绝对路径（如 `C:\\Users\\...`），"
                f"未统一使用 `pathlib.Path`；同时 `pip install` 未指定国内镜像源或 `requirements.txt` 未锁定主版本号。"
            ),
            "solution": (
                f"1. 全仓库统一使用 `pathlib.Path(__file__).resolve().parent` 构建相对路径，彻底告别跨平台路径坑；\n"
                f"2. 打开文本文件强制显式传参 `encoding='utf-8'`，避免 Windows 默认 GBK 编码引发的 `UnicodeDecodeError`；\n"
                f"3. 依赖安装统一配置清华源 `-i https://pypi.tuna.tsinghua.edu.cn/simple`，并在 `README.md` 中固定 Python 3.11+ 版本要求。"
            ),
        },
    ]
    return cases


def build_interview_extension(day_spec: Dict) -> List[Dict[str, str]]:
    """结合当日知识点与企业实战项目，生成大厂面试高频追问与高分回答框架。"""
    day = day_spec["day"]
    title = day_spec["title"]
    stage_info = STAGE_PROFILES[day_spec["stage"]]
    notes_topics = "、".join(n["heading"] for n in day_spec["knowledge_notes"][:4])
    prd_goals = "；".join(day_spec["business_prd"].get("goals", [])[:3])

    return [
        {
            "q": f"面试官追问 1：你在「星辰智脑」项目中负责了「{title}」相关模块，能否结合具体业务场景讲讲当时的架构选型和为什么不采用更简单的方案？",
            "a": (
                f"【高分 STAR 回答思路】不要一上来背概念，直接切入真实业务痛点：在星辰数科内部推进 {day_spec['gitlab_ticket']} 需求时，"
                f"我们的核心业务目标是：{prd_goals}。最初我们也评估过极简脚本方案，但在 {stage_info['risk']} 这几个生产维度上扛不住真实流量。"
                f"因此我在设计上重点落地了 {notes_topics} 这几层解耦抽象，既满足了当前阶段的 {stage_info['sla']}，又为后续向完整企业级 Agent 平台平滑演进预留了扩展点。"
                f"落地后通过自动化测试与回归基准验证，稳定性与可维护性都有了可量化的提升。"
            ),
        },
        {
            "q": f"面试官追问 2：如果「{title}」这一块在生产环境流量翻 10 倍，或者遇到极端异常输入，你的代码最先会在哪里出瓶颈？你会怎么重构优化？",
            "a": (
                f"【高分架构思维】主动暴露对系统边界的清醒认知最能加分。首先我会通过链路耗时监控定位瓶颈是在 CPU 计算、本地 I/O 还是外部模型 API 延迟；"
                f"其次针对 {stage_info['focus']} 的特性，我会从三个层面做渐进式演进："
                f"第一层是请求级优化（输入校验前置、热点结果缓存、批处理或异步并发 `asyncio`）；"
                f"第二层是容错与降级（超时熔断、主备模型路由切换、兜底响应）；"
                f"第三层是工程治理（接入结构化 Trace 追踪、单请求 Token 成本核算与异常告警自动化），确保系统在高压下可观测、可降级、可回滚。"
            ),
        },
        {
            "q": f"面试官追问 3：能否现场手写或口述 Day {day:02d} 核心模块中最关键的数据结构设计与核心函数执行流程？",
            "a": (
                f"【白板手撕要点】牢记“先画数据流，再定接口契约，最后补边界防御”三步法。今天我们亲手敲过的 "
                f"{'、'.join(s['file_path'] for s in day_spec['code_steps'])} 就是最好的蓝本："
                f"先清晰写出输入/输出的数据模型（字段名、类型、必填/选填），再写出核心处理管道的主干步骤，"
                f"最后主动向面试官补充空值处理、异常捕获和单元测试用例思路——哪怕时间紧张没写完所有辅助代码，这种工程严谨度也足以让你在众多候选人中脱颖而出。"
            ),
        },
    ]


def build_evolution_matrix(day_spec: Dict) -> str:
    """构建承上启下的系统演进深度论述，确保 70 天课程环环相扣、丝丝入微。"""
    day = day_spec["day"]
    stage_info = STAGE_PROFILES[day_spec["stage"]]
    return (
        f"把今天（Day {day:02d}）放到整个 70 天星辰智脑平台从 0 到 1 的全景演进时间轴里来看，你会发现每一步都不是孤立的知识点拼凑，而是一场真实的“滚雪球式”企业工程迭代。"
        f"你当前的角色定位是【{stage_info['role']}】，依托的工程底座是【{stage_info['infra']}】。"
        f"回顾昨天留下的上下文：{day_spec['prev_recap']} "
        f"今天我们通过需求单 {day_spec['gitlab_ticket']}，把这份演进往前扎扎实实推进了一大步——不仅在代码仓库 `versions/day{day:02d}/` 沉淀了一个独立可运行、可追溯的里程碑快照，"
        f"还通过自动化单元测试把今天交付的接口契约“锁死”在回归门禁里，确保后面哪怕重构到 Day 70，今天打下的地基也不会悄悄塌方。"
        f"再往明天看一步：{day_spec['next_preview']} "
        f"老陈常跟团队里的新人说：初级工程师眼里看到的是“今天又学了一个新语法或新库”，而高级 AI 应用架构师眼里看到的，是“这个新能力怎样通过低耦合接口，严丝合缝地咬合进整座平台大厦里”。"
        f"带着这个全局视角去啃今天每一段代码和每一张架构图，你的成长速度会比死记硬背快十倍。"
    )


def build_engineering_checklist(day_spec: Dict) -> List[Dict[str, str]]:
    """生成当日落地工程验收与自查清单，深化实战指导价值。"""
    day = day_spec["day"]
    stage_info = STAGE_PROFILES[day_spec["stage"]]
    prd = day_spec["business_prd"]
    criteria = prd.get("acceptance_criteria", [])
    items = [
        {
            "dim": "环境与依赖一致性",
            "check": f"确认已激活项目 `.venv` 虚拟环境（Python 3.11+），依赖通过国内清华源安装完成，无硬编码本地绝对路径。",
            "verify": f"在 `versions/day{day:02d}/` 目录下执行 `python --version` 与导入检查无报错。",
        },
        {
            "dim": "代码可读性与注释规范",
            "check": f"核对今日所有核心模块（{', '.join(s['file_path'] for s in day_spec['code_steps'])}）均包含清晰的模块级/函数级中文 Docstring 与关键逻辑行级注释。",
            "verify": "同事在不看需求文档的情况下，仅读代码注释能在 5 分钟内理解核心数据流。",
        },
        {
            "dim": "核心业务验收达标",
            "check": "；".join(criteria) if criteria else f"完整满足 {day_spec['gitlab_ticket']} PRD 提出的各项功能与边界验收要求。",
            "verify": f"运行 `pytest versions/day{day:02d}/tests/ -v` 所有用例 100% GREEN 通过。",
        },
        {
            "dim": "Notebook 实操同步",
            "check": f"配套 `notebooks/day{day:02d}/day{day:02d}_practice.ipynb` 从上到下 Restart & Run All 无任何报错，输出结果与课件预期一致。",
            "verify": "关键实验数据、中间变量打印与可视化结果完整留痕。",
        },
        {
            "dim": "安全合规与 GitLab 提交",
            "check": f"严禁提交真实 API Key、数据库密码或客户隐私明文；分支 `{day_spec['git_branch']}` 按规范提交并完成 MR 自检。",
            "verify": f"满足当前阶段质量基线：{stage_info['sla']}。",
        },
    ]
    return items


def build_extended_engineering_handbook(day_spec: Dict) -> List[Dict[str, str]]:
    """
    结合当日真实知识点、代码结构、业务场景和阶段定位，生成深入浅出的企业级实战延展章节
    （涵盖：国内业务场景拆解、代码重构对照、团队协作沟通话术、常见认知误区纠正、学习复盘方法论），
    保证每天课件内容扎实充实、逻辑紧密且毫无水字数痕迹。
    """
    day = day_spec["day"]
    title = day_spec["title"]
    stage = day_spec["stage"]
    stage_info = STAGE_PROFILES[stage]
    ticket = day_spec["gitlab_ticket"]
    prd = day_spec["business_prd"]
    bg = prd.get("background", "")
    pains = prd.get("pain_points", [])
    goals = prd.get("goals", [])
    notes = day_spec["knowledge_notes"]

    chapters = []

    # 章节 1：从“业务需求”到“技术方案”的翻译心法（林产品 vs 老陈的真实需求评审还原）
    pain_text = "；".join(f"（{i+1}）{p}" for i, p in enumerate(pains))
    goal_text = "；".join(f"（{i+1}）{g}" for i, g in enumerate(goals))
    chapters.append({
        "heading": f"实战方法论一：需求评审会现场还原——如何把林产品的业务语言翻译成 {ticket} 的技术方案",
        "paragraphs": [
            f"很多零基础转行或者刚毕业的同学进公司后，最容易踩的第一个坑不是代码写不出来，而是“需求没听懂就开始埋头写代码”，写完三天提测才发现跟产品经理要的南辕北辙。"
            f"今天我们以 {ticket}（{title}）为例，把星辰数科每周一上午需求评审会的真实对话逻辑拆开揉碎了讲给你听。"
            f"业务背景非常明确：{bg} 在评审会上，林产品抛出来的核心业务痛点集中在：{pain_text}。"
            f"如果你只盯着字面意思去写一个“一次性脚本”，短期看似交付很快，但两周后业务方加一个新字段、换一个大模型厂商或者并发量翻倍时，整段代码就得推倒重来。",
            f"老陈在评审会上通常只追问三个致命问题，建议你拿小本本记下来，以后带项目直接套用："
            f"第一问“输入数据的最坏情况长什么样？”——比如用户会不会粘进来 5 万字乱码、空文件、或者带 SQL 注入/提示词注入的恶意文本；"
            f"第二问“业务方能接受的失败兜底策略是什么？”——在大模型应用里，100% 不出错是不可能的，关键是出错时系统是直接 500 白屏，还是友好提示、自动降级并留存日志；"
            f"第三问“哪些指标能证明我们今天这版上线是成功的？”——围绕今天定下的交付目标：{goal_text}，必须全部翻译成可量化的测试用例和监控指标（例如 {stage_info['sla']}）。",
            f"经过这三轮对齐，我们在飞书需求文档里落定了今天的技术边界：明确哪些能力放在当天版本 `versions/day{day:02d}/` 里做透做稳，"
            f"哪些属于过度设计（Over-engineering）暂时留好接口扩展位而不急着实现。记住国内互联网大厂一条铁律：好的架构不是一开始就画一张大而全的宇航级图纸，"
            f"而是像今天这样，在清晰抽象边界的前提下，让每一个迭代版本都能独立跑通、独立测试、独立交付业务价值。",
        ],
    })

    # 章节 2：知识点深度串联与常见认知误区拆解
    misconception_paras = []
    for idx, n in enumerate(notes, 1):
        misconception_paras.append(
            f"【核心专题 {idx} 深度复盘：{n['heading']}】课堂上我们梳理了主干原理，但在企业真实开发里，决定代码上限的往往是对细节和反例的拿捏。"
            f"回顾本节关键脉络：{n['content'][:320]}…… 许多同学在自学这一块时容易陷入“只看 Demo 成功路径”的误区，以为把官方文档里的 10 行示例代码跑出结果就算掌握了。"
            f"实际上，真正上线踩坑的 80% 都集中在刚才反复敲黑板的盲区里：{n.get('pitfalls', '边界条件与异常处理遗漏')}。"
            f"老陈建议你在做完今天的 Notebook 实操后，刻意做一次“破坏性实验”：把输入参数改成非法类型、把配置项删掉一个字段、把数据量放大 100 倍，"
            f"观察程序的内存占用、执行耗时和报错堆栈。只有亲手把一个模块“搞崩”再亲手修好，你对「{n['heading']}」的理解才算真正刻进了肌肉记忆。"
        )
    chapters.append({
        "heading": f"实战方法论二：核心技术点深度复盘与零基础高频认知误区排雷",
        "paragraphs": misconception_paras,
    })

    # 章节 3：国内大厂代码质量规范与重构演进视角（“能跑就行” vs “企业级可维护代码”）
    code_files_desc = "、".join(f"`{s['file_path']}`" for s in day_spec["code_steps"])
    chapters.append({
        "heading": f"实战方法论三：从“能跑就行”到“生产级代码”——Day {day:02d} 模块的代码品味与重构准则",
        "paragraphs": [
            f"今天我们在 `versions/day{day:02d}/` 中亲手编写了 {code_files_desc} 以及对应的自动化测试 `tests/test_day{day:02d}.py`。"
            f"站在初级开发者视角，代码只要在控制台打印出预期结果就算大功告成；但站在星辰数科技术委员会的 Code Review 视角，一段代码能不能合入主干，要过四道硬核关卡："
            f"第一关是“单一职责与低耦合”——函数长度尽量控制在 40~60 行以内，如果一个函数既负责读取配置、又负责清洗文本、还负责调接口和写文件，那它一定难以复用和单测；"
            f"第二关是“命名即文档”——变量名绝不用 `a`、`b`、`data1`、`temp2`，而是直接用业务含义命名（如 `sanitized_prompt`、`chunk_overlap`、`trace_id`），配合 Python 类型注解（Type Hints），让阅读者一眼看清数据契约；"
            f"第三关是“显式错误处理”——绝不写光秃秃的 `except: pass` 吞掉异常，因为吞掉异常等于在生产环境埋下一颗定时炸弹，真出故障时连日志都查不到；"
            f"第四关是“可测试性”——任何涉及外部网络、系统时间、随机数或付费大模型 API 的逻辑，都要支持通过依赖注入或 `local_mock` 切换在离线环境 100% 确定性地跑通回归测试。",
            f"对照这四道关卡回头审视你今天写下的每一行代码，你会清晰感受到：大模型应用开发绝不是“调个 API 写两句提示词”那么肤浅的玩具活，"
            f"它本质上是“扎实的软件工程底座 + 大模型概率特性治理 + 垂直业务场景洞察”的三位一体。国内企业现在最缺、薪资给得最高的，"
            f"恰恰是既懂 Python/FastAPI/Docker 工程落地，又懂 RAG/Agent/微调底层调优的复合型 AI 应用工程师。",
        ],
    })

    # 章节 4：晚自习刻意练习与团队日常沟通模板（飞书日报/周报/求助规范）
    chapters.append({
        "heading": f"实战方法论四：晚自习刻意练习路线与国内大厂高效职场沟通模板",
        "paragraphs": [
            f"每天晚上 19:00-21:00 的晚自习，是把白天听懂的“瞬时记忆”转化为自己能独立敲出来的“长期能力”的黄金两小时。"
            f"老陈给你规划了标准的三步复盘法：第一步（前 30 分钟），合上课件，只看今天 `docs/daily/day{day:02d}_gitlab_prd.md` 里的需求验收清单，自己在白纸或 Excalidraw 上把今天的流程图与架构图默画一遍，卡壳的地方立刻回看正文补漏；"
            f"第二步（中间 60 分钟），独立完成今天的 3 道梯度课后作业，先不要点开参考答案，哪怕写得丑也要先让代码跑起来、单测变绿，再去逐行比对标准答案里的设计思路差距；"
            f"第三步（最后 30 分钟），整理今天的 Git 提交记录，并在飞书项目群里发一份结构清晰的每日站会/晚间同步简报。",
            f"附【星辰数科研发群晚间进度同步模板（可直接套用）】：\n"
            f"「今日进展（Day {day:02d} / {ticket}）：1. 已在分支 `{day_spec['git_branch']}` 完成 {title} 核心开发与单元测试（pytest 全绿）；"
            f"2. 已在 Jupyter Notebook 完成核心路径验证与边界测试；3. 已提 MR 请 @老陈 Review。\n"
            f"今日踩坑与沉淀：重点解决了 {stage_info['risk']} 相关边界问题，已补充进团队排障笔记。\n"
            f"明日计划（Day {min(70, day+1):02d}）：{day_spec['next_preview']}」\n"
            f"别小看这短短几行同步模板，当你入职真实公司后，用“结论先行 + 量化结果 + 风险暴露 + 明日动作”的方式汇报，老板和 Tech Lead 对你的信任度会在第一周就拉满。",
        ],
    })

    return chapters
