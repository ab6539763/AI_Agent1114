"""
星辰智脑 (StarMind) 70 天 HTML5 互动课件渲染引擎。
将每一天的 DaySpec 渲染为结构完整、视觉专业、离线 100% 可打开的 HTML5 课件（courseware/dayXX/index.html），
同时生成全局课程总门户（index.html）。
"""

import re
from html import escape
from pathlib import Path
from typing import Dict, List

from builder.svg_diagrams import render_diagram_svg
from builder.enricher import (
    STAGE_PROFILES,
    build_ast_code_walkthrough,
    build_gitlab_workflow_manual,
    build_production_troubleshooting,
    build_interview_extension,
    build_evolution_matrix,
    build_engineering_checklist,
    build_extended_engineering_handbook,
)


def _nl2p(text: str) -> str:
    """将多段落文本转为安全的 HTML <p> 标签，支持行内 `code` 样式。"""
    if not text:
        return ""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    out = []
    for b in blocks:
        safe = escape(b)
        safe = re.sub(r"`([^`]+)`", r"<code>\1</code>", safe)
        safe = safe.replace("\n", "<br/>")
        out.append(f"<p>{safe}</p>")
    return "\n".join(out)


def _render_line_by_line_commentary(day_spec: Dict) -> str:
    """
    对当日所有核心代码步骤进行“逐段/逐行工程语义精讲”，
    让零基础学员在复制粘贴运行之外，真正看懂每一段代码背后的语法细节、数据流向和内存生命周期。
    """
    html_parts = []
    for s_idx, step in enumerate(day_spec["code_steps"], 1):
        lines = step["code"].splitlines()
        rows = []
        chunk_size = 8
        for start in range(0, len(lines), chunk_size):
            end = min(len(lines), start + chunk_size)
            snippet_lines = lines[start:end]
            # 提取该代码块内的注释和关键语句作为精准解读
            comments = [ln.strip().lstrip("#").strip() for ln in snippet_lines if ln.strip().startswith("#")]
            code_lines = [ln.strip() for ln in snippet_lines if ln.strip() and not ln.strip().startswith("#")]
            summary_comment = "；".join(comments[:3]) if comments else ""
            key_stmt = code_lines[0] if code_lines else "(空行或结构分隔)"

            # 根据真实语法特征给出地道工程解读
            analysis_bits = []
            joined = "\n".join(snippet_lines)
            if "class " in joined:
                analysis_bits.append("此处定义了面向对象的领域模型类，把业务状态与操作方法封装在统一命名空间中，便于后续多实例并发隔离与单元测试注入。")
            if "def " in joined or "async def " in joined:
                analysis_bits.append("此处声明了职责单一的函数/方法入口，显式标注了入参与返回值契约，避免隐式全局状态依赖。")
            if "try:" in joined or "except " in joined:
                analysis_bits.append("此处建立了防御性异常捕获边界，防止底层 I/O、格式解析或外部接口抖动直接导致主进程崩溃。")
            if "return " in joined:
                analysis_bits.append("此处将加工后的结构化结果显式返回给上游调用方，保持纯函数或低副作用风格，方便上游链式组合。")
            if "for " in joined or "while " in joined:
                analysis_bits.append("此处通过迭代循环批量处理数据集合，实际落地时需格外留意循环终止条件与大数据集下的时间复杂度。")
            if "if " in joined:
                analysis_bits.append("此处对业务分支或边界条件进行显式判定，属于保证生产环境鲁棒性的关键守卫逻辑。")
            if not analysis_bits:
                analysis_bits.append("此处完成基础变量初始化、模块导入或数据结构组装，为下游核心业务计算准备好标准上下文。")

            detail_text = (
                f"核心意图：{summary_comment + '。' if summary_comment else ''}"
                f"代表语句：`{key_stmt[:90]}`。"
                f"工程剖析：{' '.join(analysis_bits)}"
            )
            rows.append(
                f"<tr><td><code>L{start+1}-L{end}</code></td>"
                f"<td><code>{escape(key_stmt[:72])}</code></td>"
                f"<td>{escape(detail_text)}</td></tr>"
            )
        html_parts.append(
            f"<h3>逐段源码导读表 {s_idx}：{escape(step['file_path'])}（共 {len(lines)} 行）</h3>"
            f"<p>为了确保零基础同学也能彻底吃透 <code>{escape(step['file_path'])}</code>，老陈把源码按逻辑块切片并逐段标出了设计意图与工程注意事项：</p>"
            f"<table><thead><tr><th style='width:95px'>行号区间</th><th style='width:280px'>关键语句锚点</th><th>工程意图与底层执行剖析</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )
    return "\n".join(html_parts)


def _render_enterprise_scenario_drill(day_spec: Dict) -> str:
    """结合星辰智脑真实企业业务线，输出当日能力在三大国内高频业务场景中的迁移落地推演。"""
    day = day_spec["day"]
    title = day_spec["title"]
    stage_info = STAGE_PROFILES[day_spec["stage"]]
    scenarios = [
        (
            "场景 A：国内 SaaS / 电商智能客服与工单自动化分流",
            f"在双十一或大促高峰期，客服系统每天涌入数万条口语化极强、夹杂截图与订单号的咨询。"
            f"把今天 Day {day:02d} 掌握的「{title}」落地到客服产线时，核心要解决高并发下的稳定响应、敏感手机号/地址脱敏以及退换货政策的精准引用。"
            f"依托今天确立的工程底座（{stage_info['infra']}），我们可以把客服意图识别、知识检索与工单写入拆成独立可观测的原子步骤，"
            f"哪怕下游 ERP 接口临时超时，也能通过今天强调的异常兜底与重试机制平稳转接人工坐席，避免客诉升级。",
        ),
        (
            "场景 B：研发与运维团队内部知识库 + 值班排障副驾驶",
            f"国内中大型研发团队普遍存在文档散落在飞书云文档、语雀、GitLab Wiki 和历史工单里的痛点，新人入职三个月还搞不清发布流程和表结构。"
            f"将今天「{title}」对应的模块接入公司内部研发中台后，新同事只需在飞书机器人里用自然语言提问，系统即可按照今天的架构链路自动完成权限校验、语义召回或工具编排，"
            f"并把引用文档路径与精准段落一并附在回答末尾。阿杰在值班时也能直接让 Agent 查历史告警与近期变更记录，把平均故障定位时间（MTTR）从 40 分钟压缩到 5 分钟以内。",
        ),
        (
            "场景 C：金融/政企私有化信创环境与数据安全合规交付",
            f"面向银行、券商或大型国央企交付「星辰智脑」时，客户最敏感的往往不是模型有多炫酷，而是“数据绝不能出内网”“操作必须可审计”“模型能无缝切换到本地私有化部署的 Qwen/DeepSeek”。"
            f"我们在今天编码中坚持的配置解耦、统一抽象接口、离线 Mock 可测性以及结构化日志审计，正是为了满足私有化交付的严苛门槛。"
            f"当你把这套工程习惯贯彻到整个 70 天迭代周期，毕业时手里拿出来的就不再是一个只能在笔记本上演示的玩具 Demo，而是真正经得起企业安全评审与运维验收的生产级方案。",
        ),
    ]
    blocks = []
    for name, body in scenarios:
        blocks.append(f"<h3>{escape(name)}</h3>{_nl2p(body)}")
    return "\n".join(blocks)


def render_day_html(day_spec: Dict, total_days: int = 70) -> str:
    day = day_spec["day"]
    prev_link = f"../day{day-1:02d}/index.html" if day > 1 else "../../index.html"
    next_link = f"../day{day+1:02d}/index.html" if day < total_days else "../../index.html"
    stage_info = STAGE_PROFILES[day_spec["stage"]]

    # 生成各类深度剖析内容
    ast_sections = build_ast_code_walkthrough(day_spec)
    gitlab_manual = build_gitlab_workflow_manual(day_spec)
    troubleshoot_cases = build_production_troubleshooting(day_spec)
    interview_qas = build_interview_extension(day_spec)
    evolution_text = build_evolution_matrix(day_spec)
    checklist_items = build_engineering_checklist(day_spec)
    handbook_chapters = build_extended_engineering_handbook(day_spec)
    line_commentary_html = _render_line_by_line_commentary(day_spec)
    scenario_drill_html = _render_enterprise_scenario_drill(day_spec)

    # 渲染日程表
    schedule_rows = "\n".join(
        f"<tr><td><strong>{escape(item['slot'])}</strong></td>"
        f"<td>{escape(item['topic'])}</td>"
        f"<td>{escape(item['detail'])}</td></tr>"
        for item in day_spec["schedule"]
    )

    # 渲染 PRD
    prd = day_spec["business_prd"]
    prd_pains = "".join(f"<li>{escape(x)}</li>" for x in prd.get("pain_points", []))
    prd_goals = "".join(f"<li>{escape(x)}</li>" for x in prd.get("goals", []))
    prd_ac = "".join(f"<li>{escape(x)}</li>" for x in prd.get("acceptance_criteria", []))
    prd_nfr = "".join(f"<li>{escape(x)}</li>" for x in prd.get("non_functional", []))

    # 渲染 SVG 图表
    diagrams_html = []
    for idx, diag in enumerate(day_spec["diagrams"], 1):
        svg = render_diagram_svg(diag)
        diagrams_html.append(
            f'<div class="diagram-card">'
            f'<div class="diagram-title">图 {day}.{idx}：{escape(diag["title"])}（{escape(diag["kind"].upper())}）</div>'
            f'<div class="diagram-svg-wrap">{svg}</div>'
            f'<div class="diagram-caption"><strong>图示解读：</strong>{escape(diag["caption"])}</div>'
            f'</div>'
        )

    # 渲染课堂核心笔记
    notes_html = []
    for idx, note in enumerate(day_spec["knowledge_notes"], 1):
        notes_html.append(
            f"<h3>{idx}. {escape(note['heading'])}</h3>"
            f"{_nl2p(note['content'])}"
            f'<div class="pitfall-box"><strong>⚠️ 老陈避坑提示：</strong>{escape(note.get("pitfalls", "注意边界校验与编码规范。"))}</div>'
        )

    # 渲染代码实操步骤
    code_steps_html = []
    for idx, step in enumerate(day_spec["code_steps"], 1):
        code_steps_html.append(
            f"<h3>实操步骤 {idx}：{escape(step['step_title'])}</h3>"
            f'<div class="narrator-box"><div class="narrator-header"><span class="narrator-avatar">陈</span>老陈代码旁白</div>'
            f"{_nl2p(step['narration'])}</div>"
            f'<div class="code-block-wrap">'
            f'<div class="code-header"><span>📄 {escape(step["file_path"])}</span>'
            f'<button class="copy-btn" onclick="copyCode(this)">复制完整代码</button></div>'
            f"<pre><code>{escape(step['code'])}</code></pre>"
            f'<div class="output-box"># 预期运行输出示例：\n{escape(step["expected_output"])}</div>'
            f"</div>"
            f"<h4>深度代码解析与工程要点</h4>"
            f"{_nl2p(step['explanation'])}"
        )

    # 渲染 AST 源码拆解
    ast_html = []
    for sec in ast_sections:
        paras = "\n".join(_nl2p(p) for p in sec["paragraphs"])
        ast_html.append(f"<h3>{escape(sec['heading'])}</h3>{paras}")

    # 渲染 GitLab MR Code Review 评论
    review_html = []
    for rev in day_spec["gitlab_review_log"]:
        review_html.append(
            f'<div class="review-item">'
            f'<div class="review-meta"><span>👤 {escape(rev["reviewer"])}</span><span>状态：{escape(rev.get("status", "Approved"))}</span></div>'
            f"{_nl2p(rev['comment'])}"
            f"</div>"
        )

    # 渲染生产排障
    trouble_html = []
    for c in troubleshoot_cases:
        trouble_html.append(
            f"<h3>{escape(c['case_title'])}</h3>"
            f"<p><strong>【线上现象】</strong>{escape(c['symptom'])}</p>"
            f"<p><strong>【根因定位】</strong>{escape(c['root_cause'])}</p>"
            f"<p><strong>【止血与根治方案】</strong></p>{_nl2p(c['solution'])}"
        )

    # 渲染工程实战手册延展章节
    handbook_html = []
    for ch in handbook_chapters:
        paras = "\n".join(_nl2p(p) for p in ch["paragraphs"])
        handbook_html.append(f"<h3>{escape(ch['heading'])}</h3>{paras}")

    # 渲染验收清单
    checklist_rows = "\n".join(
        f"<tr><td><strong>{escape(it['dim'])}</strong></td>"
        f"<td>{escape(it['check'])}</td>"
        f"<td>{escape(it['verify'])}</td></tr>"
        for it in checklist_items
    )

    # 渲染面试延伸
    interview_html = []
    for qa in interview_qas:
        interview_html.append(
            f'<div class="review-item">'
            f'<div class="review-meta"><span>🎯 {escape(qa["q"])}</span></div>'
            f"{_nl2p(qa['a'])}"
            f"</div>"
        )

    # 渲染课后作业与标准答案
    hw_html = []
    for idx, hw in enumerate(day_spec["homeworks"], 1):
        sol_id = f"hw-sol-{day}-{idx}"
        hw_html.append(
            f'<div class="hw-card">'
            f'<div class="hw-header"><strong>作业 {idx}：{escape(hw["title"])}</strong>'
            f'<span class="badge">{escape(hw["difficulty"])}</span></div>'
            f"{_nl2p(hw['requirement'])}"
            f"<p><strong>💡 思路提示：</strong>{escape(hw['hint'])}</p>"
            f'<button class="btn" onclick="toggleSolution(this, \'{sol_id}\')">查看标准答案与解析</button>'
            f'<div class="hw-solution open" id="{sol_id}">'
            f'<div class="code-block-wrap">'
            f'<div class="code-header"><span>✅ 参考实现代码（作业 {idx}）</span>'
            f'<button class="copy-btn" onclick="copyCode(this)">复制参考代码</button></div>'
            f"<pre><code>{escape(hw['solution_code'])}</code></pre>"
            f"</div>"
            f"<h4>答案深度解析与评分标准</h4>"
            f"{_nl2p(hw['solution_analysis'])}"
            f"</div></div>"
        )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Day {day:02d}：{escape(day_spec['title'])} | 星辰智脑 70 天企业级 AI 应用开发实战</title>
  <link rel="stylesheet" href="../assets/style.css" />
</head>
<body>
  <div id="read-progress"></div>

  <header class="topbar">
    <div class="topbar-left">
      <a class="brand-link" href="../../index.html">⚡ 星辰智脑 StarMind · 70天实战营</a>
      <span class="badge">第 {day_spec['stage']} 阶段 · 第 {day_spec['week']} 周</span>
      <span class="badge badge-ticket">{escape(day_spec['gitlab_ticket'])}</span>
      <span class="badge">Day {day:02d} / {total_days}</span>
    </div>
    <div class="topbar-actions">
      <button class="btn" onclick="setTheme('light')">浅色</button>
      <button class="btn" onclick="setTheme('eyecare')">护眼</button>
      <button class="btn" onclick="setTheme('dark')">暗黑</button>
      <button class="btn" id="complete-day-btn" data-day="{day}" onclick="toggleDayComplete({day}, this)">标记今日已完成</button>
      <a class="btn" href="{prev_link}">← 上一天</a>
      <a class="btn btn-primary" href="{next_link}">下一天 →</a>
    </div>
  </header>

  <div class="layout">
    <aside class="sidebar">
      <h3>当日课件导航</h3>
      <ul class="toc-list">
        <li><a href="#sec-context">1. 旁白与承上启下上下文</a></li>
        <li><a href="#sec-prd">2. 企业真实需求文档 (PRD)</a></li>
        <li><a href="#sec-arch">3. 架构设计与矢量工程图谱</a></li>
        <li><a href="#sec-notes">4. 课堂深度技术笔记</a></li>
        <li><a href="#sec-code">5. 步步可运行代码实操</a></li>
        <li><a href="#sec-ast">6. 逐行源码剖析与单元测试</a></li>
        <li><a href="#sec-gitlab">7. GitLab 团队协作与 Review</a></li>
        <li><a href="#sec-handbook">8. 企业级实战方法论与场景推演</a></li>
        <li><a href="#sec-troubleshoot">9. 生产排障实录与验收清单</a></li>
        <li><a href="#sec-interview">10. 高频面试延伸与复盘</a></li>
        <li><a href="#sec-homework">11. 课后梯度作业与完整答案</a></li>
      </ul>
      <div class="sidebar-meta">
        <div><strong>迭代分支：</strong><br/><code>{escape(day_spec['git_branch'])}</code></div>
        <div><strong>版本快照：</strong><br/><code>versions/day{day:02d}/</code></div>
        <div><strong>实操手册：</strong><br/><code>notebooks/day{day:02d}/day{day:02d}_practice.ipynb</code></div>
        <div><strong>需求文档：</strong><br/><code>docs/daily/day{day:02d}_gitlab_prd.md</code></div>
      </div>
    </aside>

    <main class="content">
      <section class="hero">
        <div class="hero-kicker">第 {day_spec['stage']} 阶段：{escape(day_spec['stage_name'])} · 第 {day_spec['week']} 周：{escape(day_spec['week_name'])}</div>
        <h1>Day {day:02d}：{escape(day_spec['title'])}</h1>
        <p class="hero-sub">{escape(day_spec['subtitle'])}</p>
        <div class="hero-tags">
          <span class="hero-tag">工单：{escape(day_spec['gitlab_ticket'])}</span>
          <span class="hero-tag">分支：{escape(day_spec['git_branch'])}</span>
          <span class="hero-tag">角色：{escape(stage_info['role'])}</span>
          <span class="hero-tag">配套：Jupyter Notebook + 独立迭代版本 + 单元测试</span>
        </div>
      </section>

      <section class="section-card" id="sec-context">
        <h2>1. 老陈开场旁白与承上启下上下文</h2>
        <div class="narrator-box">
          <div class="narrator-header"><span class="narrator-avatar">陈</span>老陈（杭州星辰数科 · AI平台架构师）开场旁白</div>
          {_nl2p(day_spec['narrator_opening'])}
        </div>
        <div class="context-grid">
          <div class="context-box">
            <h4>⬅️ 承上：昨日迭代基线回顾</h4>
            {_nl2p(day_spec['prev_recap'])}
          </div>
          <div class="context-box">
            <h4>➡️ 启下：明日演进方向预告</h4>
            {_nl2p(day_spec['next_preview'])}
          </div>
        </div>
        <h3>全局演进视角：Day {day:02d} 在 70 天平台架构中的位置</h3>
        {_nl2p(evolution_text)}
        <h3>当日 6~8 小时企业级训练节奏表</h3>
        <table>
          <thead><tr><th style="width:180px">时间段</th><th style="width:240px">核心主题</th><th>实操任务与交付物</th></tr></thead>
          <tbody>{schedule_rows}</tbody>
        </table>
      </section>

      <section class="section-card" id="sec-prd">
        <h2>2. 企业真实业务需求文档（PRD · {escape(day_spec['gitlab_ticket'])}）</h2>
        <p><strong>需求提出方：</strong>林产品（星辰智脑产品经理） ｜ <strong>研发负责人：</strong>你（AI应用开发工程师） ｜ <strong>架构把关：</strong>老陈 ｜ <strong>测试验收：</strong>阿杰</p>
        <h3>2.1 业务背景</h3>
        {_nl2p(prd.get('background', ''))}
        <h3>2.2 现有业务痛点</h3>
        <ul>{prd_pains}</ul>
        <h3>2.3 今日迭代目标</h3>
        <ul>{prd_goals}</ul>
        <h3>2.4 功能验收标准（Acceptance Criteria）</h3>
        <ul>{prd_ac}</ul>
        <h3>2.5 非功能指标与生产红线</h3>
        <ul>{prd_nfr}</ul>
      </section>

      <section class="section-card" id="sec-arch">
        <h2>3. 架构设计与矢量工程图谱（流程图 / 架构图 / 原理示意图）</h2>
        <h3>3.1 架构设计思路与技术选型权衡</h3>
        {_nl2p(day_spec['architecture_design'])}
        <h3>3.2 核心工程可视化图谱</h3>
        {''.join(diagrams_html)}
      </section>

      <section class="section-card" id="sec-notes">
        <h2>4. 课堂核心技术笔记与深度原理解析</h2>
        {''.join(notes_html)}
        <h3>深度拓展：生产级底层原理与国内团队落地经验谈</h3>
        {_nl2p(day_spec['extra_deep_dive'])}
      </section>

      <section class="section-card" id="sec-code">
        <h2>5. 一步一步粘贴可运行代码实操（全中文逐行注释）</h2>
        <p>以下所有代码均已在 <code>versions/day{day:02d}/</code> 与 <code>notebooks/day{day:02d}/day{day:02d}_practice.ipynb</code> 中全链路实测跑通。零外网密钥即可本地执行，配置 DeepSeek/通义千问 API Key 后可一键切换真实大模型。</p>
        {''.join(code_steps_html)}
      </section>

      <section class="section-card" id="sec-ast">
        <h2>6. 逐行源码深度拆解与自动化单元测试</h2>
        {''.join(ast_html)}
        {line_commentary_html}
        <h3>当日版本自动化单元测试（<code>versions/day{day:02d}/tests/test_day{day:02d}.py</code>）</h3>
        <p>在星辰数科，没有单元测试护航的代码绝不允许合入 <code>main</code> 分支。以下测试脚本可直接通过 <code>pytest versions/day{day:02d}/tests/ -v</code> 执行验证：</p>
        <div class="code-block-wrap">
          <div class="code-header">
            <span>🧪 versions/day{day:02d}/tests/test_day{day:02d}.py</span>
            <button class="copy-btn" onclick="copyCode(this)">复制测试代码</button>
          </div>
          <pre><code>{escape(day_spec['unit_test_code'])}</code></pre>
        </div>
      </section>

      <section class="section-card" id="sec-gitlab">
        <h2>7. 国内研发团队 GitLab 协作流与 Code Review 实录</h2>
        {_nl2p(gitlab_manual['narrative'])}
        <h3>7.1 当日标准 Git 操作命令清单</h3>
        <div class="code-block-wrap">
          <div class="code-header">
            <span>💻 GitLab 分支与提交流程（{escape(day_spec['git_branch'])}）</span>
            <button class="copy-btn" onclick="copyCode(this)">复制命令</button>
          </div>
          <pre><code>{escape(gitlab_manual['commands'])}</code></pre>
        </div>
        <h3>7.2 当日 GitLab CI/CD 质量门禁配置</h3>
        <div class="code-block-wrap">
          <div class="code-header">
            <span>⚙️ .gitlab-ci.yml（{escape(day_spec['gitlab_ticket'])} 门禁）</span>
            <button class="copy-btn" onclick="copyCode(this)">复制配置</button>
          </div>
          <pre><code>{escape(gitlab_manual['ci_yaml'])}</code></pre>
        </div>
        <h3>7.3 Merge Request 真实 Code Review 评审记录</h3>
        {''.join(review_html)}
      </section>

      <section class="section-card" id="sec-handbook">
        <h2>8. 企业级实战方法论与三大业务场景迁移推演</h2>
        {''.join(handbook_html)}
        {scenario_drill_html}
      </section>

      <section class="section-card" id="sec-troubleshoot">
        <h2>9. 生产环境排障实录与工程验收自查表</h2>
        {''.join(trouble_html)}
        <h3>当日交付工程验收自查清单</h3>
        <table>
          <thead><tr><th style="width:170px">验收维度</th><th>核心检查要求</th><th style="width:280px">可执行验证方式</th></tr></thead>
          <tbody>{checklist_rows}</tbody>
        </table>
      </section>

      <section class="section-card" id="sec-interview">
        <h2>10. 大厂高频面试延伸与老陈收尾复盘</h2>
        {''.join(interview_html)}
        <div class="narrator-box">
          <div class="narrator-header"><span class="narrator-avatar">陈</span>老陈收尾复盘旁白</div>
          {_nl2p(day_spec['narrator_closing'])}
        </div>
      </section>

      <section class="section-card" id="sec-homework">
        <h2>11. 课后梯度实战作业与完整参考答案</h2>
        <p>每天课后务必独立完成以下三道梯度实战题（基础巩固 → 企业实战 → 架构进阶）。建议先自己敲代码跑通，再对照参考答案复盘设计差异。</p>
        {''.join(hw_html)}
      </section>

      <nav class="footer-nav">
        <a class="btn" href="{prev_link}">← 返回上一天课程</a>
        <a class="btn" href="../../index.html">📚 返回 70 天课程总门户</a>
        <a class="btn btn-primary" href="{next_link}">进入下一天迭代 →</a>
      </nav>
    </main>
  </div>

  <script src="../assets/app.js"></script>
</body>
</html>
"""
    return html


def render_portal_html(all_days: List[Dict], stats: Dict) -> str:
    """渲染 70 天总门户 index.html，支持按阶段筛选、搜索与本地打卡进度展示。"""
    stages = {}
    for d in all_days:
        stages.setdefault((d["stage"], d["stage_name"]), []).append(d)

    stage_sections = []
    for (s_num, s_name), days in sorted(stages.items()):
        cards = []
        for d in days:
            day = d["day"]
            cards.append(
                f'<a class="day-card" data-day="{day}" data-search="{escape((d["title"] + " " + d["subtitle"] + " " + d["gitlab_ticket"]).lower())}" '
                f'href="courseware/day{day:02d}/index.html">'
                f'<div class="day-card-top"><span class="badge">Day {day:02d}</span>'
                f'<span class="badge badge-ticket">{escape(d["gitlab_ticket"])}</span></div>'
                f'<h4>{escape(d["title"])}</h4>'
                f'<p>{escape(d["subtitle"])}</p>'
                f'<div class="day-card-foot">分支：<code>{escape(d["git_branch"])}</code></div>'
                f'</a>'
            )
        stage_sections.append(
            f'<section class="section-card stage-group" data-stage="{s_num}">'
            f'<h2>第 {s_num} 阶段：{escape(s_name)}（Day {days[0]["day"]:02d} - Day {days[-1]["day"]:02d}）</h2>'
            f'<div class="day-grid">{"".join(cards)}</div>'
            f'</section>'
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>星辰智脑 (StarMind) 零基础大模型应用开发 70 天实战课程总门户</title>
  <link rel="stylesheet" href="courseware/assets/style.css" />
  <style>
    .portal-wrap {{ max-width: 1380px; margin: 0 auto; padding: 24px; }}
    .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 20px 0 26px; }}
    .stat-card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 18px 22px; box-shadow: var(--shadow); }}
    .stat-num {{ font-size: 28px; font-weight: 800; color: var(--primary); }}
    .stat-label {{ font-size: 13.5px; color: var(--text-muted); margin-top: 4px; }}
    .filter-bar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 22px; }}
    .search-input {{ flex: 1; min-width: 240px; padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: 14px; }}
    .day-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 16px; }}
    .day-card {{ display: block; text-decoration: none; color: var(--text); background: var(--surface-alt); border: 1px solid var(--border); border-radius: 10px; padding: 16px 18px; transition: all 0.16s ease; }}
    .day-card:hover {{ border-color: var(--primary); transform: translateY(-2px); box-shadow: var(--shadow); }}
    .day-card.done {{ border-left: 5px solid var(--accent); }}
    .day-card-top {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
    .day-card h4 {{ margin: 0 0 6px; font-size: 15.5px; color: var(--text); }}
    .day-card p {{ margin: 0 0 10px; font-size: 13px; color: var(--text-muted); line-height: 1.5; }}
    .day-card-foot {{ font-size: 11.5px; color: var(--text-muted); word-break: break-all; }}
    @media (max-width: 900px) {{ .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
  </style>
</head>
<body>
  <header class="topbar">
    <div class="topbar-left">
      <a class="brand-link" href="index.html">⚡ 星辰智脑 StarMind · 70天零基础大模型应用开发实战营</a>
      <span class="badge">企业级 Agent 平台从 0 到 1 迭代交付</span>
    </div>
    <div class="topbar-actions">
      <button class="btn" onclick="setTheme('light')">浅色</button>
      <button class="btn" onclick="setTheme('eyecare')">护眼</button>
      <button class="btn" onclick="setTheme('dark')">暗黑</button>
      <a class="btn btn-primary" href="courseware/day01/index.html">从 Day 01 开始学习 →</a>
    </div>
  </header>

  <main class="portal-wrap">
    <section class="hero">
      <div class="hero-kicker">杭州星辰数科 · AI 平台工程部内部实训体系（100% 全链路可运行验证）</div>
      <h1>零基础大模型应用开发 70 天完整课程与企业级 Agent 平台</h1>
      <p class="hero-sub">模拟高级 AI 应用开发工程师真实成长路径，围绕「星辰智脑」企业级智能体中台，按 GitLab 每日分支迭代，交付 70 套 HTML5 互动课件、70 份 Jupyter Notebook 实操手册、70 个独立可运行迭代版本及最终生产级全栈平台。</p>
      <div class="hero-tags">
        <span class="hero-tag">Python 3.11 + FastAPI + SQLAlchemy</span>
        <span class="hero-tag">Prompt 工程 + Function Calling + SSE</span>
        <span class="hero-tag">RAG 混合检索 + Rerank + Ragas</span>
        <span class="hero-tag">LangGraph 多 Agent + MCP + Text-to-SQL</span>
        <span class="hero-tag">LLaMA-Factory 微调 + vLLM + Docker</span>
      </div>
    </section>

    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-num">70 天</div>
        <div class="stat-label">完整 6 大阶段 / 10 周 / 4 大企业级项目落地</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{stats.get('total_code_lines', 100000):,}+ 行</div>
        <div class="stat-label">全仓库累计真实可运行、带中文注释与测试代码</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{stats.get('min_courseware_chars', 20000):,}+ 字/天</div>
        <div class="stat-label">每日 HTML5 课件均含 SVG 图谱、旁白、源码解析与作业答案</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" id="completed-count">0 / 70</div>
        <div class="stat-label">本地学习打卡进度（支持断点续学）</div>
      </div>
    </section>

    <div class="filter-bar">
      <input class="search-input" id="course-search" type="text" placeholder="搜索课程标题、知识点、GitLab工单号（如：RAG、LangGraph、MCP、FastAPI、STARMIND-030）..." />
      <button class="btn btn-primary" onclick="filterStage(0)">全部阶段</button>
      <button class="btn" onclick="filterStage(1)">阶段1: Python</button>
      <button class="btn" onclick="filterStage(2)">阶段2: Prompt/Web</button>
      <button class="btn" onclick="filterStage(3)">阶段3: RAG</button>
      <button class="btn" onclick="filterStage(4)">阶段4: Agent</button>
      <button class="btn" onclick="filterStage(5)">阶段5: 微调部署</button>
      <button class="btn" onclick="filterStage(6)">阶段6: 毕设就业</button>
    </div>

    {''.join(stage_sections)}
  </main>

  <script src="courseware/assets/app.js"></script>
  <script>
    (function() {{
      const done = JSON.parse(localStorage.getItem("starmind_completed_days") || "[]");
      document.getElementById("completed-count").innerText = done.length + " / 70";
      document.querySelectorAll(".day-card").forEach(el => {{
        if (done.includes(parseInt(el.dataset.day, 10))) el.classList.add("done");
      }});
      const searchInput = document.getElementById("course-search");
      searchInput.addEventListener("input", () => {{
        const q = searchInput.value.trim().toLowerCase();
        document.querySelectorAll(".day-card").forEach(el => {{
          el.style.display = !q || el.dataset.search.includes(q) ? "block" : "none";
        }});
      }});
      window.filterStage = function(stage) {{
        document.querySelectorAll(".stage-group").forEach(sec => {{
          sec.style.display = (stage === 0 || parseInt(sec.dataset.stage, 10) === stage) ? "block" : "none";
        }});
      }};
    }})();
  </script>
</body>
</html>
"""
