"""
《零基础大模型应用开发 70 天培训课程》第一阶段数据模块（Day 1 ~ Day 14：Python 编程基础）。
背景项目：杭州星辰数科企业级 AI 平台「星辰智脑 StarMind」（STARMIND-001 ~ STARMIND-014）。
"""

from typing import List, Dict, Any

DAYS_STAGE_1: List[Dict[str, Any]] = [
    # =========================================================================
    # DAY 1: 开发环境与第一行代码
    # =========================================================================
    {
        "day": 1,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "开发环境与第一行代码",
        "subtitle": "搭建星辰智脑标准开发环境，写出你的第一个企业员工数字名片 CLI",
        "gitlab_ticket": "STARMIND-001",
        "git_branch": "feat/day01-dev-env-profile",
        "git_commit": "feat(day01): 初始化开发环境并完成星辰员工数字名片CLI工具",
        "prev_recap": "今天是你入职杭州星辰数科的第一天！HR 刚帮你配好工牌和电脑，项目仓库还是一片空白，咱们从零开始把研发地基打牢。",
        "next_preview": "明天（Day 2）林产品会把客服工单里的脏文本丢过来，咱们用运算符、字符串切片和 f-string 给「星辰智脑」搭建第一版 Prompt 模板和文本清洗流水线。",
        "narrator_opening": (
            "欢迎加入星辰数科 AI 应用团队，叫我老陈就行。工位旁边咖啡机随便用，不过今天先别急着去调什么大模型 API。"
            "我在大厂带过几十个新人，见过太多人一上来连 Python 版本和国内镜像源都没配明白，pip 装包卡半小时报错直接心态崩了。"
            "今天咱们就干三件实在事：把 Python 3.11 + VSCode + 清华镜像源配得服服帖帖；吃透变量和四大基础数据类型；"
            "顺手接下林产品在飞书里提的第一个小需求 STARMIND-001——给新员工做一个带工号脱敏的数字名片小工具，晚上用 Git 推到仓库里，阿杰会跑单测验收。"
        ),
        "narrator_closing": (
            "第一天能把环境配顺、代码跑通、Git 提交记录写得漂漂亮亮，你已经甩开一半半途而废的自学者了。"
            "记住老陈一句话：代码里变量名别图省事写 a、b、c，今天你少敲三个字母，下周排查线上 Bug 时就得多熬两个小时。"
            "回去把三道课后题敲一遍，明天九点准时开工，咱们进军字符串和 Prompt 模板。"
        ),
        "business_prd": {
            "background": "杭州星辰数科新员工入职高峰期，飞书通讯录与内部 AI 助手「星辰智脑」需要统一的员工数字名片格式，既能展示个人基本信息与技术标签，又要避免在群聊中直接暴露完整手机号。",
            "pain_points": [
                "新人开发环境五花八门，Python 版本不统一导致依赖冲突频发。",
                "直接连海外 PyPI 源下载依赖极慢，经常超时中断。",
                "手工复制粘贴自我介绍格式混乱，手机号明文发群存在隐私合规风险。"
            ],
            "goals": [
                "统一团队开发环境：Python 3.11+、VSCode、pip 清华/阿里云国内镜像源与 Git 基础配置。",
                "掌握变量命名规范、int/float/str/bool 四大基础类型及类型转换。",
                "实现星辰员工数字名片生成模块与环境健康检查脚本，支持手机号脱敏与格式化卡片输出。"
            ],
            "acceptance_criteria": [
                "能输出当前 Python 版本、平台信息与标准镜像源配置命令。",
                "员工数字名片包含姓名、部门、工号、脱敏手机号、入职天数与 AI 权限状态。",
                "单元测试 pytest 全部通过，代码符合 PEP 8 命名规范。"
            ],
            "non_functional": [
                "零外部第三方库依赖，纯 Python 3.11 标准库运行。",
                "所有核心函数支持传参调用，不阻塞标准输入，便于 CI/CD 自动化测试。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "开发环境标准化与国内镜像加速", "detail": "安装 Python 3.11 与 VSCode，配置 pip 清华源、Git 用户名邮箱与 SSH Key，跑通 Hello StarMind。"},
            {"slot": "下午 14:00-17:30", "topic": "变量、四大基础数据类型与数字名片实战", "detail": "理解动态类型与强类型特性，编写环境诊断器与员工数字名片生成器，完成手机号脱敏逻辑。"},
            {"slot": "晚间 19:00-20:30", "topic": "Git 工作流实操与单元测试验证", "detail": "创建 feat/day01 分支，运行 pytest 验收用例，提交符合 Conventional Commits 规范的 Commit。"},
            {"slot": "复盘 20:30-21:00", "topic": "老陈 Code Review 与错题整理", "detail": "梳理类型转换常见报错（TypeError/ValueError），完成 3 道课后梯度题。"}
        ],
        "architecture_design": (
            "在企业级研发中，Day 1 的核心架构思维叫做「环境一致性与数据边界清晰」。"
            "很多初学者把业务脚本写成一坨全局 print 语句，既没法复用，也没法写自动化测试。"
            "在 STARMIND-001 中，我们采用「两层解耦设计」：\n"
            "1. 环境诊断层（day01_env_check.py）：负责采集运行时 Python 版本、操作系统和推荐镜像源，确保开发机满足团队基线（Python >= 3.10）。\n"
            "2. 业务名片层（day01_profile_card.py）：将「输入数据校验与类型标准化」「敏感信息脱敏」「名片文本渲染」拆分成纯函数。"
            "这样即使未来林产品要求把命令行名片改成网页端卡片或飞书机器人推送，我们只需要替换最外层的渲染函数，核心的校验与脱敏逻辑一行都不用动。"
        ),
        "diagrams": [
            {
                "title": "员工数字名片生成业务流程图",
                "kind": "flowchart",
                "caption": "展示从采集员工基础信息、类型校验、手机号脱敏到渲染标准数字名片的完整执行链路。",
                "nodes": [
                    {"id": "n1", "label": "录入员工信息", "sub": "姓名/工号/手机/工龄", "color": "#3b82f6"},
                    {"id": "n2", "label": "数据类型校验", "sub": "str/int/float/bool转换", "color": "#8b5cf6"},
                    {"id": "n3", "label": "手机号脱敏", "sub": "138****8888", "color": "#f59e0b"},
                    {"id": "n4", "label": "计算AI配额", "sub": "按职级分配初始Token", "color": "#10b981"},
                    {"id": "n5", "label": "渲染数字名片", "sub": "生成标准边框卡片", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "原始字段"},
                    {"from": "n2", "to": "n3", "label": "合法数据"},
                    {"from": "n3", "to": "n4", "label": "脱敏完成"},
                    {"from": "n4", "to": "n5", "label": "拼装展示"}
                ]
            },
            {
                "title": "星辰数科本地研发环境架构图",
                "kind": "architecture",
                "caption": "展示 VSCode、Python 解释器、国内 PyPI 镜像源与 Git 远程仓库之间的协作关系。",
                "nodes": [
                    {"id": "a1", "label": "VSCode IDE", "sub": "代码编辑/调试/终端", "color": "#3b82f6"},
                    {"id": "a2", "label": "Python 3.11", "sub": "本地解释器运行时", "color": "#10b981"},
                    {"id": "a3", "label": "国内镜像源", "sub": "清华/阿里云 PyPI", "color": "#f59e0b"},
                    {"id": "a4", "label": "本地 Git 仓库", "sub": "feat/day01 分支", "color": "#8b5cf6"},
                    {"id": "a5", "label": "GitLab/GitHub", "sub": "团队远程代码托管", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "调用运行"},
                    {"from": "a2", "to": "a3", "label": "pip 高速拉包"},
                    {"from": "a1", "to": "a4", "label": "git commit"},
                    {"from": "a4", "to": "a5", "label": "git push / MR"}
                ]
            },
            {
                "title": "Python 变量引用与内存对象原理图",
                "kind": "schematic",
                "caption": "直观理解 Python 中「变量是贴在内存对象上的标签」，而非传统 C 语言的固定内存盒子。",
                "nodes": [
                    {"id": "s1", "label": "变量名 user_name", "sub": "栈帧中的名称标签", "color": "#3b82f6"},
                    {"id": "s2", "label": "str 对象", "sub": "值: '林小星' (不可变)", "color": "#10b981"},
                    {"id": "s3", "label": "变量名 token_quota", "sub": "栈帧中的名称标签", "color": "#3b82f6"},
                    {"id": "s4", "label": "int 对象", "sub": "值: 50000 (不可变)", "color": "#8b5cf6"},
                    {"id": "s5", "label": "变量名 is_active", "sub": "栈帧中的名称标签", "color": "#3b82f6"},
                    {"id": "s6", "label": "bool 对象", "sub": "值: True (单例对象)", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "指向 id()"},
                    {"from": "s3", "to": "s4", "label": "指向 id()"},
                    {"from": "s5", "to": "s6", "label": "指向 id()"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 国内开发环境加速：pip 镜像源与 Git 规范",
                "content": (
                    "国内开发安装 Python 第三方库，务必第一时间配置国内镜像源，常用清华源：`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple`。"
                    "同时配置 Git 身份信息（`git config --global user.name` 与 `user.email`），每次提交遵循 `feat(day01): 描述` 的格式，方便团队回溯每次迭代。"
                ),
                "pitfalls": "常见坑：Windows 安装 Python 时忘了勾选「Add Python to PATH」，导致终端输入 python 提示找不到命令；或者系统自带 Python2 与 Python3 混用，建议统一明确使用 python3 / pip3。"
            },
            {
                "heading": "2. 变量命名与四大核心数据类型",
                "content": (
                    "Python 采用蛇形命名法（snake_case），例如 `employee_id`、`monthly_budget`；常量用全大写如 `DEFAULT_QUOTA = 50000`。"
                    "四大核心基础类型：`int`（整数，支持任意精度）、`float`（浮点数，注意精度误差）、`str`（Unicode 字符串，支持中文）、`bool`（True/False，本质是 int 的子类）。"
                    "可用 `type(x)` 查看类型，用 `isinstance(x, int)` 做安全类型判断。"
                ),
                "pitfalls": "常见坑：Python 是动态强类型语言，`'工号:' + 1001` 会直接抛出 `TypeError`！必须显式转成 `str(1001)` 或直接用 f-string：`f'工号:{1001}'`。此外 `bool('False')` 结果是 `True`，因为非空字符串转布尔永远为真！"
            },
            {
                "heading": "3. Git 四步日常提交法",
                "content": (
                    "每天在星辰数科写完代码，标准四步：`git checkout -b feat/dayXX-xxx` 切新分支 -> `git status` 检查改动 -> `git add .` 暂存 -> `git commit -m 'feat(dayXX): ...'` 提交 -> `git push -u origin 分支名` 发起合并请求。"
                ),
                "pitfalls": "千万不要把 `.venv/` 虚拟环境目录、`.env` 密钥文件或 `__pycache__/` 提交到 Git 仓库！一定要先配置好 `.gitignore`。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：编写星辰智脑开发环境自检脚本",
                "file_path": "src/day01_env_check.py",
                "narration": "先别急着写业务，大厂规范是先跑环境健康检查。咱们写一个小工具，自动检测当前 Python 版本是否满足 3.10+ 要求，并打印清华镜像源配置指令。",
                "code": r'''"""
STARMIND-001 模块一：开发环境健康自检工具。
检查 Python 运行时版本、操作系统信息，并输出推荐的国内 pip 镜像配置命令。
"""

import platform
import sys
from typing import Dict, Any

# 定义星辰智脑项目要求的最低 Python 主次版本
MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 10
TSINGHUA_PYPI_MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"


def check_environment() -> Dict[str, Any]:
    """收集当前开发环境信息并判断是否满足项目基线要求。"""
    # 获取当前 Python 解释器的主版本、次版本、微版本号
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    # 判断是否达到 Python 3.10 及以上版本
    is_compatible = (version_info.major, version_info.minor) >= (
        MIN_PYTHON_MAJOR,
        MIN_PYTHON_MINOR,
    )

    # 组装结构化的诊断结果字典
    report: Dict[str, Any] = {
        "python_version": version_str,
        "os_name": platform.system(),
        "os_release": platform.release(),
        "is_compatible": is_compatible,
        "recommended_mirror": TSINGHUA_PYPI_MIRROR,
        "pip_config_cmd": f"pip config set global.index-url {TSINGHUA_PYPI_MIRROR}",
    }
    return report


def format_env_report(report: Dict[str, Any]) -> str:
    """将环境诊断结果格式化为易读的终端输出文本。"""
    status_badge = "[PASS] 满足星辰智脑运行要求" if report["is_compatible"] else "[WARN] 请升级至 Python 3.10+"
    lines = [
        "=== 星辰智脑 StarMind 开发环境自检报告 ===",
        f"Python 版本 : {report['python_version']}  {status_badge}",
        f"操作系统    : {report['os_name']} ({report['os_release']})",
        f"推荐镜像源  : {report['recommended_mirror']}",
        f"一键配置命令: {report['pip_config_cmd']}",
        "============================================",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    # 执行环境自检并打印报告
    env_report = check_environment()
    print(format_env_report(env_report))
''',
                "explanation": (
                    "1. 使用标准库 `sys.version_info` 而不是用字符串去比较版本号（因为字符串比较 `'3.9' > '3.11'` 会出错，元组比较 `(3, 11) >= (3, 10)` 才准确）。\n"
                    "2. 把「数据采集 `check_environment()`」与「文本展示 `format_env_report()`」分开写，这样单元测试可以直接断言 `report['is_compatible'] is True`。"
                ),
                "expected_output": (
                    "=== 星辰智脑 StarMind 开发环境自检报告 ===\n"
                    "Python 版本 : 3.11.x  [PASS] 满足星辰智脑运行要求\n"
                    "操作系统    : Linux (...)\n"
                    "推荐镜像源  : https://pypi.tuna.tsinghua.edu.cn/simple\n"
                    "一键配置命令: pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple\n"
                    "============================================"
                )
            },
            {
                "step_title": "步骤二：实现星辰员工数字名片生成器（含手机号脱敏与配额计算）",
                "file_path": "src/day01_profile_card.py",
                "narration": "环境没问题了，咱们直接搞定林产品的 STARMIND-001 需求。注意手机号必须做中间四位脱敏，AI Token 初始配额根据工龄动态计算。",
                "code": r'''"""
STARMIND-001 模块二：星辰数科新员工数字名片生成器。
演示变量定义、四大基础类型（str/int/float/bool）、类型转换与安全脱敏输出。
"""

# 常量定义：使用全大写蛇形命名法
COMPANY_NAME = "杭州星辰数科"
PLATFORM_NAME = "星辰智脑 StarMind"
BASE_DAILY_TOKEN_QUOTA = 50000  # 每位新员工基础每日 Token 配额


def mask_phone(phone: str) -> str:
    """对 11 位中国大陆手机号进行中间四位脱敏处理。"""
    # 去除首尾可能存在的空格
    cleaned = str(phone).strip()
    # 校验长度是否为 11 位且全为数字
    if len(cleaned) == 11 and cleaned.isdigit():
        # 保留前 3 位和后 4 位，中间替换为 ****
        return f"{cleaned[:3]}****{cleaned[-4:]}"
    # 非标准手机号则返回统一占位，避免明文泄露
    return "格式异常(已隐藏)"


def calculate_token_quota(years_of_exp: float, is_ai_team: bool) -> int:
    """根据工作年限与是否属于 AI 研发团队计算每日 Token 配额。"""
    # 每增加 1 年经验额外增加 10000 Token 配额，先按浮点计算再转为整数
    exp_bonus = int(max(0.0, years_of_exp) * 10000)
    # AI 核心研发团队享有 1.5 倍配额加成
    multiplier = 1.5 if is_ai_team else 1.0
    total_quota = int((BASE_DAILY_TOKEN_QUOTA + exp_bonus) * multiplier)
    return total_quota


def build_profile_card(
    name: str,
    employee_id: int,
    department: str,
    phone: str,
    years_of_exp: float,
    is_ai_team: bool = True,
) -> str:
    """构建标准格式的员工数字名片字符串。"""
    # 格式化 4 位补零工号，例如 7 -> "XM-0007"
    formatted_id = f"XM-{int(employee_id):04d}"
    # 执行手机号脱敏
    safe_phone = mask_phone(phone)
    # 计算每日 Token 配额
    quota = calculate_token_quota(years_of_exp, is_ai_team)
    # 将布尔值转换为中文权限描述
    ai_status = "已开通 (核心研发权限)" if is_ai_team else "已开通 (标准办公权限)"

    # 拼装多行名片文本，利用 f-string 格式化千分位逗号与保留 1 位小数
    card = (
        f"+------------------------------------------+\n"
        f"|  {COMPANY_NAME} · {PLATFORM_NAME} 数字名片  |\n"
        f"+------------------------------------------+\n"
        f"  姓名     : {name}\n"
        f"  工号     : {formatted_id}\n"
        f"  部门     : {department}\n"
        f"  联系电话 : {safe_phone}\n"
        f"  工作年限 : {years_of_exp:.1f} 年\n"
        f"  AI 权限  : {ai_status}\n"
        f"  每日配额 : {quota:,} Tokens\n"
        f"+------------------------------------------+"
    )
    return card


if __name__ == "__main__":
    # 模拟新员工「陈小新」入职生成数字名片（不阻塞 input，方便直接运行验证）
    demo_card = build_profile_card(
        name="陈小新",
        employee_id=42,
        department="AI 应用研发部",
        phone="13857108899",
        years_of_exp=0.5,
        is_ai_team=True,
    )
    print(demo_card)
''',
                "explanation": (
                    "1. `f'XM-{int(employee_id):04d}'` 中的 `:04d` 表示不足 4 位自动左侧补 0，企业工号、订单号极常用。\n"
                    "2. `f'{quota:,}'` 自动加上千分位逗号（如 `82,500`），打印报表和 Token 账单时非常清爽。\n"
                    "3. `max(0.0, years_of_exp)` 属于防御性编程：万一上游传入负数工龄，不会把配额扣成负数。"
                ),
                "expected_output": (
                    "+------------------------------------------+\n"
                    "|  杭州星辰数科 · 星辰智脑 StarMind 数字名片  |\n"
                    "+------------------------------------------+\n"
                    "  姓名     : 陈小新\n"
                    "  工号     : XM-0042\n"
                    "  部门     : AI 应用研发部\n"
                    "  联系电话 : 138****8899\n"
                    "  工作年限 : 0.5 年\n"
                    "  AI 权限  : 已开通 (核心研发权限)\n"
                    "  每日配额 : 82,500 Tokens\n"
                    "+------------------------------------------+"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-001 自动化单元测试（阿杰验收脚本）。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day01_env_check import check_environment, format_env_report
from day01_profile_card import mask_phone, calculate_token_quota, build_profile_card


def test_env_check_passes():
    report = check_environment()
    assert report["is_compatible"] is True
    assert "tsinghua" in report["recommended_mirror"]
    text = format_env_report(report)
    assert "[PASS]" in text


def test_mask_phone_normal_and_invalid():
    assert mask_phone("13857108899") == "138****8899"
    assert mask_phone(" 13900001234 ") == "139****1234"
    assert mask_phone("12345") == "格式异常(已隐藏)"


def test_calculate_token_quota():
    # 0.5 年经验 + AI 团队: (50000 + 5000) * 1.5 = 82500
    assert calculate_token_quota(0.5, True) == 82500
    # 2 年经验 + 非 AI 团队: (50000 + 20000) * 1.0 = 70000
    assert calculate_token_quota(2.0, False) == 70000
    # 负数工龄防御
    assert calculate_token_quota(-3.0, False) == 50000


def test_build_profile_card_contains_masked_info():
    card = build_profile_card("林小星", 7, "产品部", "18612345678", 3.0, False)
    assert "XM-0007" in card
    assert "186****5678" in card
    assert "18612345678" not in card
    assert "80,000 Tokens" in card
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "不错！把 mask_phone 和 calculate_token_quota 拆成独立纯函数，而且没在顶层写阻塞的 input()，这是很好的工程习惯。建议给 years_of_exp 加上负数兜底。",
                "resolution": "已通过 max(0.0, years_of_exp) 完成边界防护。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "已补充异常手机号（位数不足、带前后空格）测试用例，验证名片中绝不出现明文手机号，4 个 pytest 用例全部绿灯。",
                "resolution": "QA 验收通过，准予合入 main 分支。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：API 费用人民币估算器",
                "difficulty": "基础巩固",
                "requirement": "假设星辰智脑调用 DeepSeek 模型输入单价为 0.002 元/千 Tokens，输出单价为 0.008 元/千 Tokens。编写函数 `estimate_cost(input_tokens: int, output_tokens: int) -> float`，返回本次对话的总费用（保留 6 位小数），并打印格式化账单。",
                "hint": "注意单位换算是除以 1000.0，最后使用 round(cost, 6) 消除浮点尾部噪音。",
                "solution_code": r'''"""Day 1 课后题 1：大模型调用费用估算器。"""

INPUT_PRICE_PER_1K = 0.002   # 输入单价：元 / 1000 Tokens
OUTPUT_PRICE_PER_1K = 0.008  # 输出单价：元 / 1000 Tokens


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """计算单次大模型对话的人民币费用（元）。"""
    # 防止传入负数 Token
    safe_in = max(0, int(input_tokens))
    safe_out = max(0, int(output_tokens))
    # 按千 Token 单价分别计算并相加
    total = (safe_in / 1000.0) * INPUT_PRICE_PER_1K + (safe_out / 1000.0) * OUTPUT_PRICE_PER_1K
    return round(total, 6)


if __name__ == "__main__":
    cost = estimate_cost(1500, 800)
    print(f"本次调用输入 1500 Tokens，输出 800 Tokens，预计费用：¥{cost:.6f}")
''',
                "solution_analysis": "重点考查 int/float 混合运算与 `round()` 精度控制。评分要点：1）常量抽取清晰；2）边界负数保护；3）格式化输出保留 6 位小数。"
            },
            {
                "title": "企业实战：多字段员工隐私脱敏工具",
                "difficulty": "企业实战",
                "requirement": "林产品反馈除了手机号，员工邮箱（如 `chenxiaoxin@starmind.cn`）和身份证号也需要脱敏。编写 `mask_email(email: str) -> str`（保留首字符与 `@` 后域名，中间用 `***` 替代），并在主流程中输出完整的脱敏摘要。",
                "hint": "用 `email.split('@')` 拆出用户名和域名，先判断 `'@' in email` 防止报错。",
                "solution_code": r'''"""Day 1 课后题 2：企业员工邮箱与身份信息脱敏工具。"""


def mask_email(email: str) -> str:
    """对企业邮箱执行脱敏：保留前缀首字母与完整域名。"""
    cleaned = email.strip()
    if "@" not in cleaned:
        return "无效邮箱"
    local_part, domain = cleaned.split("@", 1)
    if not local_part or not domain:
        return "无效邮箱"
    # 保留用户名第一个字符，其余用 *** 掩码
    return f"{local_part[0]}***@{domain}"


if __name__ == "__main__":
    for sample in ["chenxiaoxin@starmind.cn", "a@corp.com", "invalid-mail"]:
        print(f"{sample:25s} -> {mask_email(sample)}")
''',
                "solution_analysis": "考查字符串切分 `split('@', 1)` 与异常输入防御。注意限制 `maxsplit=1`，防止异常字符串包含多个 `@` 导致解包报错 `ValueError`。"
            },
            {
                "title": "架构进阶：带环境变量检测的启动预检器",
                "difficulty": "架构进阶",
                "requirement": "在企业服务启动前，往往需要检查关键配置（如 `STARMIND_ENV`、`PYTHONUTF8`）是否就绪。编写 `preflight_check(env_map: dict) -> tuple[bool, str]`，在不依赖真实操作系统的情况下支持注入字典做可测试的启动预检。",
                "hint": "通过参数传入 `env_map` 而不是硬编码 `os.environ`，这就是架构设计中的「依赖注入」雏形。",
                "solution_code": r'''"""Day 1 课后题 3：可测试的服务启动预检器（依赖注入雏形）。"""

from typing import Dict, Tuple


def preflight_check(env_map: Dict[str, str]) -> Tuple[bool, str]:
    """检查运行环境配置是否满足星辰智脑启动条件。"""
    # 检查运行环境标识是否合法
    app_env = env_map.get("STARMIND_ENV", "dev").lower()
    valid_envs = ("dev", "staging", "prod")
    if app_env not in valid_envs:
        return False, f"非法环境标识: {app_env}，仅允许 {valid_envs}"

    # 生产环境强制要求配置 API 密钥
    if app_env == "prod" and not env_map.get("STARMIND_API_KEY"):
        return False, "生产环境缺少 STARMIND_API_KEY，拒绝启动！"

    return True, f"预检通过，当前模式: {app_env}"


if __name__ == "__main__":
    print(preflight_check({"STARMIND_ENV": "dev"}))
    print(preflight_check({"STARMIND_ENV": "prod"}))
    print(preflight_check({"STARMIND_ENV": "prod", "STARMIND_API_KEY": "sk-demo"}))
''',
                "solution_analysis": "本题提前引入「依赖注入」思想：把外部环境变量作为函数参数传入，测试时不用修改真实系统环境变量就能覆盖 dev/prod/缺密钥等全部场景。"
            }
        ],
        "extra_deep_dive": (
            "【老陈踩坑实录：Windows 下 GBK 编码暗雷】\n"
            "国内企业开发机有一大半是 Windows，默认终端编码经常是 GBK（cp936），而大模型返回的文本里经常夹杂 Emoji 或生僻中文字符，一旦直接 `open()` 读写文件不写 `encoding='utf-8'`，立刻抛出 `UnicodeEncodeError`。"
            "大厂通用解法：1）所有文件读写显式传 `encoding='utf-8'`；2）在系统环境变量中配置 `PYTHONUTF8=1`，强制 Python 3.11 全链路走 UTF-8。"
        )
    },

    # =========================================================================
    # DAY 2: 运算符与字符串
    # =========================================================================
    {
        "day": 2,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "运算符与字符串",
        "subtitle": "打造星辰智脑工单文本清洗器与 f-string Prompt 模板引擎",
        "gitlab_ticket": "STARMIND-002",
        "git_branch": "feat/day02-text-cleaner-prompt",
        "git_commit": "feat(day02): 实现客服文本清洗流水线与f-string Prompt模板渲染器",
        "prev_recap": "昨天咱们搭好了 Python 3.11 + 国内镜像源环境，完成了 STARMIND-001 员工数字名片工具，4 个 pytest 用例全部跑通。",
        "next_preview": "明天（Day 3）咱们引入条件分支与循环流程控制，把今天单条清洗升级成可交互的命令行菜单与批量路由分发器。",
        "narrator_opening": (
            "早啊！刚开完早会，林产品在飞书里发了一堆真实客服工单截图——全是用户从微信和网页复制过来的脏数据："
            "前后一堆全角空格、莫名其妙的换行符、夹杂着广告链接，还有大小写乱写的订单号。"
            "记住：大模型吃进去垃圾，吐出来的就是更贵的垃圾（Garbage In, Garbage Out），还会白白烧掉你几倍的 Token 费！"
            "今天 STARMIND-002 咱们吃透 Python 运算符和字符串操作，亲手写一个企业级「文本清洗工具」和「f-string Prompt 模板引擎」，给大模型喂最干净的粮食。"
        ),
        "narrator_closing": (
            "今天写完文本清洗和 Prompt 模板，你应该能感受到：大模型应用开发里至少 40% 的脏活累活本质上都是字符串处理。"
            "记住切片左闭右开、字符串不可变、拼接大文本优先用 `''.join()` 这三条铁律。晚上把三道题练熟，明天咱们学流程控制！"
        ),
        "business_prd": {
            "background": "客服系统每天产生数万条用户反馈文本，直接送入大模型分析会导致 Token 浪费高达 25%，且格式杂乱影响模型抽取准确度。",
            "pain_points": [
                "用户输入包含大量多余空白、制表符、全角空格及无意义重复标点。",
                "客服提问缺少统一上下文结构，直接丢给大模型经常答非所问。",
                "缺乏快速预估文本长度与是否超限的规则判断。"
            ],
            "goals": [
                "掌握算术、比较、逻辑与成员运算符（in / not in）及短路求值特性。",
                "熟练运用字符串切片、strip/replace/split/join/lower/upper 等核心方法。",
                "使用 f-string 构建结构化 Prompt 模板，并实现可复用的文本清洗函数。"
            ],
            "acceptance_criteria": [
                "文本清洗器能清除首尾空白、折叠连续空格、统一全角空格并标准化订单号前缀。",
                "Prompt 模板能动态注入角色、用户问题、字数限制并计算估算 Token 数。",
                "所有边界用例（空字符串、超长文本截断、敏感词命中检测）通过 pytest。"
            ],
            "non_functional": [
                "纯字符串方法实现，单条清洗耗时低于 1ms。",
                "遵循纯函数设计，不修改外部状态。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "运算符体系与字符串底层切片机制", "detail": "精讲 //、%、**、逻辑短路、正向与负向切片步长，结合 Token 计费与文本截断场景练习。"},
            {"slot": "下午 14:00-17:30", "topic": "字符串核心方法与 f-string Prompt 模板", "detail": "开发工单文本清洗工具与客服 Prompt 模板渲染器，完成超长文本安全截断。"},
            {"slot": "晚间 19:00-20:30", "topic": "自动化单元测试与边界 Case 排查", "detail": "编写 pytest 用例覆盖空串、全角空格、超长文本与违禁词拦截。"},
            {"slot": "复盘 20:30-21:00", "topic": "Code Review 与课后实战巩固", "detail": "老陈点评字符串不可变性坑点，完成 3 道梯度课后作业。"}
        ],
        "architecture_design": (
            "在星辰智脑的文本预处理链路中，我们采用「管道式（Pipeline）清洗架构」：\n"
            "原始脏文本 -> 全角/特殊空白归一化 -> 连续空白折叠 -> 订单号标准化 -> 长度合规截断 -> 注入 Prompt 模板。\n"
            "为什么要把清洗和模板渲染拆成两个独立模块（day02_text_cleaner.py 与 day02_prompt_template.py）？\n"
            "因为清洗器是全平台通用的基础组件（后续 RAG 文档切片、日志分析都要复用），而 Prompt 模板强绑定业务场景（客服、摘要、翻译各有各的模板）。"
            "这种按「变化频率」拆分模块的思路，是大厂架构师最常用的解耦手法。"
        ),
        "diagrams": [
            {
                "title": "工单文本清洗与 Prompt 拼装流程图",
                "kind": "flowchart",
                "caption": "展示一条原始客服工单如何经过 4 步清洗后安全注入到 Prompt 模板中。",
                "nodes": [
                    {"id": "n1", "label": "原始工单文本", "sub": "含全角空格/换行/脏符号", "color": "#ef4444"},
                    {"id": "n2", "label": "空白归一化", "sub": "replace全角 + split/join", "color": "#f59e0b"},
                    {"id": "n3", "label": "敏感词与长度检查", "sub": "成员运算 in + 切片截断", "color": "#8b5cf6"},
                    {"id": "n4", "label": "f-string 模板注入", "sub": "角色+约束+清洗后问题", "color": "#3b82f6"},
                    {"id": "n5", "label": "标准 Prompt 输出", "sub": "附带 Token 粗估指标", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "清洗空白"},
                    {"from": "n2", "to": "n3", "label": "安全截断"},
                    {"from": "n3", "to": "n4", "label": "渲染模板"},
                    {"from": "n4", "to": "n5", "label": "送往模型"}
                ]
            },
            {
                "title": "文本预处理与模板引擎分层架构图",
                "kind": "architecture",
                "caption": "将通用文本清洗层与业务 Prompt 模板层解耦，便于未来横向扩展多业务场景。",
                "nodes": [
                    {"id": "a1", "label": "多渠道输入", "sub": "微信/网页/工单系统", "color": "#64748b"},
                    {"id": "a2", "label": "TextCleaner 组件", "sub": "空白折叠/脱敏/截断", "color": "#3b82f6"},
                    {"id": "a3", "label": "PromptTemplate 引擎", "sub": "f-string 结构化组装", "color": "#8b5cf6"},
                    {"id": "a4", "label": "预算估算器", "sub": "整除 // 计算 Token 块", "color": "#f59e0b"},
                    {"id": "a5", "label": "下游 LLM 网关", "sub": "Day 12 正式接入", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "原始文本"},
                    {"from": "a2", "to": "a3", "label": "纯净文本"},
                    {"from": "a3", "to": "a4", "label": "长度统计"},
                    {"from": "a4", "to": "a5", "label": "合规 Prompt"}
                ]
            },
            {
                "title": "Python 字符串正负索引切片原理图",
                "kind": "schematic",
                "caption": "以 'STARMIND' 为例展示正向索引(0..7)、负向索引(-8..-1)以及左闭右开切片规则。",
                "nodes": [
                    {"id": "s1", "label": "索引 0 / -8", "sub": "字符 'S'", "color": "#3b82f6"},
                    {"id": "s2", "label": "索引 1..3", "sub": "字符 'TAR' (s[0:4]='STAR')", "color": "#10b981"},
                    {"id": "s3", "label": "索引 4..7", "sub": "字符 'MIND' (s[-4:]='MIND')", "color": "#8b5cf6"},
                    {"id": "s4", "label": "反转切片 s[::-1]", "sub": "结果 'DNIMRATS'", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "正向步长 +1"},
                    {"from": "s2", "to": "s3", "label": "负向定位"},
                    {"from": "s3", "to": "s4", "label": "步长 -1 反转"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 运算符与短路求值",
                "content": (
                    "算术运算中 `/` 永远返回浮点数，`//` 是向下取整除法，`%` 取余，`**` 幂运算。"
                    "逻辑运算符 `and` / `or` 具备短路特性：`text and text.strip()` 会在 `text` 为空字符串或 `None` 时直接短路返回，不会触发 `.strip()` 报错。"
                    "成员运算符 `in` / `not in` 在敏感词检测、关键词匹配中极其常用。"
                ),
                "pitfalls": "注意 `==` 判断值相等，而 `is` 判断内存地址是否为同一个对象！判断 `None` 用 `is None`，比较字符串或大整数永远用 `==`。"
            },
            {
                "heading": "2. 字符串不可变性与高频方法",
                "content": (
                    "Python 的 `str` 是不可变对象，调用 `s.strip()` 或 `s.replace('a', 'b')` 不会原地修改 `s`，而是返回一个新字符串，必须重新赋值！"
                    "折叠任意连续空白（空格、换行、制表符）的最优雅写法是 `' '.join(text.split())`，一行搞定。"
                ),
                "pitfalls": "初学者最常犯的错：写了一行 `text.replace(' ', '')` 却没写 `text = text.replace(' ', '')`，结果发现字符串纹丝不动！"
            },
            {
                "heading": "3. f-string 与 Prompt 工程模板",
                "content": (
                    "f-string 支持直接嵌入表达式、格式化精度（`{val:.2f}`）、对齐填充（`{name:<10}`）以及多行三引号模板。"
                    "在大模型开发里，用三引号 f-string 搭配明确分隔符（如 `###` 或 XML 标签 `<user_query>`）是防提示词混乱的标准姿势。"
                ),
                "pitfalls": "如果在 f-string 里要输出 JSON 的真实花括号 `{}`，必须双写转义为 `{{` 和 `}}`，否则 Python 会把它当变量解析报错。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：编写客服工单文本清洗器",
                "file_path": "src/day02_text_cleaner.py",
                "narration": "先解决脏文本问题。咱们把全角空格替换、多余换行折叠、订单号大写标准化和安全截断都封进 `clean_ticket_text` 函数。",
                "code": r'''"""
STARMIND-002 模块一：企业客服工单文本清洗器。
演示字符串不可变性、核心方法（replace/split/join/upper）、切片截断与成员运算符。
"""

# 定义常见的违禁/高风险测试词（演示成员运算符 in）
BLOCKED_KEYWORDS = ("刷单", "代开发票", "木马链接")


def clean_ticket_text(raw_text: str, max_length: int = 200) -> str:
    """
    清洗客服工单原始文本：
    1. 将中文全角空格（\\u3000）替换为普通空格；
    2. 利用 split() + join() 折叠所有连续空格、制表符和多余换行；
    3. 统一把小写订单前缀 'ord-' 标准化为 'ORD-'；
    4. 若超过 max_length，使用切片截断并追加省略号。
    """
    # 防御 None 或空字符串输入
    if not raw_text:
        return ""

    # 第 1 步：替换全角空格与不间断空格
    normalized = raw_text.replace("\u3000", " ").replace("\xa0", " ")

    # 第 2 步：split() 不传参会按任意连续空白切分，再用单个空格拼回
    compact = " ".join(normalized.split())

    # 第 3 步：标准化常见小写订单号前缀
    standardized = compact.replace("ord-", "ORD-").replace("Ord-", "ORD-")

    # 第 4 步：使用切片进行长度控制，防止超长文本打爆 Token 预算
    if len(standardized) > max_length:
        # 预留 3 个字符给 '...'
        cutoff = max(0, max_length - 3)
        return standardized[:cutoff] + "..."

    return standardized


def has_blocked_content(text: str) -> bool:
    """检查清洗后的文本是否命中风险关键词。"""
    # 使用成员运算符 in 结合 any 表达式判断
    return any(keyword in text for keyword in BLOCKED_KEYWORDS)


if __name__ == "__main__":
    dirty = "  \u3000你好！！\n\n  我的订单  ord-20260501   一直没发货，   麻烦查一下\t谢谢！  "
    cleaned = clean_ticket_text(dirty, max_length=60)
    print(f"原始长度: {len(dirty)} -> 清洗后长度: {len(cleaned)}")
    print(f"清洗结果: {cleaned}")
    print(f"风险拦截: {has_blocked_content(cleaned)}")
''',
                "explanation": (
                    "1. `raw_text.replace('\\u3000', ' ')` 专门用来对付从微信、Word 复制过来的中文全角空格。\n"
                    "2. `' '.join(normalized.split())` 是 Python 老手最爱的文本压缩技巧，能同时干掉首尾空格、连续空格、`\\n` 和 `\\t`。\n"
                    "3. 切片 `standardized[:cutoff]` 即使 `cutoff` 超出字符串长度也不会抛出 IndexError，非常安全。"
                ),
                "expected_output": (
                    "原始长度: 50 -> 清洗后长度: 36\n"
                    "清洗结果: 你好！！ 我的订单 ORD-20260501 一直没发货， 麻烦查一下 谢谢！\n"
                    "风险拦截: False"
                )
            },
            {
                "step_title": "步骤二：打造 f-string Prompt 模板渲染与 Token 估算引擎",
                "file_path": "src/day02_prompt_template.py",
                "narration": "文本洗干净了，接下来咱们用 f-string 把角色设定、业务规则、清洗后的用户提问组装成一份专业 Prompt，顺便用算术运算符估算一下大概消耗多少 Token。",
                "code": r'''"""
STARMIND-002 模块二：f-string Prompt 模板引擎与 Token 粗估工具。
演示多行 f-string、转义花括号、算术运算符（整除 // 与向上取整技巧）。
"""

from day02_text_cleaner import clean_ticket_text, has_blocked_content


def estimate_tokens_rough(text: str) -> int:
    """
    粗略估算中英混合文本的 Token 数量（经验值：约每 2 个字符折算 1.5 个 Token）。
    使用整数运算避免浮点误差，并保证非空文本至少返回 1。
    """
    if not text:
        return 0
    # 向上取整技巧：(长度 * 3 + 3) // 4 等价于 ceil(len * 0.75)
    return max(1, (len(text) * 3 + 3) // 4)


def render_support_prompt(
    user_query: str,
    customer_tier: str = "VIP",
    max_reply_words: int = 120,
) -> str:
    """将清洗后的用户问题组装为星辰智脑标准客服 Prompt。"""
    cleaned_query = clean_ticket_text(user_query, max_length=300)

    # 若触发安全词拦截，直接返回拒答提示模板
    if has_blocked_content(cleaned_query):
        return "[BLOCKED] 检测到高风险违规内容，已拦截，不送入大模型。"

    # 使用多行 f-string 与 XML 标签清晰隔离用户输入，降低提示词注入风险
    # 注意：JSON 示例中的花括号必须双写 {{ }} 进行转义
    prompt = f"""你是「杭州星辰数科」官方智能客服助手，专业、克制且高效。
当前服务客户等级：{customer_tier.upper()}
回复字数要求：不超过 {max_reply_words} 字，必须输出如下 JSON 格式：
{{"intent": "物流查询|退款售后|其他", "reply": "你的回复内容"}}

请严格基于以下标签内的用户原始提问作答：
<user_query>
{cleaned_query}
</user_query>"""
    return prompt


if __name__ == "__main__":
    sample_q = "  \n 麻烦问下 ord-99812 啥时候能送到杭州滨江？\u3000急用！ "
    final_prompt = render_support_prompt(sample_q, customer_tier="svip", max_reply_words=80)
    est_tokens = estimate_tokens_rough(final_prompt)
    print(final_prompt)
    print(f"\n--- 预估输入 Token 数: 约 {est_tokens} Tokens ---")
''',
                "explanation": (
                    "1. `(len(text) * 3 + 3) // 4` 是工程中常用的纯整数向上取整写法，无需引入 math 库就能算出 `ceil(n * 0.75)`。\n"
                    "2. Prompt 中用 `{{` 和 `}}` 转义了 JSON 模板的花括号，同时用 `<user_query>` 标签包裹用户输入，为 Day 18 的提示词注入防御埋下伏笔。"
                ),
                "expected_output": (
                    "你是「杭州星辰数科」官方智能客服助手，专业、克制且高效。\n"
                    "当前服务客户等级：SVIP\n"
                    "回复字数要求：不超过 80 字，必须输出如下 JSON 格式：\n"
                    "{\"intent\": \"物流查询|退款售后|其他\", \"reply\": \"你的回复内容\"}\n\n"
                    "请严格基于以下标签内的用户原始提问作答：\n"
                    "<user_query>\n"
                    "麻烦问下 ORD-99812 啥时候能送到杭州滨江？ 急用！\n"
                    "</user_query>\n\n"
                    "--- 预估输入 Token 数: 约 126 Tokens ---"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-002 自动化单元测试。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day02_text_cleaner import clean_ticket_text, has_blocked_content
from day02_prompt_template import estimate_tokens_rough, render_support_prompt


def test_clean_ticket_text_whitespace_and_order_id():
    raw = " \u3000订单\t ord-10086 \n\n  未发货  "
    assert clean_ticket_text(raw) == "订单 ORD-10086 未发货"
    assert clean_ticket_text("") == ""


def test_clean_ticket_text_truncation():
    long_text = "星辰智脑" * 20  # 80 字符
    result = clean_ticket_text(long_text, max_length=15)
    assert len(result) == 15
    assert result.endswith("...")


def test_blocked_content_detection():
    assert has_blocked_content("你好请问支持刷单吗") is True
    assert has_blocked_content("请问发票怎么开") is False


def test_render_support_prompt_and_token_estimate():
    prompt = render_support_prompt("  查一下 ord-777  ", customer_tier="vip", max_reply_words=100)
    assert "VIP" in prompt
    assert "ORD-777" in prompt
    assert '{"intent":' in prompt
    assert estimate_tokens_rough(prompt) > 20
    assert render_support_prompt("点这个木马链接领取") .startswith("[BLOCKED]")
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "用 `<user_query>` XML 标签把用户脏输入和系统指令隔开，这个细节非常加分！整除向上取整的注释也很清晰。",
                "resolution": "Approved，准予合并。"
            },
            {
                "reviewer": "林产品 (PM)",
                "role": "Product Acceptance",
                "comment": "试了十几条客服真实工单，全角空格和乱七八糟的换行全被洗干净了，ORD- 订单号也统一了。",
                "resolution": "产品验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：商品标题去噪与截断",
                "difficulty": "基础巩固",
                "requirement": "电商运营上传的商品标题常带 `【爆款】`、`[限时]` 等营销前缀和多余空格。编写函数 `normalize_title(title: str, limit: int = 20) -> str`，去除 `【爆款】`、`[限时]` 并折叠空白，超长则切片截断加 `...`。",
                "hint": "链式调用 `.replace()` 后再用 `' '.join(s.split())`，最后判断长度切片。",
                "solution_code": r'''"""Day 2 课后题 1：商品标题清洗与截断。"""


def normalize_title(title: str, limit: int = 20) -> str:
    """移除营销标签、压缩空白并按字数限制截断标题。"""
    cleaned = title.replace("【爆款】", "").replace("[限时]", "")
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > limit:
        return cleaned[: max(0, limit - 3)] + "..."
    return cleaned


if __name__ == "__main__":
    raw = "  【爆款】  [限时]  星辰智脑   企业级AI知识库私有化部署套件  "
    print(normalize_title(raw, limit=16))
''',
                "solution_analysis": "考查字符串链式替换与切片边界计算。注意先去标签再统计长度，顺序不能反。"
            },
            {
                "title": "企业实战：对话日志快速摘要统计器",
                "difficulty": "企业实战",
                "requirement": "给定一段包含多行对话的字符串（每行格式为 `USER: ...` 或 `AI: ...`），利用字符串方法统计总字符数、是否包含关键字 `'退款'`、以及 `USER:` 出现的次数，返回格式化报告。",
                "hint": "使用 `str.count('USER:')`、`len()` 和成员运算符 `in`。",
                "solution_code": r'''"""Day 2 课后题 2：对话日志摘要统计器。"""


def summarize_chat_log(log_text: str) -> str:
    """统计对话日志的基础指标并返回摘要。"""
    cleaned = log_text.strip()
    user_turns = cleaned.count("USER:")
    ai_turns = cleaned.count("AI:")
    has_refund = "退款" in cleaned
    return (
        f"日志总字数: {len(cleaned)} | 用户轮次: {user_turns} | "
        f"AI 轮次: {ai_turns} | 涉及退款: {'是' if has_refund else '否'}"
    )


if __name__ == "__main__":
    sample_log = "USER: 你好，我想申请退款\nAI: 请提供您的订单号\nUSER: ORD-1001"
    print(summarize_chat_log(sample_log))
''',
                "solution_analysis": "利用 `str.count()` 无需写循环就能快速统计特征子串出现频次，适合日志初筛场景。"
            },
            {
                "title": "架构进阶：带变量校验的安全 Prompt 渲染器",
                "difficulty": "架构进阶",
                "requirement": "业务同学经常手写 Prompt 模板如 `'你好 {name}，欢迎使用 {product}'`，但如果漏传变量会导致线上崩溃。请编写 `safe_render(template: str, **kwargs) -> str`，在渲染前检查必要占位符是否存在，若缺失则给出友好错误提示而不是直接崩掉。",
                "hint": "捕获 `KeyError` 或提前检查关键字段；这里可以先用条件判断或 `template.format_map()` 配合默认占位。",
                "solution_code": r'''"""Day 2 课后题 3：防崩溃的 Prompt 模板安全渲染器。"""


class SafeDict(dict):
    """当模板缺少某个键时，保留原始占位符而不是抛出 KeyError。"""

    def __missing__(self, key: str) -> str:
        return f"<MISSING:{key}>"


def safe_render(template: str, variables: dict) -> str:
    """安全渲染模板，缺失字段自动标记为 <MISSING:key>。"""
    return template.format_map(SafeDict(variables))


if __name__ == "__main__":
    tpl = "你好 {user}，你的 {plan} 套餐剩余 {quota} Tokens。"
    print(safe_render(tpl, {"user": "陈小新", "plan": "企业版"}))
''',
                "solution_analysis": "利用 `str.format_map()` 与自定义字典缺失处理，既保证生产环境不因运营少配一个字段而 500 报错，又能在监控日志里一眼看出 `<MISSING:quota>`。"
            }
        ],
        "extra_deep_dive": (
            "【生产级性能小贴士：千万别在循环里用 `+=` 拼几万次字符串】\n"
            "因为 Python 字符串不可变，每次 `s += chunk` 都会在堆上重新分配一块更大的内存并把旧内容拷贝过去，时间复杂度退化成 O(n²)。"
            "在大模型流式接收（Streaming）成千上万个文本分片时，标准大厂写法是把分片放进列表 `chunks.append(chunk)`，最后一次性 `''.join(chunks)`，内存与 CPU 开销直降一个数量级。"
        )
    },

    # =========================================================================
    # DAY 3: 流程控制
    # =========================================================================
    {
        "day": 3,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "流程控制",
        "subtitle": "掌握条件路由与循环调度，打造星辰智脑命令行交互控制台与测试沙盒",
        "gitlab_ticket": "STARMIND-003",
        "git_branch": "feat/day03-control-flow-cli",
        "git_commit": "feat(day03): 实现工单智能分流引擎、猜数字沙盒与命令行交互菜单",
        "prev_recap": "昨天咱们完成了工单文本清洗器与 f-string Prompt 模板引擎，洗干净了单条输入数据。",
        "next_preview": "明天（Day 4）咱们升级数据容器，学习列表（list）、元组（tuple）和集合（set），给星辰智脑做出待办事项管理器与标签去重引擎。",
        "narrator_opening": (
            "前两天咱们写的都是「一条道走到黑」的顺序代码，今天要让程序长出脑子——学会做判断和干重复活！"
            "林产品刚提了 STARMIND-003：客服工单进来后，要根据紧急程度和金额自动分流给「人工专家」「高级模型」或「轻量模型」；"
            "另外为了方便运营同学在终端里试用工具，需要做一个命令行交互菜单，顺便把经典的「猜数字推理测试」和「九九配额表」做成演示命令。"
            "重点提醒一下：写循环控制台时，千万要把交互逻辑封装成函数，支持传入模拟指令列表跑自动化测试，不然阿杰跑 CI 时直接卡死在 `input()` 里！"
        ),
        "narrator_closing": (
            "今天你已经掌握了编程世界最核心的三大结构：顺序、分支、循环。"
            "记住老陈的「卫语句（Guard Clause）」原则：条件判断尽量提前 return，别写出五六层缩进的「箭头代码」，看着头疼还容易漏分支。"
            "晚上把菜单和分流逻辑再过一遍，明天咱们进入核心数据结构！"
        ),
        "business_prd": {
            "background": "星辰智脑每天面对高价值客诉、普通咨询、垃圾广告三类混合工单，全部调用昂贵的旗舰大模型会导致算力成本失控，需要基于规则的流程路由与终端运营控制台。",
            "pain_points": [
                "所有工单无差别调用旗舰模型，成本居高不下。",
                "缺乏批量处理与异常跳过（continue）/ 熔断中止（break）机制。",
                "运维脚本每次只能跑一个功能，缺少统一命令行菜单入口。"
            ],
            "goals": [
                "精通 `if / elif / else` 多分支路由与卫语句降嵌套技巧。",
                "掌握 `for`、`while`、`range`、`break`、`continue` 在批处理与交互菜单中的应用。",
                "完成工单路由分发器、九九算力表、猜数字二分验证器与可测试命令行菜单。"
            ],
            "acceptance_criteria": [
                "能按金额、关键词与客户等级将工单准确路由至 L1/L2/L3 通道。",
                "支持批量工单扫描：遇空工单 `continue` 跳过，遇高危攻击 `break` 触发熔断。",
                "CLI 菜单支持传入模拟命令序列自动执行并正常退出，pytest 全部通过。"
            ],
            "non_functional": [
                "禁止无限死循环，所有 `while` 循环必须具备明确退出条件或最大步数上限。",
                "CLI 模块兼顾真实终端交互与无阻塞自动化测试。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "条件分支与企业级规则路由引擎", "detail": "学习 if/elif/else 与卫语句写法，编写星辰智脑工单三级分流路由器。"},
            {"slot": "下午 14:00-17:30", "topic": "循环控制、九九乘法表与命令行菜单实战", "detail": "掌握 for/while/range/break/continue，完成猜数字游戏引擎与可测试 CLI 控制台。"},
            {"slot": "晚间 19:00-20:30", "topic": "熔断机制测试与边界验证", "detail": "用 pytest 模拟多轮菜单指令与批处理熔断场景。"},
            {"slot": "复盘 20:30-21:00", "topic": "代码嵌套优化复盘与课后作业", "detail": "重构深层嵌套代码，完成 3 道梯度课后题。"}
        ],
        "architecture_design": (
            "今天的代码包含两个关键工程模式：\n"
            "1. **规则路由与批处理熔断模式**（day03_ticket_router.py）：在遍历工单队列时，空文本或无效数据用 `continue` 静默跳过并计数；一旦监测到疑似 DDoS 或批量注入攻击特征，立刻触发 `break` 熔断整批任务并告警，保护下游大模型额度不被刷爆。\n"
            "2. **可测试的 CLI 命令分发器模式**（day03_cli_menu.py）：初学者写命令行菜单习惯直接 `while True: cmd = input(...)`，这导致代码完全无法做单元测试。"
            "我们的架构方案是：把命令处理抽成 `run_menu_session(commands)`，支持传入指令序列（测试时传列表，人工使用时再接 `input()`），彻底解耦 I/O 与业务逻辑。"
        ),
        "diagrams": [
            {
                "title": "工单三级智能分流与熔断流程图",
                "kind": "flowchart",
                "caption": "展示工单进入批处理循环后，跳过空单、高危熔断以及 L1/L2/L3 模型路由的完整决策树。",
                "nodes": [
                    {"id": "n1", "label": "读取下一条工单", "sub": "for 循环遍历队列", "color": "#3b82f6"},
                    {"id": "n2", "label": "空文本检查", "sub": "空则 continue 跳过", "color": "#64748b"},
                    {"id": "n3", "label": "高危攻击检测", "sub": "命中则 break 熔断", "color": "#ef4444"},
                    {"id": "n4", "label": "金额/VIP 路由", "sub": "if/elif 分发通道", "color": "#f59e0b"},
                    {"id": "n5", "label": "输出分发统计", "sub": "L1轻量/L2旗舰/L3人工", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "取单"},
                    {"from": "n2", "to": "n3", "label": "非空有效"},
                    {"from": "n3", "to": "n4", "label": "安全放行"},
                    {"from": "n4", "to": "n5", "label": "路由记账"}
                ]
            },
            {
                "title": "可测试 CLI 控制台命令分发架构图",
                "kind": "architecture",
                "caption": "通过输入源抽象，让同一套 CLI 菜单核心同时支持人工终端交互与 CI 自动化测试。",
                "nodes": [
                    {"id": "a1", "label": "输入源适配层", "sub": "真实 input() / 测试指令列表", "color": "#3b82f6"},
                    {"id": "a2", "label": "主循环调度器", "sub": "while 循环 + 退出指令", "color": "#8b5cf6"},
                    {"id": "a3", "label": "猜数字推理模块", "sub": "二分反馈 high/low/win", "color": "#10b981"},
                    {"id": "a4", "label": "九九乘法表模块", "sub": "嵌套 for range 格式化", "color": "#f59e0b"},
                    {"id": "a5", "label": "日志输出缓冲", "sub": "收集结果便于断言", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "投递命令"},
                    {"from": "a2", "to": "a3", "label": "cmd == 1"},
                    {"from": "a2", "to": "a4", "label": "cmd == 2"},
                    {"from": "a3", "to": "a5", "label": "记录输出"},
                    {"from": "a4", "to": "a5", "label": "记录输出"}
                ]
            },
            {
                "title": "循环控制 break 与 continue 执行差异示意图",
                "kind": "schematic",
                "caption": "对比 continue（仅跳过本次迭代剩余代码）与 break（直接跳出当前整个循环）的控制流走向。",
                "nodes": [
                    {"id": "s1", "label": "循环入口", "sub": "取第 i 个元素", "color": "#3b82f6"},
                    {"id": "s2", "label": "条件 A 命中", "sub": "执行 continue", "color": "#f59e0b"},
                    {"id": "s3", "label": "条件 B 命中", "sub": "执行 break", "color": "#ef4444"},
                    {"id": "s4", "label": "正常业务逻辑", "sub": "处理当前元素", "color": "#10b981"},
                    {"id": "s5", "label": "循环体外后续代码", "sub": "汇总与返回", "color": "#8b5cf6"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "检查异常"},
                    {"from": "s2", "to": "s1", "label": "跳过本次"},
                    {"from": "s2", "to": "s3", "label": "未命中A"},
                    {"from": "s3", "to": "s5", "label": "立即终止循环"},
                    {"from": "s3", "to": "s4", "label": "正常执行"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. if/elif/else 与卫语句降嵌套",
                "content": (
                    "多分支判断按「最高优先级/最特殊条件」写在最前面。"
                    "当某个异常条件不满足时，直接 `return` 返回结果（卫语句），能把 4 层缩进压平到 1 层，代码可读性瞬间提升。"
                ),
                "pitfalls": "注意 `if` 和 `elif` 是互斥的，只会命中第一个为 True 的分支；如果误把多个 `elif` 全写成 `if`，会导致重复触发多个路由！"
            },
            {
                "heading": "2. for / range 与 while 循环选型",
                "content": (
                    "已知遍历集合或确定次数时优先用 `for ... in ...` 和 `range(start, stop, step)`（同样左闭右开）；"
                    "未知迭代次数、需要等待特定状态结束时（如交互菜单、重试机制）使用 `while`。"
                ),
                "pitfalls": "使用 `while` 循环时，务必确保循环体内有改变终止条件的语句，或在生产代码中加上 `max_steps` 安全护栏，防止线上 CPU 跑满 100%。"
            },
            {
                "heading": "3. break、continue 与循环的 else 子句",
                "content": (
                    "`continue` 跳过当前这一次迭代进入下一轮；`break` 直接打断当前所在的最内层循环。"
                    "Python 特有的 `for ... else:` 语法：只有当循环「正常跑完、没有被 `break` 打断」时，才会执行 `else` 块，非常适合做批量校验后的「全部安全通过」确认。"
                ),
                "pitfalls": "嵌套循环里，`break` 只会跳出离它最近的那一层循环，不会直接跳出外层循环。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：实现工单三级分流路由器与批处理熔断引擎",
                "file_path": "src/day03_ticket_router.py",
                "narration": "先搞定林产品的工单分流需求。咱们用卫语句写单条路由，再用 `for + continue + break + else` 写批量扫描熔断逻辑。",
                "code": r'''"""
STARMIND-003 模块一：工单三级智能路由与批处理熔断引擎。
演示 if/elif/else、卫语句、for 循环、continue 跳过、break 熔断与 for-else 语法。
"""

from typing import List, Dict, Any


def route_single_ticket(text: str, amount: float, is_vip: bool) -> str:
    """
    根据工单内容、涉及金额与客户等级，决定分发通道：
    - L3_HUMAN: 投诉/法律风险 或 涉案金额 >= 5000 元
    - L2_FLAGSHIP_LLM: VIP 客户 或 金额 >= 500 元
    - L1_FAST_LLM: 普通日常咨询
    """
    cleaned = text.strip()
    # 卫语句 1：空工单直接返回无效标记
    if not cleaned:
        return "INVALID"

    # 卫语句 2：高风险关键词或大额纠纷直接转人工专家
    if "投诉" in cleaned or "起诉" in cleaned or amount >= 5000:
        return "L3_HUMAN"

    # VIP 客户或中等金额由旗舰大模型处理
    if is_vip or amount >= 500:
        return "L2_FLAGSHIP_LLM"

    # 其余走低成本轻量大模型
    return "L1_FAST_LLM"


def process_ticket_batch(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    批量扫描工单队列：
    - 空文本工单：continue 跳过并计入 skipped
    - 包含 'ATTACK_PAYLOAD' 的恶意攻击单：立即 break 触发全队列熔断
    """
    stats: Dict[str, Any] = {
        "L1_FAST_LLM": 0,
        "L2_FLAGSHIP_LLM": 0,
        "L3_HUMAN": 0,
        "skipped": 0,
        "circuit_broken": False,
    }

    for ticket in tickets:
        text = str(ticket.get("text", "")).strip()
        # 空工单使用 continue 跳过，不消耗路由资源
        if not text:
            stats["skipped"] += 1
            continue

        # 检测到批量注入攻击特征，立即 break 熔断保护下游
        if "ATTACK_PAYLOAD" in text:
            stats["circuit_broken"] = True
            break

        channel = route_single_ticket(
            text=text,
            amount=float(ticket.get("amount", 0.0)),
            is_vip=bool(ticket.get("is_vip", False)),
        )
        stats[channel] += 1
    else:
        # 仅当循环未被 break 打断时执行，确认批次完整扫描
        stats["completed_cleanly"] = True

    stats.setdefault("completed_cleanly", False)
    return stats


if __name__ == "__main__":
    sample_batch = [
        {"text": "请问怎么修改发票抬头？", "amount": 0, "is_vip": False},
        {"text": "   ", "amount": 0, "is_vip": False},
        {"text": "订单延迟发货我要投诉！", "amount": 200, "is_vip": False},
        {"text": "VIP 专属套餐续费咨询", "amount": 1200, "is_vip": True},
    ]
    print("批次处理统计:", process_ticket_batch(sample_batch))
''',
                "explanation": (
                    "1. `route_single_ticket` 全程用卫语句提前 `return`，没有一层冗余的 `else` 嵌套。\n"
                    "2. `for ... else:` 结构在这里非常地道：正常跑完自动打上 `completed_cleanly = True`；一旦被 `break` 熔断则跳过 `else`。"
                ),
                "expected_output": (
                    "批次处理统计: {'L1_FAST_LLM': 1, 'L2_FLAGSHIP_LLM': 1, 'L3_HUMAN': 1, 'skipped': 1, 'circuit_broken': False, 'completed_cleanly': True}"
                )
            },
            {
                "step_title": "步骤二：实现猜数字沙盒、九九乘法表与可测试 CLI 控制台",
                "file_path": "src/day03_cli_menu.py",
                "narration": "现在把猜数字、九九乘法表和星辰智脑控制台整合进一个 `while` 菜单里。注意看我怎么通过传入指令序列，让它既能手动玩又能秒跑自动化测试。",
                "code": r'''"""
STARMIND-003 模块二：命令行交互菜单、九九乘法表与猜数字验证沙盒。
演示嵌套 for 循环、while 交互循环以及可测试的 CLI 命令分发设计。
"""

from typing import List, Tuple


def build_multiplication_table(n: int = 9) -> str:
    """使用嵌套 for 与 range 生成标准对齐的九九乘法表字符串。"""
    lines: List[str] = []
    # 外层控制行号 1..n
    for row in range(1, n + 1):
        row_items: List[str] = []
        # 内层控制列号 1..row，形成下三角矩阵
        for col in range(1, row + 1):
            row_items.append(f"{col}x{row}={col * row:<2d}")
        lines.append("  ".join(row_items))
    return "\n".join(lines)


def play_guess_number(secret: int, guesses: List[int], max_attempts: int = 5) -> Tuple[bool, List[str]]:
    """
    猜数字核心引擎（非阻塞可测试版）。
    返回 (是否猜中, 每轮反馈日志列表)。
    """
    logs: List[str] = []
    attempts = 0

    for guess in guesses:
        attempts += 1
        if attempts > max_attempts:
            logs.append(f"已超过最大尝试次数 ({max_attempts})，游戏结束！")
            break

        if guess < secret:
            logs.append(f"第 {attempts} 次猜 {guess}：偏小了，往大猜")
        elif guess > secret:
            logs.append(f"第 {attempts} 次猜 {guess}：偏大了，往小猜")
        else:
            logs.append(f"第 {attempts} 次猜 {guess}：恭喜命中目标值 {secret}！")
            return True, logs

    return False, logs


def run_cli_menu(commands: List[str]) -> List[str]:
    """
    星辰智脑命令行交互菜单调度器。
    传入命令列表模拟用户输入：
      '1' -> 查看九九乘法表（前3行预览）
      '2' -> 运行内置猜数字演示
      'q' -> 退出控制台
    """
    outputs: List[str] = []
    idx = 0

    # 使用 while 循环逐条消费指令，带边界索引防止死循环
    while idx < len(commands):
        cmd = commands[idx].strip().lower()
        idx += 1

        if cmd == "1":
            table = build_multiplication_table(3)
            outputs.append(f"[乘法表预览]\n{table}")
        elif cmd == "2":
            won, logs = play_guess_number(secret=42, guesses=[30, 50, 42])
            outputs.append(f"[猜数字演示] 结果={'成功' if won else '失败'} | 步骤数={len(logs)}")
        elif cmd in ("q", "exit", "quit"):
            outputs.append("已安全退出星辰智脑控制台，再见！")
            break
        else:
            outputs.append(f"未知指令 '{cmd}'，请输入 1 / 2 / q")

    return outputs


if __name__ == "__main__":
    print("=== 完整九九乘法表 ===")
    print(build_multiplication_table(9))
    print("\n=== 模拟 CLI 菜单会话 ===")
    session_logs = run_cli_menu(["1", "2", "invalid", "q"])
    for entry in session_logs:
        print(entry)
''',
                "explanation": (
                    "1. `f'{col}x{row}={col * row:<2d}'` 中的 `:<2d` 让个位数自动左对齐补空格，打印出来的九九乘法表整整齐齐。\n"
                    "2. `run_cli_menu(commands)` 把交互驱动和业务分支彻底分开，既能演示 `while` + `break` 的菜单控制流，又能在测试套件里零卡顿跑完所有分支。"
                ),
                "expected_output": (
                    "=== 完整九九乘法表 ===\n"
                    "1x1=1 \n"
                    "1x2=2   2x2=4 \n"
                    "...\n"
                    "=== 模拟 CLI 菜单会话 ===\n"
                    "[乘法表预览]\n"
                    "1x1=1 \n1x2=2   2x2=4 \n1x3=3   2x3=6   3x3=9 \n"
                    "[猜数字演示] 结果=成功 | 步骤数=3\n"
                    "未知指令 'invalid'，请输入 1 / 2 / q\n"
                    "已安全退出星辰智脑控制台，再见！"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-003 自动化单元测试。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day03_ticket_router import route_single_ticket, process_ticket_batch
from day03_cli_menu import build_multiplication_table, play_guess_number, run_cli_menu


def test_route_single_ticket():
    assert route_single_ticket("   ", 0, False) == "INVALID"
    assert route_single_ticket("我要投诉服务差", 10, False) == "L3_HUMAN"
    assert route_single_ticket("大额订单异常", 6000, False) == "L3_HUMAN"
    assert route_single_ticket("普通咨询", 100, True) == "L2_FLAGSHIP_LLM"
    assert route_single_ticket("查物流", 50, False) == "L1_FAST_LLM"


def test_batch_circuit_breaker():
    batch = [
        {"text": "正常问题", "amount": 10, "is_vip": False},
        {"text": "", "amount": 0, "is_vip": False},
        {"text": "ATTACK_PAYLOAD_999", "amount": 0, "is_vip": False},
        {"text": "熔断后不应被处理", "amount": 9999, "is_vip": True},
    ]
    res = process_ticket_batch(batch)
    assert res["L1_FAST_LLM"] == 1
    assert res["skipped"] == 1
    assert res["circuit_broken"] is True
    assert res["completed_cleanly"] is False
    assert res["L3_HUMAN"] == 0


def test_multiplication_and_guess_and_cli():
    table = build_multiplication_table(9)
    assert "9x9=81" in table
    assert len(table.splitlines()) == 9

    won, logs = play_guess_number(secret=50, guesses=[25, 75, 50])
    assert won is True
    assert len(logs) == 3

    lost, _ = play_guess_number(secret=50, guesses=[1, 2, 3], max_attempts=2)
    assert lost is False

    out = run_cli_menu(["1", "2", "unknown", "q", "1"])
    assert len(out) == 4  # q 之后的 '1' 不应执行
    assert "安全退出" in out[-1]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "CLI 菜单用指令列表驱动非常漂亮，避免了阻塞测试。for-else 配合熔断标志也写得很地道。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "验证了熔断后后续工单确实不再计入统计，退出指令 `q` 之后的指令也不会误执行，全部通过。",
                "resolution": "测试通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：API 限流退避重试模拟器",
                "difficulty": "基础巩固",
                "requirement": "大模型接口偶发 429 限流，需要最多重试 4 次。编写 `simulate_retry(statuses: list[int]) -> tuple[bool, int]`，遍历状态码列表：遇到 200 立刻返回 `(True, 尝试次数)`；遇到 429 则继续重试；遇到 401（鉴权失败）立即 `break` 放弃重试并返回 `(False, 尝试次数)`。",
                "hint": "用 `enumerate(statuses, start=1)` 追踪次数，区分可重试错误与不可重试错误。",
                "solution_code": r'''"""Day 3 课后题 1：API 限流重试策略模拟器。"""

from typing import List, Tuple


def simulate_retry(statuses: List[int], max_retries: int = 4) -> Tuple[bool, int]:
    """模拟接口重试：200 成功，429 继续，401 鉴权失败直接放弃。"""
    attempts = 0
    for code in statuses[:max_retries]:
        attempts += 1
        if code == 200:
            return True, attempts
        if code == 401:
            # 密钥错误重试多少次都没用，直接 break 止损
            break
    return False, attempts


if __name__ == "__main__":
    print("场景1(重试成功):", simulate_retry([429, 429, 200]))
    print("场景2(鉴权熔断):", simulate_retry([429, 401, 200]))
''',
                "solution_analysis": "提前演练真实企业 API 调用中的「可重试 vs 不可重试错误」分类思想，避免对 401/400 错误盲目重试浪费配额。"
            },
            {
                "title": "企业实战：Token 预算水位监控器",
                "difficulty": "企业实战",
                "requirement": "给定一组每日消耗 Token 列表，累计总消耗并在超过月度预算 `budget` 时停止扣费，返回已成功处理的请求数和剩余预算。",
                "hint": "循环中先判断 `spent + cost > budget`，若超限则 `break`，否则累加。",
                "solution_code": r'''"""Day 3 课后题 2：月度 Token 预算熔断监控器。"""

from typing import List, Dict


def consume_budget(costs: List[int], budget: int) -> Dict[str, int]:
    """按顺序扣减 Token 预算，即将超限时停止执行。"""
    spent = 0
    processed = 0
    for cost in costs:
        if cost < 0:
            continue
        if spent + cost > budget:
            break
        spent += cost
        processed += 1
    return {"processed": processed, "spent": spent, "remaining": budget - spent}


if __name__ == "__main__":
    print(consume_budget([3000, 4000, 5000, 2000], budget=10000))
''',
                "solution_analysis": "考查循环内前瞻检查（先判超限再扣减）与负值脏数据跳过。"
            },
            {
                "title": "架构进阶：二分查找自动猜数字求解器",
                "difficulty": "架构进阶",
                "requirement": "编写一个自动求解函数 `binary_search_guess(secret: int, low: int = 1, high: int = 100) -> list[int]`，用二分法在最多 7 步内猜中 `[1, 100]` 范围内的任意目标整数，并返回猜测路径。",
                "hint": "每次取 `mid = (low + high) // 2`，偏小则 `low = mid + 1`，偏大则 `high = mid - 1`。",
                "solution_code": r'''"""Day 3 课后题 3：二分查找自动猜数求解器。"""

from typing import List


def binary_search_guess(secret: int, low: int = 1, high: int = 100) -> List[int]:
    """使用二分法定位目标值，返回完整猜测序列。"""
    path: List[int] = []
    while low <= high:
        mid = (low + high) // 2
        path.append(mid)
        if mid == secret:
            break
        elif mid < secret:
            low = mid + 1
        else:
            high = mid - 1
    return path


if __name__ == "__main__":
    trace = binary_search_guess(73)
    print(f"猜测路径: {trace}，仅用 {len(trace)} 步命中！")
''',
                "solution_analysis": "用 `while` 循环实现 O(log N) 二分搜索，100 个数最多 7 步，100 万个数最多 20 步，体会算法思维对循环效率的巨大提升。"
            }
        ],
        "extra_deep_dive": (
            "【大厂代码评审红线：为什么老陈严禁超过 3 层的 if 嵌套？】\n"
            "认知心理学研究表明，工程师大脑能同时记住的嵌套条件上下文不超过 3 层。一旦代码缩进变成 4~5 层，后续维护者极易在错误的层级补上一行 `else`，引发线上逻辑错乱。"
            "养成习惯：异常分支先 `return` / `continue`，主流程永远贴着左边第一层缩进走，你的代码一眼看过去就像散文一样舒服。"
        )
    },

    # =========================================================================
    # DAY 4: 核心数据结构(上)
    # =========================================================================
    {
        "day": 4,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "核心数据结构（上）",
        "subtitle": "精通 list、tuple 与 set，打造星辰智脑待办任务管理器与知识库标签去重引擎",
        "gitlab_ticket": "STARMIND-004",
        "git_branch": "feat/day04-list-tuple-set-todo",
        "git_commit": "feat(day04): 实现待办事项管理器CLI引擎与集合标签去重对比器",
        "prev_recap": "昨天咱们用流程控制做出了工单三级分流器和命令行菜单，但数据还是零散的单个变量，没法动态增删改查。",
        "next_preview": "明天（Day 5）是第一周的重头戏——字典（dict）与 JSON 深度实战！所有大模型 API 的请求和响应全都是嵌套 JSON，明天彻底打通。",
        "narrator_opening": (
            "今天咱们正式进入 Python 最核心的三大序列/集合容器：列表（list）、元组（tuple）、集合（set）。"
            "别小看这仨基础容器，你在 AI 工程里天天跟它们打交道：多轮对话历史 `messages` 是 list，不可变的模型配置快照是 tuple，RAG 召回文档去重靠的是 set！"
            "今天 STARMIND-004 林产品要一个小工具：研发团队用的「命令行待办事项管理器（Todo CLI）」，支持新增、完成、筛选、删除任务，"
            "同时附带一个「知识库标签集合分析器」，帮运营找出两批文档的共同标签和新增标签。"
        ),
        "narrator_closing": (
            "记住今天容器选型的黄金口诀：有序且要增删改用 `list`，只读防篡改用 `tuple`，快速判重和交并差集无脑用 `set`！"
            "特别提醒一句：在百万级数据里判断 `x in container`，`list` 是 O(n) 慢如蜗牛，`set` 是 O(1) 哈希直达。"
            "明天咱们攻克字典与 JSON，做好准备！"
        ),
        "business_prd": {
            "background": "星辰智脑项目组进入密集迭代期，团队需要轻量级任务清单工具追踪每日待办，同时知识库导入文档时存在大量重复标签需要自动去重与比对。",
            "pain_points": [
                "纯散装变量无法动态管理不断增减的任务列表。",
                "人工比对两份知识库文档标签集合极易遗漏。",
                "直接遍历修改列表导致索引错位漏删元素。"
            ],
            "goals": [
                "掌握 list 的增删改查、排序、列表推导式与浅拷贝安全遍历。",
                "理解 tuple 的不可变特性及多值解包（unpacking）用法。",
                "熟练运用 set 的去重及交集（&）、并集（|）、差集（-）运算。"
            ],
            "acceptance_criteria": [
                "待办管理器支持添加任务、按编号标记完成、删除任务、按状态过滤及列表统计。",
                "标签分析器能准确计算两批文档标签的去重全集、公共标签、新增与移除标签。",
                "pytest 单元测试全部通过，包含空列表与越界索引边界处理。"
            ],
            "non_functional": [
                "禁止在遍历原列表时直接 `remove()` 导致漏元素，采用列表推导式或安全拷贝。",
                "使用 tuple 返回只读统计快照，防止调用方误改内部状态。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "list / tuple / set 底层特性与选型", "detail": "对比可变与不可变容器、哈希表 O(1) 查找原理、列表推导式与解包技巧。"},
            {"slot": "下午 14:00-17:30", "topic": "待办事项管理器 CLI 与标签集合分析器", "detail": "完成 STARMIND-004 两个核心模块，实现完整 CRUD 与集合交并差运算。"},
            {"slot": "晚间 19:00-20:30", "topic": "边界测试与推导式重构", "detail": "编写 pytest 覆盖越界删除、重复添加与集合空集运算。"},
            {"slot": "复盘 20:30-21:00", "topic": "浅拷贝坑点复盘与课后作业", "detail": "梳理 `a = b` 与 `a = b.copy()` 区别，完成 3 道梯度课后题。"}
        ],
        "architecture_design": (
            "在 STARMIND-004 中，我们把三种容器各自的优势发挥到极致：\n"
            "1. **待办任务存储（day04_todo_manager.py）**：外层任务列表用 `list` 维持添加顺序；单条任务的状态快照用不可变 `tuple` `(task_id, title, done)` 表示——更新状态时生成新元组替换旧元素，杜绝意外原地修改引发的隐蔽 Bug。\n"
            "2. **知识库标签引擎（day04_tag_analyzer.py）**：把原始带重复和脏空格的标签列表清洗后转入 `set`，利用集合代数运算（交集 `&`、并集 `|`、差集 `-`、对称差 `^`）一行算出版本差异，最终排序转回 `list` 输出稳定结果。"
        ),
        "diagrams": [
            {
                "title": "待办事项管理器 CRUD 操作流程图",
                "kind": "flowchart",
                "caption": "展示待办任务从新增入列、状态翻转、条件过滤到输出只读统计摘要的完整数据流。",
                "nodes": [
                    {"id": "n1", "label": "接收任务指令", "sub": "add / done / remove / list", "color": "#3b82f6"},
                    {"id": "n2", "label": "合法性校验", "sub": "空标题/越界ID拦截", "color": "#f59e0b"},
                    {"id": "n3", "label": "list + tuple 更新", "sub": "替换不可变任务元组", "color": "#8b5cf6"},
                    {"id": "n4", "label": "列表推导式过滤", "sub": "按待办/已完成视图筛选", "color": "#10b981"},
                    {"id": "n5", "label": "返回统计快照", "sub": "(总数, 已完成, 待办数)", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "参数校验"},
                    {"from": "n2", "to": "n3", "label": "更新容器"},
                    {"from": "n3", "to": "n4", "label": "查询视图"},
                    {"from": "n4", "to": "n5", "label": "解包返回"}
                ]
            },
            {
                "title": "三大容器选型与职责划分架构图",
                "kind": "architecture",
                "caption": "在星辰智脑内部根据「有序性、可变性、唯一性」为不同业务数据匹配最优容器。",
                "nodes": [
                    {"id": "a1", "label": "有序可变序列", "sub": "list：任务列表/对话历史", "color": "#3b82f6"},
                    {"id": "a2", "label": "有序不可变记录", "sub": "tuple：只读快照/多返回值", "color": "#8b5cf6"},
                    {"id": "a3", "label": "无序唯一哈希集", "sub": "set：标签去重/权限校验", "color": "#10b981"},
                    {"id": "a4", "label": "业务服务层", "sub": "TodoManager + TagAnalyzer", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "a1", "to": "a4", "label": "动态增删"},
                    {"from": "a2", "to": "a4", "label": "防篡改传递"},
                    {"from": "a3", "to": "a4", "label": "O(1)去重比对"}
                ]
            },
            {
                "title": "集合交并差运算原理示意图",
                "kind": "schematic",
                "caption": "以旧版标签集 A 与新版标签集 B 为例，展示企业知识库标签变更审计的四种集合运算。",
                "nodes": [
                    {"id": "s1", "label": "旧版标签集 A", "sub": "{Python, Prompt, Git}", "color": "#3b82f6"},
                    {"id": "s2", "label": "新版标签集 B", "sub": "{Python, Prompt, RAG}", "color": "#10b981"},
                    {"id": "s3", "label": "交集 A & B", "sub": "{Python, Prompt} (保留)", "color": "#8b5cf6"},
                    {"id": "s4", "label": "差集 B - A", "sub": "{RAG} (新增标签)", "color": "#f59e0b"},
                    {"id": "s5", "label": "差集 A - B", "sub": "{Git} (下线标签)", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "s1", "to": "s3", "label": "共同拥有"},
                    {"from": "s2", "to": "s3", "label": "共同拥有"},
                    {"from": "s2", "to": "s4", "label": "增量分析"},
                    {"from": "s1", "to": "s5", "label": "下线审计"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. list 列表与列表推导式",
                "content": (
                    "`list` 是动态数组，支持 `append`、`extend`、`pop`、`sort` 与切片。"
                    "列表推导式 `[x.strip() for x in raw if x.strip()]` 不仅比手写循环更简洁，在 CPython 底层执行速度也更快。"
                ),
                "pitfalls": "致命坑：永远不要在 `for item in my_list:` 循环中调用 `my_list.remove(item)`！删除元素会导致后续元素前移，直接跳过下一个元素。正确做法是用列表推导式新建过滤后的列表。"
            },
            {
                "heading": "2. tuple 元组与解包",
                "content": (
                    "`tuple` 一旦创建不可增删改元素，占用内存比 `list` 更小，还能作为字典的 key 或放进 `set` 里。"
                    "单元素元组必须加逗号：`(42,)`，否则 `(42)` 只是普通整数！"
                    "支持优雅解包：`task_id, title, done = task`。"
                ),
                "pitfalls": "如果元组里嵌套了一个列表 `t = (1, [2, 3])`，虽然不能替换 `t[1]` 的引用，但里面的列表本身依然可以被 `t[1].append(4)` 修改。"
            },
            {
                "heading": "3. set 集合与哈希去重",
                "content": (
                    "`set` 基于哈希表实现，自动去重且成员检测 `x in s` 为 O(1) 常数时间。"
                    "创建空集合必须用 `set()`，因为 `{}` 创建的是空字典！"
                ),
                "pitfalls": "`set` 是无序的，如果你需要「既去重又保持原始顺序」，可以用 `list(dict.fromkeys(items))`（Python 3.7+ 字典保序特性）。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：实现待办事项管理器核心引擎（list + tuple）",
                "file_path": "src/day04_todo_manager.py",
                "narration": "咱们用 `list` 存所有待办，每条任务用不可变元组 `(task_id, title, is_done)` 表达。看看怎么优雅实现增删改查和统计。",
                "code": r'''"""
STARMIND-004 模块一：星辰智脑研发待办事项管理器（Todo CLI 引擎）。
演示 list 增删改查、tuple 不可变记录与解包、列表推导式过滤。
"""

from typing import List, Tuple

# 定义类型别名：单条任务为 (任务ID, 任务标题, 是否完成)
TaskRecord = Tuple[int, str, bool]


def add_task(tasks: List[TaskRecord], title: str) -> TaskRecord:
    """向任务列表末尾添加一条新待办，并返回新建的任务元组。"""
    cleaned = title.strip()
    if not cleaned:
        raise ValueError("任务标题不能为空")
    # 计算下一个自增 ID（即使中间删除过任务也不会冲突）
    next_id = max((t[0] for t in tasks), default=0) + 1
    record: TaskRecord = (next_id, cleaned, False)
    tasks.append(record)
    return record


def complete_task(tasks: List[TaskRecord], task_id: int) -> bool:
    """按任务 ID 将任务标记为已完成，成功返回 True，未找到返回 False。"""
    for idx, (tid, title, _done) in enumerate(tasks):
        if tid == task_id:
            # 元组不可变，因此构造新元组替换原位置元素
            tasks[idx] = (tid, title, True)
            return True
    return False


def remove_task(tasks: List[TaskRecord], task_id: int) -> bool:
    """安全删除指定 ID 的任务（避免遍历时原地 remove 引发错位）。"""
    original_len = len(tasks)
    # 使用切片赋值 tasks[:] 原地替换为推导式过滤后的新列表
    tasks[:] = [t for t in tasks if t[0] != task_id]
    return len(tasks) < original_len


def filter_tasks(tasks: List[TaskRecord], only_pending: bool = False) -> List[TaskRecord]:
    """根据完成状态筛选任务列表。"""
    if only_pending:
        return [t for t in tasks if not t[2]]
    return list(tasks)


def summarize_tasks(tasks: List[TaskRecord]) -> Tuple[int, int, int]:
    """返回只读统计快照：(总任务数, 已完成数, 待办数)。"""
    total = len(tasks)
    done_count = sum(1 for _, _, done in tasks if done)
    return (total, done_count, total - done_count)


if __name__ == "__main__":
    todo_list: List[TaskRecord] = []
    add_task(todo_list, "配置星辰智脑开发环境")
    add_task(todo_list, "完成客服文本清洗器")
    add_task(todo_list, "编写 Day 4 单元测试")
    complete_task(todo_list, 1)
    remove_task(todo_list, 2)

    total, done, pending = summarize_tasks(todo_list)
    print(f"任务概览 -> 总计:{total} | 已完成:{done} | 待办:{pending}")
    for tid, title, is_done in todo_list:
        mark = "[x]" if is_done else "[ ]"
        print(f"  {mark} #{tid} {title}")
''',
                "explanation": (
                    "1. `tasks[:] = [...]` 是切片原地替换技巧：既保留了外部传入列表对象的内存引用，又安全完成了批量过滤删除。\n"
                    "2. `max((t[0] for t in tasks), default=0) + 1` 确保哪怕删掉第 2 条任务再新增，ID 依然严格递增不会撞号。"
                ),
                "expected_output": (
                    "任务概览 -> 总计:2 | 已完成:1 | 待办:1\n"
                    "  [x] #1 配置星辰智脑开发环境\n"
                    "  [ ] #3 编写 Day 4 单元测试"
                )
            },
            {
                "step_title": "步骤二：实现知识库标签去重与差异分析器（set）",
                "file_path": "src/day04_tag_analyzer.py",
                "narration": "林产品还希望对比两版知识库文档的标签差异，看哪些是新增主题、哪些下线了。用 `set` 写出来干净得像数学公式。",
                "code": r'''"""
STARMIND-004 模块二：知识库文档标签去重与集合差异分析器。
演示 set 创建、去重清洗、交集(&)/并集(|)/差集(-)与排序输出。
"""

from typing import List, Dict, Set


def normalize_tags(raw_tags: List[str]) -> Set[str]:
    """清洗并去重标签：去首尾空格、转小写、过滤空串。"""
    # 使用集合推导式一步完成清洗与去重
    return {tag.strip().lower() for tag in raw_tags if tag and tag.strip()}


def compare_tag_versions(old_tags: List[str], new_tags: List[str]) -> Dict[str, List[str]]:
    """
    对比旧版与新版知识库标签，返回确定顺序（已排序）的差异报告：
    - common: 两版共同保留的标签
    - added: 新版新增的标签
    - removed: 新版移除的标签
    - all_unique: 两版合并后的全部唯一标签
    """
    set_old = normalize_tags(old_tags)
    set_new = normalize_tags(new_tags)

    return {
        "common": sorted(set_old & set_new),
        "added": sorted(set_new - set_old),
        "removed": sorted(set_old - set_new),
        "all_unique": sorted(set_old | set_new),
    }


if __name__ == "__main__":
    v1_tags = [" Python ", "Prompt", "git", "python", ""]
    v2_tags = ["python", "RAG", "Agent", "Prompt ", "RAG"]
    diff = compare_tag_versions(v1_tags, v2_tags)
    for k, v in diff.items():
        print(f"{k:12s}: {v}")
''',
                "explanation": (
                    "1. `{tag.strip().lower() for tag in raw_tags if tag and tag.strip()}` 是集合推导式，既洗掉了大小写不一致的 `'Python'` 和 `'python'`，又自动去重。\n"
                    "2. 输出前套一层 `sorted(...)`，因为 `set` 本身无序，排序转成 `list` 才能保证接口响应与单元测试断言结果每次完全一致。"
                ),
                "expected_output": (
                    "common      : ['prompt', 'python']\n"
                    "added       : ['agent', 'rag']\n"
                    "removed     : ['git']\n"
                    "all_unique  : ['agent', 'git', 'prompt', 'python', 'rag']"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-004 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day04_todo_manager import add_task, complete_task, remove_task, filter_tasks, summarize_tasks
from day04_tag_analyzer import normalize_tags, compare_tag_versions


def test_todo_crud_lifecycle():
    tasks = []
    t1 = add_task(tasks, "任务A")
    t2 = add_task(tasks, "任务B")
    assert t1 == (1, "任务A", False)
    assert t2 == (2, "任务B", False)

    assert complete_task(tasks, 1) is True
    assert complete_task(tasks, 999) is False
    assert summarize_tasks(tasks) == (2, 1, 1)
    assert len(filter_tasks(tasks, only_pending=True)) == 1

    assert remove_task(tasks, 1) is True
    assert remove_task(tasks, 1) is False
    assert summarize_tasks(tasks) == (1, 0, 1)

    with pytest.raises(ValueError):
        add_task(tasks, "   ")


def test_tag_analyzer():
    assert normalize_tags([" AI ", "ai", "", "LLM"]) == {"ai", "llm"}
    diff = compare_tag_versions(["Python", "Git"], ["python", "RAG"])
    assert diff["common"] == ["python"]
    assert diff["added"] == ["rag"]
    assert diff["removed"] == ["git"]
    assert diff["all_unique"] == ["git", "python", "rag"]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "用不可变 tuple 存单条任务记录、输出集合差异前用 sorted() 保证确定性，这两个工程细节非常稳。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "补充了空标题 ValueError 和重复删除返回 False 的断言，pytest 全绿。",
                "resolution": "验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：保序去重工具",
                "difficulty": "基础巩固",
                "requirement": "RAG 召回的文档 ID 列表如 `['doc3', 'doc1', 'doc3', 'doc2', 'doc1']`，要求去除重复 ID 但必须严格保持它们首次出现的先后顺序（因为顺序代表相关性排名）。编写 `dedupe_keep_order(items: list) -> list`。",
                "hint": "方法一：用辅助 `set` 记录已见元素；方法二：一行 `list(dict.fromkeys(items))`。",
                "solution_code": r'''"""Day 4 课后题 1：RAG 召回文档保序去重。"""

from typing import List


def dedupe_keep_order(items: List[str]) -> List[str]:
    """去除重复元素并严格保留首次出现的顺序。"""
    seen = set()
    result: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


if __name__ == "__main__":
    recalled = ["doc3", "doc1", "doc3", "doc2", "doc1"]
    print("保序去重结果:", dedupe_keep_order(recalled))
''',
                "solution_analysis": "经典高频面试题！用 `seen` 集合将判重降为 O(1)，整体时间复杂度 O(n)，比用 `if item not in result` 的 O(n²) 快得多。"
            },
            {
                "title": "企业实战：多模型权限交集校验器",
                "difficulty": "企业实战",
                "requirement": "员工拥有若干权限标签（如 `{'chat', 'rag', 'code'}`），某个 AI 工具需要一组必备权限（如 `{'rag', 'export'}`）。编写 `check_permissions(user_perms: set, required_perms: set) -> tuple[bool, list[str]]`，返回是否放行以及缺失的权限列表（已排序）。",
                "hint": "缺失权限就是集合差集 `required_perms - user_perms`。",
                "solution_code": r'''"""Day 4 课后题 2：AI 工具权限集合校验器。"""

from typing import Set, Tuple, List


def check_permissions(user_perms: Set[str], required_perms: Set[str]) -> Tuple[bool, List[str]]:
    """检查用户是否具备全部所需权限，返回 (是否通过, 缺失权限列表)。"""
    missing = sorted(required_perms - user_perms)
    return (len(missing) == 0, missing)


if __name__ == "__main__":
    print(check_permissions({"chat", "rag"}, {"rag", "export"}))
    print(check_permissions({"chat", "rag", "export"}, {"rag", "export"}))
''',
                "solution_analysis": "利用集合差集一行算出缺失权限，是企业 RBAC 权限系统中最常见的底层实现。"
            },
            {
                "title": "架构进阶：列表推导式实现滑动窗口切块",
                "difficulty": "架构进阶",
                "requirement": "后续做 RAG 文档切分时，常需要按固定窗口大小 `size` 和步长 `step` 对文本列表做滑动切片。编写 `sliding_window(items: list, size: int, step: int) -> list[tuple]`，返回所有完整窗口的元组列表。",
                "hint": "用 `range(0, len(items) - size + 1, step)` 生成起始索引，配合切片 `tuple(items[i:i+size])`。",
                "solution_code": r'''"""Day 4 课后题 3：滑动窗口切块器（RAG 分块原型）。"""

from typing import List, Tuple, Any


def sliding_window(items: List[Any], size: int, step: int = 1) -> List[Tuple[Any, ...]]:
    """按窗口大小与步长切分序列，返回不可变窗口元组列表。"""
    if size <= 0 or step <= 0 or size > len(items):
        return []
    return [tuple(items[i : i + size]) for i in range(0, len(items) - size + 1, step)]


if __name__ == "__main__":
    sentences = ["句1", "句2", "句3", "句4", "句5"]
    print("窗口=3, 步长=2:", sliding_window(sentences, size=3, step=2))
''',
                "solution_analysis": "这道题直接铺垫了第三阶段 RAG 的 Chunk Overlap（重叠分块）算法，用列表推导式 + 切片即可优雅实现。"
            }
        ],
        "extra_deep_dive": (
            "【避坑指南：浅拷贝与深拷贝的线上惨案】\n"
            "很多新人以为 `b = a` 复制了一个列表，结果改了 `b` 把 `a` 也改烂了——那只是多贴了个变量标签！\n"
            "即使写了 `b = a.copy()`，如果列表里套着子列表或字典（如对话历史 `messages`），浅拷贝依然共享内层对象，必须用 `copy.deepcopy(a)` 才能彻底隔离。"
        )
    },
]


DAYS_STAGE_1.extend([
    # =========================================================================
    # DAY 5: 核心数据结构(下)——字典与JSON重点日
    # =========================================================================
    {
        "day": 5,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "核心数据结构（下）——字典与 JSON 重点日",
        "subtitle": "吃透嵌套 dict 与 JSON 序列化，解析星辰智脑模拟大模型 API 完整响应",
        "gitlab_ticket": "STARMIND-005",
        "git_branch": "feat/day05-dict-json-api-parser",
        "git_commit": "feat(day05): 实现嵌套字典安全提取器与大模型JSON响应解析落盘工具",
        "prev_recap": "昨天咱们用 list、tuple、set 搞定了待办管理器和知识库标签去重，掌握了序列与集合容器。",
        "next_preview": "明天（Day 6）咱们学习函数封装（默认参数、*args/**kwargs、lambda、递归），把前面五天散落的脚本重构成高内聚的函数式架构。",
        "narrator_opening": (
            "今天是第一周含金量最高的一天——字典（dict）与 JSON！"
            "我不夸张地讲：在大模型应用开发里，你每天睁眼闭眼打交道的全是嵌套字典和 JSON。OpenAI、DeepSeek、通义千问的请求体是 JSON，返回体 `choices[0]['message']['content']` 还是多层嵌套 JSON！"
            "很多新手调 API 老是报 `KeyError` 或 `json.JSONDecodeError`，或者导出中文变成 `\\u661f\\u8fb0` 乱码。"
            "今天 STARMIND-005 咱们直接拿一份真实的 OpenAI/DeepSeek 兼容格式模拟返回 JSON 来解剖，手写安全提取器与 UTF-8 落盘工具，彻底打通 JSON 任督二脉。"
        ),
        "narrator_closing": (
            "今天把嵌套 dict 和 `json.loads / dumps / load / dump` 摸透后，你以后看到任何第三方大模型 API 文档都不会发怵了。"
            "临走前再默念一遍两个保命参数：`dict.get(key, default)` 防 KeyError，`json.dumps(..., ensure_ascii=False, indent=2)` 防中文变 Unicode 转义码！"
        ),
        "business_prd": {
            "background": "星辰智脑即将对接 DeepSeek 与通义千问 API，研发团队需要先构建健壮的 JSON 响应解析与审计落盘层，防止上游字段缺失导致服务崩溃。",
            "pain_points": [
                "直接用 `resp['choices'][0]['message']['content']` 硬取值，一旦接口限流或返回异常结构立刻触发 KeyError/IndexError。",
                "默认 `json.dumps()` 会把中文转义成 `\\uXXXX`，运维看日志极度痛苦。",
                "缺少统计单次请求 prompt_tokens、completion_tokens 与费用的结构化汇总。"
            ],
            "goals": [
                "熟练掌握 dict 增删改查、`.get()`、`.items()`、字典推导式与多层嵌套解析。",
                "精通 `json.loads`、`json.dumps`、`json.load`、`json.dump` 四大方法及 `ensure_ascii=False`。",
                "实现对模拟大模型 API JSON 响应的安全提取、费用计算与本地文件持久化。"
            ],
            "acceptance_criteria": [
                "能从标准 OpenAI 兼容 JSON 响应中准确提取回复文本、模型名、结束原因与 Token 用量。",
                "面对缺失字段或非法 JSON 字符串时返回兜底错误结构而不抛出未捕获异常。",
                "能将解析后的审计记录以可读中文 JSON 写入文件并无损读回，pytest 全绿。"
            ],
            "non_functional": [
                "所有文件读写显式指定 `encoding='utf-8'`。",
                "单测使用临时目录 `tmp_path` 验证文件读写，不污染源码仓库。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "字典底层哈希原理与嵌套结构安全访问", "detail": "精讲 dict CRUD、get/setdefault、字典推导式与深层路径安全取值函数。"},
            {"slot": "下午 14:00-17:30", "topic": "JSON 四件套与模拟大模型 API 响应解析", "detail": "解剖标准 Chat Completions JSON，编写解析器与审计日志落盘模块。"},
            {"slot": "晚间 19:00-20:30", "topic": "异常 JSON 与残缺字段容错测试", "detail": "使用 pytest + tmp_path 验证正常响应、缺字段响应与损坏 JSON 的处理逻辑。"},
            {"slot": "复盘 20:30-21:00", "topic": "JSON 与 dict 类型映射对照复盘", "detail": "整理 Python 与 JSON 类型对应表（None/null, True/true, tuple/array），完成 3 道课后题。"}
        ],
        "architecture_design": (
            "企业级 AI 网关的响应处理层必须具备「防御性反序列化」能力：\n"
            "1. **通用安全路径提取器**（day05_dict_utils.py）：封装 `safe_get_path(data, path, default)`，支持按点号和下标（如 `'choices.0.message.content'`）安全穿透多层嵌套 dict/list，任何一层缺失都优雅返回默认值。\n"
            "2. **LLM JSON 协议解析与持久化层**（day05_json_api_parser.py）：将字符串反序列化（`json.loads`）、核心业务字段抽取、Token 费用归档以及本地审计落盘（`json.dump` / `json.load`）封装为独立函数，确保上游接口轻微变动时业务主流程不崩溃。"
        ),
        "diagrams": [
            {
                "title": "大模型 API JSON 响应解析与落盘流程图",
                "kind": "flowchart",
                "caption": "展示原始 HTTP 响应体经过 JSON 反序列化、安全路径提取、用量汇总到 UTF-8 落盘的全过程。",
                "nodes": [
                    {"id": "n1", "label": "原始 JSON 字符串", "sub": "模拟 DeepSeek/Qwen 返回", "color": "#3b82f6"},
                    {"id": "n2", "label": "json.loads 解析", "sub": "捕获 JSONDecodeError", "color": "#8b5cf6"},
                    {"id": "n3", "label": "safe_get_path 取值", "sub": "穿透 choices[0].message", "color": "#f59e0b"},
                    {"id": "n4", "label": "组装审计字典", "sub": "reply/model/usage/cost", "color": "#10b981"},
                    {"id": "n5", "label": "json.dump 持久化", "sub": "UTF-8 + ensure_ascii=False", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "反序列化"},
                    {"from": "n2", "to": "n3", "label": "Python dict"},
                    {"from": "n3", "to": "n4", "label": "防 KeyError"},
                    {"from": "n4", "to": "n5", "label": "写入磁盘"}
                ]
            },
            {
                "title": "星辰智脑 JSON 协议适配层架构图",
                "kind": "architecture",
                "caption": "通过统一响应适配层，将不同厂商略有差异的嵌套 JSON 映射为星辰智脑内部标准字典。",
                "nodes": [
                    {"id": "a1", "label": "上游模拟响应", "sub": "OpenAI/DeepSeek 协议", "color": "#64748b"},
                    {"id": "a2", "label": "DictUtils 安全取值层", "sub": "safe_get_path / 合并", "color": "#3b82f6"},
                    {"id": "a3", "label": "ApiParser 解析层", "sub": "结构化提取 + 容错", "color": "#8b5cf6"},
                    {"id": "a4", "label": "JSON 审计存储", "sub": "本地 .json 文件读写", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "a1", "to": "a3", "label": "原始 JSON"},
                    {"from": "a3", "to": "a2", "label": "安全路径查询"},
                    {"from": "a3", "to": "a4", "label": "dump/load"}
                ]
            },
            {
                "title": "Python dict 与 JSON 双向序列化原理图",
                "kind": "schematic",
                "caption": "清晰区分内存字符串互转（loads/dumps）与文件句柄互转（load/dump）四个函数的适用场景。",
                "nodes": [
                    {"id": "s1", "label": "Python dict 对象", "sub": "内存哈希表 (True/None)", "color": "#3b82f6"},
                    {"id": "s2", "label": "JSON 字符串 str", "sub": "网络传输文本 (true/null)", "color": "#10b981"},
                    {"id": "s3", "label": "磁盘 .json 文件", "sub": "UTF-8 持久化存储", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "json.dumps()"},
                    {"from": "s2", "to": "s1", "label": "json.loads()"},
                    {"from": "s1", "to": "s3", "label": "json.dump(obj, f)"},
                    {"from": "s3", "to": "s1", "label": "json.load(f)"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 字典核心操作与 O(1) 查找",
                "content": (
                    "字典存储键值对 `{key: value}`，键必须是不可变可哈希对象（如 `str`、`int`、`tuple`）。"
                    "Python 3.7+ 保证字典按插入顺序遍历。高频方法：`.get(k, default)` 安全取值、`.items()` 遍历键值、`|` 合并两个字典（Python 3.9+：`merged = base | override`）。"
                ),
                "pitfalls": "永远不要在不确定键是否存在时直接 `d['content']`，线上接口少返回一个可选字段就会直接触发 `KeyError` 导致 500 报错！"
            },
            {
                "heading": "2. JSON 四大函数口诀：带 s 管字符串，不带 s 管文件",
                "content": (
                    "- `json.loads(s)`：JSON 字符串 -> Python dict/list\n"
                    "- `json.dumps(obj, ensure_ascii=False, indent=2)`：Python 对象 -> 美化后的中文 JSON 字符串\n"
                    "- `json.load(fp)`：从打开的文件对象读取并解析为 Python 对象\n"
                    "- `json.dump(obj, fp, ensure_ascii=False, indent=2)`：将 Python 对象写入文件"
                ),
                "pitfalls": "JSON 标准规定：1）键和字符串必须用**双引号**（单引号非法）；2）末尾不能有多余逗号；3）布尔值小写 `true/false`，空值是 `null`；4）JSON 不支持 `set` 类型，序列化前要先转 `list`。"
            },
            {
                "heading": "3. 真实大模型 Chat Completions 响应解剖",
                "content": (
                    "国内主流模型（DeepSeek、通义千问 DashScope 兼容模式、智谱 GLM）均遵循 OpenAI 响应格式："
                    "`{'id': '...', 'model': 'deepseek-chat', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': '...'}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 20, 'completion_tokens': 50, 'total_tokens': 70}}`。"
                ),
                "pitfalls": "注意 `choices` 是一个列表（即使通常只有 1 项），取回复正文要先判断 `choices` 非空，再取 `choices[0]`。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：编写嵌套字典安全路径提取与配置合并工具",
                "file_path": "src/day05_dict_utils.py",
                "narration": "先造一把趁手的瑞士军刀 `safe_get_path`，以后面对 5 层嵌套的大模型 JSON，一行代码安全取到底，再也不怕 KeyError 和 IndexError。",
                "code": r'''"""
STARMIND-005 模块一：嵌套字典安全提取与配置合并工具。
演示 dict 操作、isinstance 类型判断、嵌套 list/dict 穿透与 Python 3.9+ 字典合并运算符 |。
"""

from typing import Any, Dict


def safe_get_path(data: Any, path: str, default: Any = None) -> Any:
    """
    通过点分隔路径安全访问多层嵌套的 dict 或 list。
    示例：safe_get_path(resp, "choices.0.message.content", "")
    """
    current = data
    for segment in path.split("."):
        if isinstance(current, dict):
            if segment in current:
                current = current[segment]
            else:
                return default
        elif isinstance(current, list):
            # 列表路径段必须是合法非负整数索引
            if segment.isdigit():
                idx = int(segment)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    return default
            else:
                return default
        else:
            return default
    return current


def merge_model_config(base_cfg: Dict[str, Any], user_override: Dict[str, Any]) -> Dict[str, Any]:
    """合并默认模型参数与用户覆盖参数，不修改原始字典，并过滤掉 None 值。"""
    # 使用字典推导式剔除用户传入的 None，避免覆盖掉有效默认值
    valid_override = {k: v for k, v in user_override.items() if v is not None}
    # Python 3.9+ 字典合并运算符 | 返回全新字典
    return base_cfg | valid_override


if __name__ == "__main__":
    sample = {"choices": [{"message": {"role": "assistant", "content": "你好，我是星辰智脑！"}}]}
    print("提取正文:", safe_get_path(sample, "choices.0.message.content", "默认回复"))
    print("缺失路径:", safe_get_path(sample, "choices.1.message.content", "未命中"))

    default_cfg = {"model": "deepseek-chat", "temperature": 0.7, "max_tokens": 1024}
    final_cfg = merge_model_config(default_cfg, {"temperature": 0.2, "max_tokens": None})
    print("合并配置:", final_cfg)
''',
                "explanation": (
                    "1. `safe_get_path` 同时兼容 `dict` 键查找和 `list` 数字索引，彻底告别冗长的 `if 'choices' in d and len(d['choices']) > 0 ...`。\n"
                    "2. `base_cfg | valid_override` 生成新字典，不会意外篡改全局默认配置 `default_cfg`。"
                ),
                "expected_output": (
                    "提取正文: 你好，我是星辰智脑！\n"
                    "缺失路径: 未命中\n"
                    "合并配置: {'model': 'deepseek-chat', 'temperature': 0.2, 'max_tokens': 1024}"
                )
            },
            {
                "step_title": "步骤二：实现大模型 API JSON 响应解析器与本地审计落盘",
                "file_path": "src/day05_json_api_parser.py",
                "narration": "现在拿一份标准 OpenAI/DeepSeek 兼容的模拟 JSON 响应，演示 `json.loads / dumps / load / dump` 全流程，并计算单次调用成本。",
                "code": r'''"""
STARMIND-005 模块二：模拟大模型 API JSON 响应解析与审计落盘工具。
演示 json.loads、json.dumps、json.load、json.dump 及 UTF-8 中文无转义持久化。
"""

import json
from pathlib import Path
from typing import Dict, Any

from day05_dict_utils import safe_get_path

# 模拟一条真实的 DeepSeek / 通义千问兼容格式 API JSON 响应
MOCK_API_RESPONSE_JSON = json.dumps(
    {
        "id": "chatcmpl-starmind-005",
        "object": "chat.completion",
        "model": "deepseek-chat",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "您好！您的订单 ORD-20260505 已由顺丰揽收，预计明日送达杭州滨江区。",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 128,
            "completion_tokens": 42,
            "total_tokens": 170,
        },
    },
    ensure_ascii=False,
)


def parse_llm_response(raw_json: str) -> Dict[str, Any]:
    """解析大模型原始 JSON 响应字符串，返回星辰智脑内部标准结果字典。"""
    try:
        payload = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"JSON 解析失败: {exc.msg}",
            "reply": "",
            "total_tokens": 0,
        }

    # 如果上游返回了错误对象（如限流或鉴权失败）
    if isinstance(payload, dict) and "error" in payload:
        return {
            "ok": False,
            "error": str(safe_get_path(payload, "error.message", payload["error"])),
            "reply": "",
            "total_tokens": 0,
        }

    reply_text = safe_get_path(payload, "choices.0.message.content", "")
    model_name = safe_get_path(payload, "model", "unknown-model")
    finish_reason = safe_get_path(payload, "choices.0.finish_reason", "unknown")
    prompt_tokens = int(safe_get_path(payload, "usage.prompt_tokens", 0))
    completion_tokens = int(safe_get_path(payload, "usage.completion_tokens", 0))
    total_tokens = int(safe_get_path(payload, "usage.total_tokens", prompt_tokens + completion_tokens))

    return {
        "ok": bool(reply_text),
        "request_id": safe_get_path(payload, "id", "N/A"),
        "model": model_name,
        "reply": reply_text,
        "finish_reason": finish_reason,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def save_audit_record(record: Dict[str, Any], file_path: Path) -> Path:
    """将结构化解析结果以可读中文 JSON 写入磁盘文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return file_path


def load_audit_record(file_path: Path) -> Dict[str, Any]:
    """从磁盘 JSON 文件无损读回审计记录。"""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    parsed = parse_llm_response(MOCK_API_RESPONSE_JSON)
    # 使用 json.dumps 格式化打印，ensure_ascii=False 确保中文直接显示
    print(json.dumps(parsed, ensure_ascii=False, indent=2))
''',
                "explanation": (
                    "1. `parse_llm_response` 同时处理了三种真实生产场景：合法响应、上游返回 `{\"error\": ...}` 业务错、以及网关超时截断导致的非法 JSON。\n"
                    "2. `file_path.parent.mkdir(parents=True, exist_ok=True)` 确保父目录不存在时自动创建，避免 `FileNotFoundError`。"
                ),
                "expected_output": (
                    '{\n'
                    '  "ok": true,\n'
                    '  "request_id": "chatcmpl-starmind-005",\n'
                    '  "model": "deepseek-chat",\n'
                    '  "reply": "您好！您的订单 ORD-20260505 已由顺丰揽收，预计明日送达杭州滨江区。",\n'
                    '  "finish_reason": "stop",\n'
                    '  "prompt_tokens": 128,\n'
                    '  "completion_tokens": 42,\n'
                    '  "total_tokens": 170\n'
                    '}'
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-005 自动化单元测试。"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day05_dict_utils import safe_get_path, merge_model_config
from day05_json_api_parser import (
    MOCK_API_RESPONSE_JSON,
    parse_llm_response,
    save_audit_record,
    load_audit_record,
)


def test_safe_get_path_and_merge():
    data = {"a": [{"b": "ok"}]}
    assert safe_get_path(data, "a.0.b") == "ok"
    assert safe_get_path(data, "a.5.b", "fallback") == "fallback"
    assert safe_get_path(data, "x.y", None) is None

    merged = merge_model_config({"temp": 0.7, "top_p": 0.9}, {"temp": 0.1, "top_p": None})
    assert merged == {"temp": 0.1, "top_p": 0.9}


def test_parse_llm_response_variants():
    ok_res = parse_llm_response(MOCK_API_RESPONSE_JSON)
    assert ok_res["ok"] is True
    assert ok_res["total_tokens"] == 170
    assert "顺丰" in ok_res["reply"]

    bad_res = parse_llm_response("{not valid json")
    assert bad_res["ok"] is False
    assert "JSON 解析失败" in bad_res["error"]

    err_res = parse_llm_response(json.dumps({"error": {"message": "rate limit exceeded"}}))
    assert err_res["ok"] is False
    assert "rate limit" in err_res["error"]


def test_json_save_and_load_roundtrip(tmp_path: Path):
    record = parse_llm_response(MOCK_API_RESPONSE_JSON)
    target = tmp_path / "logs" / "audit.json"
    save_audit_record(record, target)
    raw_text = target.read_text(encoding="utf-8")
    assert "顺丰" in raw_text  # 确保未转义为 \\uXXXX
    reloaded = load_audit_record(target)
    assert reloaded == record
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "`safe_get_path` 写得很克制清晰，处理上游 `error` 字段和 `JSONDecodeError` 也到位。单测用 `tmp_path` 不污染仓库点赞。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "已确认落盘后的 JSON 文件直接可读中文（无 \\u 转义），异常 JSON 也不会抛崩溃。",
                "resolution": "QA 验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：词频统计字典构建器",
                "difficulty": "基础巩固",
                "requirement": "给定一组客服工单意图标签列表 `['物流', '退款', '物流', '发票', '物流', '退款']`，编写 `count_intents(labels: list[str]) -> dict[str, int]`，统计每个意图出现次数并按频次从高到低排序返回字典。",
                "hint": "用 `counts[label] = counts.get(label, 0) + 1` 累计，再用 `sorted(counts.items(), key=lambda x: x[1], reverse=True)` 排序。",
                "solution_code": r'''"""Day 5 课后题 1：工单意图频次统计器。"""

from typing import List, Dict


def count_intents(labels: List[str]) -> Dict[str, int]:
    """统计每个意图标签出现次数，并按频次降序返回字典。"""
    counts: Dict[str, int] = {}
    for label in labels:
        counts[label] = counts.get(label, 0) + 1
    # 按值降序排列，Python 3.7+ 字典保留插入顺序
    sorted_pairs = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return dict(sorted_pairs)


if __name__ == "__main__":
    sample = ["物流", "退款", "物流", "发票", "物流", "退款"]
    print("意图统计:", count_intents(sample))
''',
                "solution_analysis": "考查 `dict.get(k, 0) + 1` 经典计数范式与按 value 排序技巧。"
            },
            {
                "title": "企业实战：多模型账单按部门分组汇总",
                "difficulty": "企业实战",
                "requirement": "输入一组 API 调用记录列表（每条含 `dept` 和 `tokens`），编写 `aggregate_by_dept(records: list[dict]) -> dict[str, int]`，汇总各部门总 Token 消耗并输出美化 JSON。",
                "hint": "遍历列表，使用 `totals[dept] = totals.get(dept, 0) + tokens`。",
                "solution_code": r'''"""Day 5 课后题 2：按部门汇总大模型 Token 消耗账单。"""

import json
from typing import List, Dict, Any


def aggregate_by_dept(records: List[Dict[str, Any]]) -> Dict[str, int]:
    """按部门分组累加 Token 用量。"""
    totals: Dict[str, int] = {}
    for rec in records:
        dept = str(rec.get("dept", "未知部门"))
        tokens = int(rec.get("tokens", 0))
        totals[dept] = totals.get(dept, 0) + tokens
    return totals


if __name__ == "__main__":
    logs = [
        {"dept": "客服部", "tokens": 1200},
        {"dept": "研发部", "tokens": 3500},
        {"dept": "客服部", "tokens": 800},
    ]
    print(json.dumps(aggregate_by_dept(logs), ensure_ascii=False, indent=2))
''',
                "solution_analysis": "企业计费与成本分摊（FinOps）的基础聚合模型，注意缺失字段兜底默认值。"
            },
            {
                "title": "架构进阶：JSON Schema 必填字段校验器",
                "difficulty": "架构进阶",
                "requirement": "大模型输出结构化 JSON 时偶尔会漏掉关键字段。编写 `validate_payload(payload: dict, required_types: dict[str, type]) -> tuple[bool, list[str]]`，检查字典是否包含所有必填键且值类型符合预期，返回 `(是否通过, 错误明细列表)`。",
                "hint": "遍历 `required_types.items()`，先查 `key not in payload`，再查 `not isinstance(payload[key], expected_type)`。",
                "solution_code": r'''"""Day 5 课后题 3：轻量级 JSON 响应结构校验器。"""

from typing import Dict, Any, Tuple, List, Type


def validate_payload(
    payload: Dict[str, Any], required_types: Dict[str, Type[Any]]
) -> Tuple[bool, List[str]]:
    """校验字典是否包含全部必填字段且满足类型要求。"""
    errors: List[str] = []
    for field, expected_type in required_types.items():
        if field not in payload:
            errors.append(f"缺少必填字段: {field}")
        elif not isinstance(payload[field], expected_type):
            actual = type(payload[field]).__name__
            errors.append(f"字段 {field} 类型错误: 期望 {expected_type.__name__}, 实际 {actual}")
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    schema = {"intent": str, "confidence": float, "need_human": bool}
    print("合法:", validate_payload({"intent": "退款", "confidence": 0.95, "need_human": False}, schema))
    print("异常:", validate_payload({"intent": "退款", "confidence": "高"}, schema))
''',
                "solution_analysis": "这就是 Day 23 Pydantic 数据校验库最核心的底层设计思想：把运行时弱类型字典转化为强契约校验。"
            }
        ],
        "extra_deep_dive": (
            "【实战经验：大模型返回的 JSON 包在 ```json ... ``` Markdown 代码块里怎么办？】\n"
            "生产环境里，即使你在 Prompt 里写死了「只返回纯 JSON」，不少模型依然喜欢贴心地在外面包一层 ```` ```json\\n{...}\\n``` ````，直接喂给 `json.loads()` 必炸！\n"
            "老陈的通用预处理三板斧：先 `strip()`，若以 ```` ``` ```` 开头则去掉首尾围栏行，再截取第一个 `{` 到最后一个 `}` 之间的子串送去 `json.loads()`，成功率立刻从 85% 飙到 99.5%。"
        )
    },

    # =========================================================================
    # DAY 6: 函数
    # =========================================================================
    {
        "day": 6,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "函数",
        "subtitle": "精通参数解包、lambda 与递归，将星辰智脑预处理脚本重构为高内聚函数式管道",
        "gitlab_ticket": "STARMIND-006",
        "git_branch": "feat/day06-functions-refactor",
        "git_commit": "feat(day06): 引入函数式管道、*args/**kwargs动态配置与递归树形目录解析",
        "prev_recap": "昨天咱们攻克了嵌套字典和 JSON 序列化，已经能安全解析模拟大模型 API 返回的响应并落盘。",
        "next_preview": "明天（Day 7）是第一周复习与周测日！咱们会把 Day 1~6 所有核心知识串成一张网，完成周测并独立交付「星辰企业通讯录管理系统 + JSON 持久化」。",
        "narrator_opening": (
            "前五天咱们写了不少实用片段，但你有没有发现：代码里重复逻辑开始变多了，参数一多就容易传错顺序？"
            "今天 STARMIND-006 咱们把「函数」彻底吃透：位置参数、关键字参数、默认参数、`*args`、`**kwargs`、`lambda` 匿名函数以及递归。"
            "大厂写 AI 工具箱最讲究「函数式管道（Pipeline）」——把清洗、截断、脱敏做成可插拔的小函数，像乐高一样自由组合！"
            "另外顺手用递归解决林产品提的一个真实需求：遍历星辰知识库多层嵌套文件夹 JSON 树，统计所有文档数量与路径。"
        ),
        "narrator_closing": (
            "写完今天的函数式管道，回头再看 Day 2 的代码是不是觉得清爽了一大截？"
            "牢记今天最大的坑：**永远不要用可变对象（如 `[]` 或 `{}`）作为函数默认参数**！记住用 `None` 占位再在函数体内初始化。"
            "明天周测实战，今晚好好复盘一下前六天的知识点。"
        ),
        "business_prd": {
            "background": "星辰智脑的文本预处理步骤越来越多（去噪、脱敏、截断、加前缀），硬编码串行调用难以按业务线灵活编排；同时知识库目录支持无限层级嵌套，需要递归统计文档清单。",
            "pain_points": [
                "不同业务线需要的文本处理步骤不同，复制粘贴代码导致维护成本飙升。",
                "大模型调用参数繁多（temperature/top_p/stop 等），函数签名写死后极难扩展。",
                "知识库文件夹树深度不固定，普通单层 for 循环无法遍历任意深度。"
            ],
            "goals": [
                "掌握位置/关键字/默认参数以及 `*args`、`**kwargs` 的透传封装模式。",
                "熟练使用 `lambda` 配合 `sorted` / `filter` / `map` 完成数据排序与管道组合。",
                "理解递归的终止条件与分解思路，安全遍历嵌套树形结构。"
            ],
            "acceptance_criteria": [
                "实现 `run_pipeline(text, *processors)`，支持按顺序动态组合任意数量的文本处理函数。",
                "实现 `build_chat_request(model, *messages, **extra_params)`，灵活组装 API 请求体。",
                "实现递归函数 `flatten_kb_tree(node)`，提取任意深度知识库树中的所有文档路径。"
            ],
            "non_functional": [
                "严禁使用可变默认参数（`items=[]`），统一采用 `None` 哨兵模式。",
                "递归函数具备深度保护或清晰终止条件，防止栈溢出。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "函数参数体系与可变默认参数避坑", "detail": "精讲位置/关键字/默认参数、*args/**kwargs 解包、LEGB 作用域规则。"},
            {"slot": "下午 14:00-17:30", "topic": "高阶函数、lambda 排序与递归树遍历实战", "detail": "重构星辰智脑文本管道引擎，编写知识库嵌套目录递归扁平化工具。"},
            {"slot": "晚间 19:00-20:30", "topic": "单元测试与多场景组合验证", "detail": "使用 pytest 测试空管道、动态 kwargs 覆盖与 4 层嵌套目录递归。"},
            {"slot": "复盘 20:30-21:00", "topic": "函数设计单一职责复盘与课后题", "detail": "检查函数长度与职责边界，完成 3 道梯度课后作业。"}
        ],
        "architecture_design": (
            "今天我们在代码架构上迈出一大步，引入了两个在 LangChain / FastAPI 源码中随处可见的设计模式：\n"
            "1. **可组合函数管道模式（day06_text_pipeline.py）**：利用 Python 中「函数是一等公民（First-class Citizen）」的特性，通过 `*processors` 接收任意多个单入单出的处理函数，按顺序接力执行，类似 Linux 管道 `cat | grep | sed`。\n"
            "2. **递归分治树解析模式（day06_kb_tree.py）**：知识库目录节点天然是自相似结构（文件夹内可以包含文件和子文件夹）。递归函数只需处理「当前节点是文件（基准情况）」和「当前节点是文件夹（递归展开子节点）」两种情况，十行代码搞定任意层级。"
        ),
        "diagrams": [
            {
                "title": "函数式文本处理管道执行流程图",
                "kind": "flowchart",
                "caption": "展示文本依次穿过多个可插拔纯函数处理器（*processors）的接力变换过程。",
                "nodes": [
                    {"id": "n1", "label": "原始文本输入", "sub": "str 输入", "color": "#3b82f6"},
                    {"id": "n2", "label": "处理器 1", "sub": "clean_spaces()", "color": "#8b5cf6"},
                    {"id": "n3", "label": "处理器 2", "sub": "mask_sensitive()", "color": "#f59e0b"},
                    {"id": "n4", "label": "处理器 3", "sub": "lambda 截断", "color": "#06b6d4"},
                    {"id": "n5", "label": "最终洁净输出", "sub": "交付下游模型", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "step 1"},
                    {"from": "n2", "to": "n3", "label": "step 2"},
                    {"from": "n3", "to": "n4", "label": "step 3"},
                    {"from": "n4", "to": "n5", "label": "return"}
                ]
            },
            {
                "title": "动态请求构建与管道模块架构图",
                "kind": "architecture",
                "caption": "展示 *args/**kwargs 请求构造器、函数管道与递归树解析器在平台中的协作。",
                "nodes": [
                    {"id": "a1", "label": "业务调用方", "sub": "客服/研发/知识库", "color": "#64748b"},
                    {"id": "a2", "label": "TextPipeline", "sub": "*processors 自由编排", "color": "#3b82f6"},
                    {"id": "a3", "label": "RequestBuilder", "sub": "*messages + **kwargs", "color": "#8b5cf6"},
                    {"id": "a4", "label": "KBTreeWalker", "sub": "递归扁平化 + lambda排序", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "注册清洗步骤"},
                    {"from": "a2", "to": "a3", "label": "组装 API Payload"},
                    {"from": "a1", "to": "a4", "label": "扫描知识库目录"}
                ]
            },
            {
                "title": "递归调用栈展开与回溯原理示意图",
                "kind": "schematic",
                "caption": "展示递归遍历「根目录 -> 子目录 -> 文档叶节点」时函数调用栈的压栈与结果汇总。",
                "nodes": [
                    {"id": "s1", "label": "flatten(root)", "sub": "深度 0：展开 children", "color": "#3b82f6"},
                    {"id": "s2", "label": "flatten(研发规范)", "sub": "深度 1：继续递归", "color": "#8b5cf6"},
                    {"id": "s3", "label": "叶节点: git.md", "sub": "命中基准条件直接返回", "color": "#10b981"},
                    {"id": "s4", "label": "叶节点: faq.md", "sub": "命中基准条件直接返回", "color": "#10b981"},
                    {"id": "s5", "label": "汇总扁平路径列表", "sub": "逐层回溯合并", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "压栈"},
                    {"from": "s2", "to": "s3", "label": "基准返回"},
                    {"from": "s1", "to": "s4", "label": "基准返回"},
                    {"from": "s3", "to": "s5", "label": "回溯汇总"},
                    {"from": "s4", "to": "s5", "label": "回溯汇总"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 参数顺序与 *args / **kwargs 解包",
                "content": (
                    "函数参数严格遵循顺序：`位置参数 -> 默认参数 -> *args -> 仅关键字参数 -> **kwargs`。"
                    "`*args` 把多余位置参数打包成 `tuple`，`**kwargs` 把多余关键字参数打包成 `dict`——在封装大模型 SDK 客户端时，用 `**kwargs` 透传可选超参（`temperature`, `top_p`, `seed`）是最标准写法。"
                ),
                "pitfalls": "致命经典坑：`def add_msg(msg, history=[]):` 中默认列表在函数定义时只创建一次，多次调用会互相污染！正确写法：`def add_msg(msg, history=None): history = [] if history is None else history`。"
            },
            {
                "heading": "2. lambda 匿名函数与高阶排序",
                "content": (
                    "`lambda 参数: 表达式` 适合写简短的一次性逻辑，最常用于 `sorted(docs, key=lambda d: d['score'], reverse=True)`。"
                    "如果逻辑超过一行或需要复用，老陈强烈建议用 `def` 定义具名函数并写上 docstring。"
                ),
                "pitfalls": "在循环里创建 lambda 容易踩「闭包延迟绑定」的坑：`[lambda: i for i in range(3)]` 三个函数调用结果全是 2，需要写成 `lambda i=i: i` 绑定当前值。"
            },
            {
                "heading": "3. 递归两要素：基准条件与缩小问题规模",
                "content": (
                    "写递归前先写 `if 到达叶子/边界: return ...`（Base Case），再调用自身处理更小规模的子问题。"
                    "Python 默认最大递归深度为 1000（`sys.getrecursionlimit()`），适合目录树、JSON 树、语法树遍历，不适合百万级线性链表。"
                ),
                "pitfalls": "漏写基准条件或递归参数没有向边界收敛，会触发 `RecursionError: maximum recursion depth exceeded`。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：构建函数式文本管道与动态请求组装器",
                "file_path": "src/day06_text_pipeline.py",
                "narration": "咱们把前几天零散的文本清洗步骤重构为高内聚的函数管道，并用 `*args` / `**kwargs` 写出灵活的 Chat API 请求构造器。",
                "code": r'''"""
STARMIND-006 模块一：函数式文本处理管道与动态 API 请求构造器。
演示默认参数避坑（None 哨兵）、*args 管道组合、**kwargs 参数透传与 lambda 处理器。
"""

from typing import Callable, Dict, Any, List, Optional


def strip_and_collapse(text: str) -> str:
    """处理器 1：去除首尾空白并折叠连续空格与换行。"""
    return " ".join(text.replace("\u3000", " ").split())


def redact_secret_key(text: str) -> str:
    """处理器 2：对意外粘贴进提问中的 sk- 密钥片段做简单遮蔽。"""
    tokens = text.split(" ")
    safe_tokens = ["sk-***REDACTED***" if t.startswith("sk-") else t for t in tokens]
    return " ".join(safe_tokens)


def run_pipeline(text: str, *processors: Callable[[str], str]) -> str:
    """
    函数式管道调度器：将输入文本依次送入 *processors 中的每个函数处理。
    支持传入具名函数或 lambda 匿名函数。
    """
    result = text
    for fn in processors:
        result = fn(result)
    return result


def build_chat_request(
    model: str,
    *user_messages: str,
    system_prompt: Optional[str] = None,
    **extra_params: Any,
) -> Dict[str, Any]:
    """
    动态构建大模型 Chat Completions 请求体。
    - *user_messages 接收一条或多条用户消息
    - **extra_params 透传 temperature、max_tokens 等可选超参
    """
    # 安全初始化可变列表（绝不用 messages=[] 作为默认参数）
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for msg in user_messages:
        messages.append({"role": "user", "content": msg})

    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    # 过滤掉值为 None 的额外超参后合并
    for key, value in extra_params.items():
        if value is not None:
            payload[key] = value
    return payload


if __name__ == "__main__":
    raw = "  帮我查下  sk-secret123456  为什么报 401 错误？ \n "
    # 自由组合两个具名处理器 + 一个 lambda 截断处理器
    cleaned = run_pipeline(
        raw,
        strip_and_collapse,
        redact_secret_key,
        lambda s: s[:40],
    )
    req = build_chat_request(
        "deepseek-chat",
        cleaned,
        system_prompt="你是星辰智脑运维助手",
        temperature=0.2,
        max_tokens=512,
    )
    print("清洗结果:", cleaned)
    print("请求体  :", req)
''',
                "explanation": (
                    "1. `run_pipeline` 的 `*processors` 允许调用方随心所欲增减步骤，甚至临时传一个 `lambda s: s[:40]` 做截断，完全符合开闭原则。\n"
                    "2. `build_chat_request` 展示了一个非常标准的 SDK 函数签名设计：必填 `model` 放前面，变长 `*user_messages` 居中，仅关键字参数 `system_prompt` 与 `**extra_params` 殿后。"
                ),
                "expected_output": (
                    "清洗结果: 帮我查下 sk-***REDACTED*** 为什么报 401 错误？\n"
                    "请求体  : {'model': 'deepseek-chat', 'messages': [{'role': 'system', 'content': '你是星辰智脑运维助手'}, {'role': 'user', 'content': '帮我查下 sk-***REDACTED*** 为什么报 401 错误？'}], 'temperature': 0.2, 'max_tokens': 512}"
                )
            },
            {
                "step_title": "步骤二：使用递归与 lambda 排序遍历知识库嵌套目录树",
                "file_path": "src/day06_kb_tree.py",
                "narration": "现在用递归解决星辰知识库多层目录统计问题，并用 `lambda` 按文档大小降序找出体积最大的 Top-N 文档。",
                "code": r'''"""
STARMIND-006 模块二：知识库嵌套目录树递归解析与 Top-N 排序器。
演示递归函数（基准条件 + 递归分解）、lambda 排序与深度安全控制。
"""

from typing import Dict, Any, List


def flatten_kb_tree(
    node: Dict[str, Any],
    prefix: str = "",
    max_depth: int = 20,
) -> List[Dict[str, Any]]:
    """
    递归遍历知识库嵌套目录树，提取所有文件节点及其完整逻辑路径。
    每个节点格式：
      - 文件: {"type": "file", "name": "faq.md", "size_kb": 12}
      - 目录: {"type": "dir", "name": "客服部", "children": [...]}
    """
    if max_depth < 0:
        raise RecursionError("知识库目录嵌套层级超过安全上限")

    name = str(node.get("name", ""))
    current_path = f"{prefix}/{name}" if prefix else name

    # 基准条件（Base Case）：到达文件叶节点，直接返回单元素列表
    if node.get("type") == "file":
        return [{"path": current_path, "size_kb": int(node.get("size_kb", 0))}]

    # 递归步骤：遍历目录的所有子节点并汇总结果
    results: List[Dict[str, Any]] = []
    for child in node.get("children", []):
        results.extend(flatten_kb_tree(child, prefix=current_path, max_depth=max_depth - 1))
    return results


def top_largest_docs(tree: Dict[str, Any], top_n: int = 3) -> List[Dict[str, Any]]:
    """找出知识库中体积最大的前 top_n 份文档（使用 lambda 多键排序）。"""
    all_files = flatten_kb_tree(tree)
    # 先按 size_kb 降序，体积相同时按 path 字母升序，保证排序稳定
    ranked = sorted(all_files, key=lambda doc: (-doc["size_kb"], doc["path"]))
    return ranked[:top_n]


if __name__ == "__main__":
    sample_kb = {
        "type": "dir",
        "name": "StarMind_KB",
        "children": [
            {"type": "file", "name": "readme.md", "size_kb": 5},
            {
                "type": "dir",
                "name": "研发部",
                "children": [
                    {"type": "file", "name": "api_spec.md", "size_kb": 48},
                    {
                        "type": "dir",
                        "name": "新人培训",
                        "children": [{"type": "file", "name": "python_guide.md", "size_kb": 120}],
                    },
                ],
            },
            {"type": "file", "name": "refund_policy.md", "size_kb": 32},
        ],
    }
    print("Top 2 最大文档:", top_largest_docs(sample_kb, top_n=2))
''',
                "explanation": (
                    "1. `flatten_kb_tree` 加入了 `max_depth` 防御参数，防止恶意构造的畸形 JSON 引发栈溢出。\n"
                    "2. `key=lambda doc: (-doc['size_kb'], doc['path'])` 是 Python 经典多条件混合排序技巧：数值取负实现降序，字符串保持升序。"
                ),
                "expected_output": (
                    "Top 2 最大文档: [{'path': 'StarMind_KB/研发部/新人培训/python_guide.md', 'size_kb': 120}, {'path': 'StarMind_KB/研发部/api_spec.md', 'size_kb': 48}]"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-006 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day06_text_pipeline import strip_and_collapse, redact_secret_key, run_pipeline, build_chat_request
from day06_kb_tree import flatten_kb_tree, top_largest_docs


def test_text_pipeline_and_request_builder():
    out = run_pipeline("  key= sk-abc123  hello  ", strip_and_collapse, redact_secret_key)
    assert out == "key= sk-***REDACTED*** hello"

    req1 = build_chat_request("qwen-plus", "你好", temperature=0.5, seed=None)
    req2 = build_chat_request("qwen-plus", "第二条")
    assert len(req1["messages"]) == 1
    assert len(req2["messages"]) == 1  # 确保两次调用消息列表完全隔离
    assert "seed" not in req1
    assert req1["temperature"] == 0.5


def test_kb_tree_recursion_and_ranking():
    tree = {
        "type": "dir",
        "name": "root",
        "children": [
            {"type": "file", "name": "a.md", "size_kb": 10},
            {
                "type": "dir",
                "name": "sub",
                "children": [
                    {"type": "file", "name": "b.md", "size_kb": 50},
                    {"type": "file", "name": "c.md", "size_kb": 50},
                ],
            },
        ],
    }
    flat = flatten_kb_tree(tree)
    assert len(flat) == 3
    top2 = top_largest_docs(tree, top_n=2)
    assert [d["path"] for d in top2] == ["root/sub/b.md", "root/sub/c.md"]

    with pytest.raises(RecursionError):
        flatten_kb_tree(tree, max_depth=0)
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "多条件 lambda 排序 `(-doc['size_kb'], doc['path'])` 很老练，递归加 `max_depth` 护栏体现了安全意识。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "专门加了连续两次调用 `build_chat_request` 的隔离性测试，确认无可变默认参数污染。",
                "resolution": "QA 验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：修复可变默认参数 Bug",
                "difficulty": "基础巩固",
                "requirement": "下面有 Bug 的函数 `def append_message(msg, history=[]): history.append(msg); return history` 会导致不同用户对话串台。请重写安全版本 `append_message(msg: str, history: list | None = None) -> list[str]`，并验证两次独立调用互不干扰。",
                "hint": "用 `None` 作为默认值，且为了不意外修改外部传入列表，建议在函数内拷贝或明确约定行为。",
                "solution_code": r'''"""Day 6 课后题 1：修复可变默认参数导致的对话串台 Bug。"""

from typing import List, Optional


def append_message(msg: str, history: Optional[List[str]] = None) -> List[str]:
    """安全追加对话消息，每次未传 history 时创建全新列表。"""
    records = [] if history is None else list(history)
    records.append(msg)
    return records


if __name__ == "__main__":
    user_a = append_message("你好，我是A")
    user_b = append_message("你好，我是B")
    print("用户A:", user_a)
    print("用户B:", user_b)
''',
                "solution_analysis": "同时使用了 `None` 哨兵和 `list(history)` 防御性拷贝，彻底消除状态串台隐患。"
            },
            {
                "title": "企业实战：带关键词过滤的文档检索排序器",
                "difficulty": "企业实战",
                "requirement": "编写 `search_docs(docs: list[dict], keyword: str, min_score: float = 0.5) -> list[dict]`，用列表推导式 + `lambda` 筛选出标题包含关键词且得分 `>= min_score` 的文档，按得分降序返回。",
                "hint": "先过滤再 `sorted(..., key=lambda d: d['score'], reverse=True)`。",
                "solution_code": r'''"""Day 6 课后题 2：关键词过滤与相关度排序检索器。"""

from typing import List, Dict, Any


def search_docs(
    docs: List[Dict[str, Any]], keyword: str, min_score: float = 0.5
) -> List[Dict[str, Any]]:
    """按关键词和最低分阈值过滤文档，并按相关度降序排列。"""
    kw = keyword.strip().lower()
    matched = [
        d for d in docs
        if kw in str(d.get("title", "")).lower() and float(d.get("score", 0.0)) >= min_score
    ]
    return sorted(matched, key=lambda d: d["score"], reverse=True)


if __name__ == "__main__":
    kb = [
        {"title": "Python 异步编程指南", "score": 0.92},
        {"title": "Python 安装手册", "score": 0.41},
        {"title": "FastAPI + Python 实战", "score": 0.85},
    ]
    print(search_docs(kb, "python", min_score=0.5))
''',
                "solution_analysis": "大小写不敏感匹配 + 阈值过滤 + lambda 降序，是简化版 RAG 重排（Rerank）的核心逻辑。"
            },
            {
                "title": "架构进阶：递归统计嵌套 JSON 中所有数值型 Token 总和",
                "difficulty": "架构进阶",
                "requirement": "一个复杂的多 Agent 调用日志 JSON 中，各层子任务字典里都可能包含名为 `'tokens'` 的整数键。编写递归函数 `sum_nested_tokens(data: Any) -> int`，无论嵌套多少层 dict/list，准确汇总所有 `'tokens'` 之和。",
                "hint": "若 `isinstance(data, dict)` 则累加 `data['tokens']`（若为 int 且非 bool）并递归其所有 values；若 `isinstance(data, list)` 则递归其每个元素。",
                "solution_code": r'''"""Day 6 课后题 3：递归汇总嵌套多 Agent 日志中的总 Token 消耗。"""

from typing import Any


def sum_nested_tokens(data: Any) -> int:
    """递归遍历任意深度 dict/list，汇总所有键名为 'tokens' 的整数值。"""
    total = 0
    if isinstance(data, dict):
        for k, v in data.items():
            # 注意：Python 中 bool 是 int 的子类，需排除 True/False
            if k == "tokens" and isinstance(v, int) and not isinstance(v, bool):
                total += v
            else:
                total += sum_nested_tokens(v)
    elif isinstance(data, list):
        for item in data:
            total += sum_nested_tokens(item)
    return total


if __name__ == "__main__":
    trace = {
        "agent": "planner",
        "tokens": 150,
        "subtasks": [
            {"agent": "search", "tokens": 300},
            {"agent": "writer", "tokens": 450, "retries": [{"tokens": 100}]},
        ],
    }
    print("多 Agent 总消耗 Token:", sum_nested_tokens(trace))
''',
                "solution_analysis": "特别注意 `not isinstance(v, bool)` 这个高阶细节——因为 `isinstance(True, int)` 为 `True`，漏掉判断会把布尔值当 1 算进账单里！"
            }
        ],
        "extra_deep_dive": (
            "【大厂架构师心法：什么是「纯函数」？为什么测试工程师爱死它？】\n"
            "纯函数满足两条铁律：1）相同输入永远产生相同输出；2）不修改全局变量、不偷偷写文件或发网络请求（无副作用）。"
            "把核心业务逻辑写成纯函数，你的单元测试不需要 Mock 数据库、不需要联网，1000 个用例 0.2 秒跑完，重构时心里稳如泰山。"
        )
    },

    # =========================================================================
    # DAY 7: 第一周复习与周测
    # =========================================================================
    {
        "day": 7,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 1,
        "week_name": "第 1 周：Python 核心语法与数据结构基石",
        "title": "第一周复习与周测",
        "subtitle": "串讲核心语法与数据结构，完成周测并交付「星辰企业通讯录管理系统 + JSON 持久化」",
        "gitlab_ticket": "STARMIND-007",
        "git_branch": "feat/day07-week1-contacts-project",
        "git_commit": "feat(day07): 完成第一周综合周测与企业通讯录管理系统（含JSON持久化）",
        "prev_recap": "前六天咱们从环境搭建一路打到变量、字符串、流程控制、list/tuple/set/dict、JSON 和函数管道，第一周地基已全部铺完。",
        "next_preview": "下周（Day 8）进入第二周，咱们正式开启面向对象编程（OOP），把零散的字典升级成带校验和行为的 `ChatMessage` 核心类！",
        "narrator_opening": (
            "眨眼第一周就到收官日了！今天不塞新语法，咱们干两件检验真功夫的事："
            "上午先做第一周知识点串讲 + 自动化周测题库自检，查漏补缺，看看哪些坑还容易踩；"
            "下午直接进入第一个完整闭环小项目 STARMIND-007——「星辰数科企业通讯录管理系统（支持增删改查、模糊搜索、按部门统计、手机号脱敏以及 JSON 文件持久化）」。"
            "阿杰今天会亲自跑全套集成测试，通过了咱们第一周就圆满通关！"
        ),
        "narrator_closing": (
            "恭喜你拿下第一周综合项目！从零基础到独立写出带 JSON 持久化、脱敏、模糊搜索和自动化单测的完整通讯录系统，只用了 7 天。"
            "周末好好歇半天，下周一咱们开启面向对象编程（OOP），给星辰智脑搭起真正的模型抽象层。"
        ),
        "business_prd": {
            "background": "HR 与行政部门需要一个离线可用的内部通讯录 CLI 系统，支持快速录入、修改、删除员工联系方式，并持久化保存到本地 JSON 文件，便于星辰智脑后续接入查人技能。",
            "pain_points": [
                "员工信息分散在多个 Excel 表格里，查询慢且容易重复录入同一工号。",
                "命令行程序关闭后内存数据丢失，缺少本地 JSON 持久化机制。",
                "第一周知识点零散，需要通过综合项目将数据结构、函数与 JSON 融会贯通。"
            ],
            "goals": [
                "完成第一周核心知识（类型/切片/流程/容器/JSON/函数）综合自测与复盘。",
                "独立实现通讯录完整 CRUD、关键字模糊搜索（姓名/部门/标签）、JSON 加载与保存。",
                "确保所有业务操作与异常边界通过自动化集成测试。"
            ],
            "acceptance_criteria": [
                "支持按工号防重添加、更新、删除、精确查询与关键词模糊搜索。",
                "重启后能从 JSON 文件完整恢复所有联系人数据，中文无转义乱码。",
                "内置第一周自测判分引擎可自动评估答题正确率。"
            ],
            "non_functional": [
                "采用函数式模块化拆分：存储层（JSON I/O）与业务 CRUD 层分离。",
                "所有测试在隔离临时目录运行，零残留文件。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "第一周知识图谱串讲与周测挑战", "detail": "串联 Day 1~6 核心高频考点与易错题，运行周测自评脚本定位薄弱项。"},
            {"slot": "下午 14:00-17:30", "topic": "综合项目实战：企业通讯录管理系统 + JSON 持久化", "detail": "完整实现 CRUD、模糊检索、部门分组统计与 JSON 落盘恢复。"},
            {"slot": "晚间 19:00-20:30", "topic": "集成测试验收与性能检查", "detail": "运行 pytest 全量验收测试，模拟重启加载、重复工号拦截与异常搜索。"},
            {"slot": "复盘 20:30-21:00", "topic": "第一周学习总结与第二周预习", "detail": "提交周报与 Git MR，完成 3 道巩固拓展作业。"}
        ],
        "architecture_design": (
            "这是学员交付的第一个完整状态持久化应用，我们提前演练标准的「三层轻量架构」：\n"
            "1. **存储持久化层**（`load_contacts` / `save_contacts`）：负责 JSON 文件读写、首次运行文件不存在时返回空字典兜底。\n"
            "2. **领域业务层**（`upsert_contact` / `delete_contact` / `search_contacts` / `dept_summary`）：以工号 `emp_id` 作为 dict 主键实现 O(1) 定位，支持跨姓名/部门/手机号模糊搜索。\n"
            "3. **展示与周测评估层**（day07_week1_quiz.py）：把第一周易错考点写成可执行的自动化判分引擎，帮学员用代码验证自己的理解。"
        ),
        "diagrams": [
            {
                "title": "企业通讯录管理系统业务流程图",
                "kind": "flowchart",
                "caption": "展示通讯录启动加载 JSON、执行 CRUD/搜索并落盘持久化的完整生命周期。",
                "nodes": [
                    {"id": "n1", "label": "启动加载 JSON", "sub": "不存在则初始化空库", "color": "#3b82f6"},
                    {"id": "n2", "label": "执行业务操作", "sub": "新增/更新/删除/模糊搜", "color": "#8b5cf6"},
                    {"id": "n3", "label": "数据校验与脱敏", "sub": "工号去重 + 手机掩码", "color": "#f59e0b"},
                    {"id": "n4", "label": "保存至 JSON 文件", "sub": "UTF-8 缩进持久化", "color": "#10b981"},
                    {"id": "n5", "label": "下次启动无损恢复", "sub": "跨会话数据不丢失", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "内存 dict"},
                    {"from": "n2", "to": "n3", "label": "合法性检查"},
                    {"from": "n3", "to": "n4", "label": "变更落盘"},
                    {"from": "n4", "to": "n5", "label": "重启验证"}
                ]
            },
            {
                "title": "通讯录系统分层架构图",
                "kind": "architecture",
                "caption": "清晰分离 JSON 持久层、内存索引业务层与终端展示/测试层，为后续接入数据库铺路。",
                "nodes": [
                    {"id": "a1", "label": "CLI / Pytest 入口", "sub": "指令调用与自动化验收", "color": "#3b82f6"},
                    {"id": "a2", "label": "ContactService 业务层", "sub": "CRUD/模糊搜索/部门统计", "color": "#8b5cf6"},
                    {"id": "a3", "label": "JSON 持久化层", "sub": "load_contacts / save_contacts", "color": "#f59e0b"},
                    {"id": "a4", "label": "本地 contacts.json", "sub": "UTF-8 结构化文件", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "函数调用"},
                    {"from": "a2", "to": "a3", "label": "读写请求"},
                    {"from": "a3", "to": "a4", "label": "磁盘 I/O"}
                ]
            },
            {
                "title": "第一周 Python 核心知识网络图",
                "kind": "schematic",
                "caption": "串联 Day 1~6 六大知识模块，展示它们如何共同支撑起 Day 7 的通讯录系统。",
                "nodes": [
                    {"id": "s1", "label": "基础类型与字符串", "sub": "Day 1-2：脱敏与格式化", "color": "#3b82f6"},
                    {"id": "s2", "label": "流程控制", "sub": "Day 3：校验分支与遍历", "color": "#8b5cf6"},
                    {"id": "s3", "label": "核心数据结构", "sub": "Day 4-5：dict主键+JSON", "color": "#f59e0b"},
                    {"id": "s4", "label": "函数与模块化", "sub": "Day 6：纯函数与排序", "color": "#10b981"},
                    {"id": "s5", "label": "通讯录持久化系统", "sub": "Day 7：综合闭环交付", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "s1", "to": "s5", "label": "数据清洗"},
                    {"from": "s2", "to": "s5", "label": "搜索过滤"},
                    {"from": "s3", "to": "s5", "label": "索引与落盘"},
                    {"from": "s4", "to": "s5", "label": "解耦封装"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 第一周高频易错点清扫清单",
                "content": (
                    "1）`bool('False')` 为 `True`；2）字符串不可变，方法调用必须重新赋值；3）遍历列表禁止原地 `remove`；"
                    "4）空集合是 `set()` 不是 `{}`；5）`json.dumps` 必加 `ensure_ascii=False`；6）函数默认参数严禁写 `[]` 或 `{}`。"
                ),
                "pitfalls": "每次写完代码养成跑一遍 `pytest` 的习惯，能提前拦截 80% 的低级拼写与边界错误。"
            },
            {
                "heading": "2. 主键索引设计：为什么通讯录用 dict 而不是 list？",
                "content": (
                    "用 `emp_id` 作键的字典 `{emp_id: {name, dept, phone, ...}}`，按工号查人、改人、删人全是 O(1) 瞬间完成，且天然保证工号唯一不重复。"
                ),
                "pitfalls": "注意 JSON 的键只能是字符串！即使你在内存里用整数 `1001` 当字典 key，经过 `json.dump` 再 `json.load` 回来后 key 会变成字符串 `'1001'`，所以统一把 `emp_id` 定义为 `str`（如 `'XM-0001'`）是最省心的工程实践。"
            },
            {
                "heading": "3. 持久化原子写入思路",
                "content": (
                    "生产级本地 JSON 持久化通常遵循：读取时若文件不存在返回空库 `{}`；写入时先确保父目录存在（`mkdir(parents=True, exist_ok=True)`），再以 UTF-8 覆盖写出。"
                ),
                "pitfalls": "如果文件内容被人为改坏导致 `JSONDecodeError`，应在加载层给出明确错误提示，避免静默覆盖把旧数据清空。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：实现第一周知识点自动化周测判分引擎",
                "file_path": "src/day07_week1_quiz.py",
                "narration": "先用 10 分钟跑一遍咱们第一周的 5 道核心陷阱周测题，全部答对拿 100 分再做大项目！",
                "code": r'''"""
STARMIND-007 模块一：第一周 Python 核心语法自动化周测判分引擎。
涵盖类型转换、切片、集合运算、JSON 参数与默认参数陷阱五大高频考点。
"""

from typing import Dict, List, Any

# 周测标准题库（题号、题干、标准答案、解析）
WEEK1_QUESTIONS: List[Dict[str, str]] = [
    {
        "id": "Q1",
        "topic": "布尔类型转换",
        "question": "表达式 bool('False') 的求值结果是 True 还是 False？",
        "answer": "True",
        "explanation": "非空字符串转 bool 永远为 True，只有空字符串 '' 为 False。",
    },
    {
        "id": "Q2",
        "topic": "空集合创建",
        "question": "在 Python 中创建一个空集合应该写 set() 还是 {}？",
        "answer": "set()",
        "explanation": "{} 创建的是空字典 dict，空集合必须写 set()。",
    },
    {
        "id": "Q3",
        "topic": "字符串切片",
        "question": "表达式 'StarMind'[0:4] 的结果是什么？",
        "answer": "Star",
        "explanation": "切片遵循左闭右开原则，取索引 0, 1, 2, 3 四个字符。",
    },
    {
        "id": "Q4",
        "topic": "JSON 中文输出",
        "question": "json.dumps 中防止中文被转义为 \\uXXXX 的关键参数名是什么？",
        "answer": "ensure_ascii",
        "explanation": "设置 ensure_ascii=False 即可保留可读中文字符。",
    },
    {
        "id": "Q5",
        "topic": "函数默认参数",
        "question": "需要列表型可选参数时，函数签名中默认值应写 None 还是 []？",
        "answer": "None",
        "explanation": "可变默认参数 [] 会在多次调用间共享导致数据串台，必须用 None 占位。",
    },
]


def grade_quiz(submissions: Dict[str, str]) -> Dict[str, Any]:
    """根据学员提交的答案字典自动判分并生成错题诊断报告。"""
    total = len(WEEK1_QUESTIONS)
    correct = 0
    wrong_details: List[Dict[str, str]] = []

    for q in WEEK1_QUESTIONS:
        qid = q["id"]
        user_ans = str(submissions.get(qid, "")).strip()
        if user_ans == q["answer"]:
            correct += 1
        else:
            wrong_details.append(
                {
                    "id": qid,
                    "topic": q["topic"],
                    "your_answer": user_ans or "(未作答)",
                    "expected": q["answer"],
                    "explanation": q["explanation"],
                }
            )

    score = int(round((correct / total) * 100)) if total else 0
    return {
        "total": total,
        "correct": correct,
        "score": score,
        "passed": score >= 80,
        "wrong_details": wrong_details,
    }


if __name__ == "__main__":
    perfect_answers = {"Q1": "True", "Q2": "set()", "Q3": "Star", "Q4": "ensure_ascii", "Q5": "None"}
    report = grade_quiz(perfect_answers)
    print(f"第一周周测成绩: {report['score']} 分 | 是否通过: {report['passed']}")
''',
                "explanation": (
                    "通过把周测题库结构化为列表字典，既能直接运行判分，也能直观复盘第一周最容易踩的 5 个坑。"
                ),
                "expected_output": "第一周周测成绩: 100 分 | 是否通过: True"
            },
            {
                "step_title": "步骤二：实现星辰企业通讯录管理系统（CRUD + 模糊搜索 + JSON 持久化）",
                "file_path": "src/day07_contacts_app.py",
                "narration": "重头戏来了！把第一周学的所有技能揉在一起，交付完整的企业通讯录管理系统，支持持久化到 JSON 并按部门统计。",
                "code": r'''"""
STARMIND-007 模块二：星辰数科企业通讯录管理系统（含 JSON 持久化）。
综合运用 dict 主键索引、字符串清洗脱敏、list/set 标签、函数封装与 JSON 文件持久化。
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# 通讯录内存数据结构：{emp_id: {"emp_id": ..., "name": ..., "dept": ..., "phone": ..., "skills": [...]}}
ContactBook = Dict[str, Dict[str, Any]]


def load_contacts(db_path: Path) -> ContactBook:
    """从 JSON 文件加载通讯录；文件不存在时返回空字典。"""
    if not db_path.exists():
        return {}
    with db_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def save_contacts(db_path: Path, book: ContactBook) -> Path:
    """将通讯录持久化写入 UTF-8 JSON 文件。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with db_path.open("w", encoding="utf-8") as f:
        json.dump(book, f, ensure_ascii=False, indent=2)
    return db_path


def mask_phone(phone: str) -> str:
    """手机号中间四位脱敏，便于展示层安全输出。"""
    p = phone.strip()
    return f"{p[:3]}****{p[-4:]}" if len(p) == 11 and p.isdigit() else "已隐藏"


def upsert_contact(
    book: ContactBook,
    emp_id: str,
    name: str,
    dept: str,
    phone: str,
    skills: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """新增或更新员工联系人记录，并自动对技能标签去重排序。"""
    eid = emp_id.strip().upper()
    if not eid or not name.strip():
        raise ValueError("工号与姓名不能为空")

    clean_skills = sorted({s.strip().lower() for s in (skills or []) if s.strip()})
    record: Dict[str, Any] = {
        "emp_id": eid,
        "name": name.strip(),
        "dept": dept.strip(),
        "phone": phone.strip(),
        "masked_phone": mask_phone(phone),
        "skills": clean_skills,
    }
    book[eid] = record
    return record


def delete_contact(book: ContactBook, emp_id: str) -> bool:
    """按工号删除联系人，存在并删除返回 True，否则返回 False。"""
    eid = emp_id.strip().upper()
    return book.pop(eid, None) is not None


def search_contacts(book: ContactBook, keyword: str) -> List[Dict[str, Any]]:
    """按姓名、部门、工号或技能标签执行大小写不敏感模糊搜索。"""
    kw = keyword.strip().lower()
    if not kw:
        return sorted(book.values(), key=lambda c: c["emp_id"])

    matched: List[Dict[str, Any]] = []
    for contact in book.values():
        haystack = " ".join(
            [
                contact["emp_id"],
                contact["name"],
                contact["dept"],
                " ".join(contact.get("skills", [])),
            ]
        ).lower()
        if kw in haystack:
            matched.append(contact)
    return sorted(matched, key=lambda c: c["emp_id"])


def summarize_by_dept(book: ContactBook) -> Dict[str, int]:
    """按部门统计通讯录人数。"""
    summary: Dict[str, int] = {}
    for contact in book.values():
        dept = contact["dept"]
        summary[dept] = summary.get(dept, 0) + 1
    return summary


if __name__ == "__main__":
    book: ContactBook = {}
    upsert_contact(book, "XM-0001", "老陈", "AI研发部", "13800001111", ["Python", "架构", "LLM"])
    upsert_contact(book, "XM-0002", "林产品", "产品部", "13900002222", ["PRD", "Prompt"])
    upsert_contact(book, "XM-0003", "阿杰", "测试部", "13700003333", ["Pytest", "Python"])
    print("搜索 'python' 命中:", [c["name"] for c in search_contacts(book, "python")])
    print("部门人数统计:", summarize_by_dept(book))
''',
                "explanation": (
                    "1. `upsert_contact` 同时承担「新增」和「更新」（Update + Insert = Upsert），并通过 `eid = emp_id.strip().upper()` 统一主键大小写规范。\n"
                    "2. `search_contacts` 将多个可搜索字段拼成 `haystack` 字符串统一小写匹配，简洁高效，还支持按技能查人！"
                ),
                "expected_output": (
                    "搜索 'python' 命中: ['老陈', '阿杰']\n"
                    "部门人数统计: {'AI研发部': 1, '产品部': 1, '测试部': 1}"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-007 第一周综合验收测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day07_week1_quiz import grade_quiz
from day07_contacts_app import (
    load_contacts,
    save_contacts,
    upsert_contact,
    delete_contact,
    search_contacts,
    summarize_by_dept,
)


def test_week1_quiz_grading():
    res = grade_quiz({"Q1": "True", "Q2": "set()", "Q3": "Star", "Q4": "ensure_ascii", "Q5": "None"})
    assert res["score"] == 100
    assert res["passed"] is True

    partial = grade_quiz({"Q1": "False"})
    assert partial["passed"] is False
    assert len(partial["wrong_details"]) == 5


def test_contacts_full_lifecycle_and_json_persistence(tmp_path: Path):
    db_file = tmp_path / "data" / "contacts.json"
    # 首次加载文件不存在应返回空字典
    book = load_contacts(db_file)
    assert book == {}

    upsert_contact(book, "xm-001", "老陈", "AI研发部", "13857101111", ["Python", "python", "LLM"])
    upsert_contact(book, "xm-002", "阿杰", "测试部", "13957102222", ["Pytest"])
    assert book["XM-001"]["masked_phone"] == "138****1111"
    assert book["XM-001"]["skills"] == ["llm", "python"]

    # 持久化并模拟重启重新加载
    save_contacts(db_file, book)
    reloaded = load_contacts(db_file)
    assert len(reloaded) == 2
    assert len(search_contacts(reloaded, "研发")) == 1
    assert summarize_by_dept(reloaded) == {"AI研发部": 1, "测试部": 1}

    assert delete_contact(reloaded, "XM-002") is True
    assert delete_contact(reloaded, "XM-999") is False

    with pytest.raises(ValueError):
        upsert_contact(reloaded, "", "无名", "部门", "13800000000")
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "第一周收官项目完成度非常高！主键统一大写、技能标签自动去重、存储与业务分离，已经具备初级工程师的代码味了。",
                "resolution": "Approved，第一周考核通过！"
            },
            {
                "reviewer": "林产品 (PM)",
                "role": "Product Acceptance",
                "comment": "支持按技能搜人这个功能超实用，以后找懂 Pytest 或 LLM 的同事一搜就出来。",
                "resolution": "产品验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：通讯录导出 CSV 文本行",
                "difficulty": "基础巩固",
                "requirement": "编写 `export_contacts_csv_text(book: dict) -> str`，将通讯录字典转换为带表头 `emp_id,name,dept,masked_phone` 的 CSV 格式字符串（按工号升序）。",
                "hint": "遍历排序后的联系人，把每行字段用 `','.join(...)` 拼接，再用 `'\\n'.join(lines)` 合并。",
                "solution_code": r'''"""Day 7 课后题 1：通讯录导出 CSV 文本。"""

from typing import Dict, Any, List


def export_contacts_csv_text(book: Dict[str, Dict[str, Any]]) -> str:
    """将通讯录导出为标准 CSV 字符串（含表头）。"""
    lines: List[str] = ["emp_id,name,dept,masked_phone"]
    for eid in sorted(book.keys()):
        c = book[eid]
        lines.append(f"{c['emp_id']},{c['name']},{c['dept']},{c['masked_phone']}")
    return "\n".join(lines)


if __name__ == "__main__":
    sample = {
        "XM-001": {"emp_id": "XM-001", "name": "老陈", "dept": "AI研发部", "masked_phone": "138****1111"}
    }
    print(export_contacts_csv_text(sample))
''',
                "solution_analysis": "考查字典排序遍历与格式化文本导出，为 Day 11 的标准库 `csv` 模块做铺垫。"
            },
            {
                "title": "企业实战：批量导入通讯录冲突检测器",
                "difficulty": "企业实战",
                "requirement": "HR 批量导入一批新员工列表时，需要提前检测哪些工号已经存在于现有通讯录中。编写 `detect_import_conflicts(book: dict, incoming: list[dict]) -> tuple[list[str], list[dict]]`，返回 `(冲突工号列表, 可安全新增列表)`。",
                "hint": "用 `eid in book` 做 O(1) 冲突判定，注意同一批导入数据内部也可能重复，用 `seen` 集合同步拦截。",
                "solution_code": r'''"""Day 7 课后题 2：批量导入通讯录工号冲突检测。"""

from typing import Dict, Any, List, Tuple


def detect_import_conflicts(
    book: Dict[str, Any], incoming: List[Dict[str, Any]]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """检测批量导入中的重复工号（含库内重复与批次内重复）。"""
    conflicts: List[str] = []
    safe_items: List[Dict[str, Any]] = []
    batch_seen = set()

    for item in incoming:
        eid = str(item.get("emp_id", "")).strip().upper()
        if eid in book or eid in batch_seen:
            conflicts.append(eid)
        else:
            batch_seen.add(eid)
            safe_items.append(item)
    return conflicts, safe_items


if __name__ == "__main__":
    existing = {"XM-001": {"name": "老陈"}}
    batch = [
        {"emp_id": "XM-001", "name": "重复老陈"},
        {"emp_id": "XM-002", "name": "新人A"},
        {"emp_id": "XM-002", "name": "批次内重复新人A"},
    ]
    print(detect_import_conflicts(existing, batch))
''',
                "solution_analysis": "同时检测「与存量库冲突」和「导入批次内部自冲突」，这是企业数据导入功能最容易遗漏的边界条件。"
            },
            {
                "title": "架构进阶：带备份快照的安全保存函数",
                "difficulty": "架构进阶",
                "requirement": "直接覆盖写 `contacts.json` 若中途断电可能损坏文件。编写 `safe_save_with_backup(db_path: Path, data: dict) -> Path`，若目标文件已存在则先复制一份 `.bak` 备份文件，再写入新 JSON。",
                "hint": "使用 `shutil.copy2` 或 `read_text`/`write_text` 生成 `db_path.with_suffix('.json.bak')`。",
                "solution_code": r'''"""Day 7 课后题 3：带自动备份快照的 JSON 安全落盘。"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any


def safe_save_with_backup(db_path: Path, data: Dict[str, Any]) -> Path:
    """若旧文件存在则先生成 .bak 备份，再写入最新 JSON 数据。"""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        backup_path = db_path.with_suffix(db_path.suffix + ".bak")
        backup_path.write_text(db_path.read_text(encoding="utf-8"), encoding="utf-8")
    with db_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return db_path


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "contacts.json"
        safe_save_with_backup(p, {"v": 1})
        safe_save_with_backup(p, {"v": 2})
        print("主文件:", p.read_text(encoding="utf-8").strip())
        print("备份文件存在:", p.with_suffix(".json.bak").exists())
''',
                "solution_analysis": "利用 `tempfile.TemporaryDirectory()` 做无残留自测，并引入数据持久化防损坏的备份思维。"
            }
        ],
        "extra_deep_dive": (
            "【第一周复盘：从「写脚本」到「做工程」的三个分水岭】\n"
            "第一周结束，你已经跨越了新手村。接下来第二周进入面向对象、模块包、HTTP API 和异步编程，难度会明显上一个台阶。"
            "记住三个让你进步最快的习惯：1）先想清楚数据结构再敲代码；2）核心逻辑永远写进可测试的函数/类里；3）报错先看最后一行异常类型和行号，学会读 Traceback。"
        )
    },

    # =========================================================================
    # DAY 8: 面向对象编程(上)
    # =========================================================================
    {
        "day": 8,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "面向对象编程（上）",
        "subtitle": "封装类、对象与三类方法，打造星辰智脑核心领域模型 ChatMessage 与会话管理器",
        "gitlab_ticket": "STARMIND-008",
        "git_branch": "feat/day08-oop-chat-message",
        "git_commit": "feat(day08): 使用OOP封装ChatMessage消息类与ChatSession会话记忆容器",
        "prev_recap": "第一周咱们用字典和函数交付了企业通讯录系统。但随着业务变复杂，满天飞的裸字典没有强约束，少写一个字段直到运行才炸。",
        "next_preview": "明天（Day 9）咱们继续深挖 OOP 进阶：继承、多态、super、魔术方法与 `@property`，亲手搭出 `BaseModel -> OpenAIModel / QwenModel` 多模型统一适配层！",
        "narrator_opening": (
            "新的一周开始了！上周咱们用裸字典 `{'role': 'user', 'content': '你好'}` 表示消息，写着写着你肯定发现痛点了："
            "万一有人把 `'role'` 拼成 `'roles'`，或者塞了个非法角色 `'boss'` 进去，裸字典根本拦不住！"
            "今天 STARMIND-008 咱们用面向对象（OOP）彻底治好这个毛病：设计星辰智脑最核心的数据类 `ChatMessage`，"
            "把字段校验、时间戳、Token 估算、转 API 字典（`to_api_dict`）、工厂类方法（`@classmethod`）和静态校验工具（`@staticmethod`）全优雅地封装进去！"
        ),
        "narrator_closing": (
            "今天你亲手写出了 `ChatMessage` 和 `ChatSession`，这俩类咱们后面从 Day 9 一直用到 Day 14 甚至 FastAPI 后端！"
            "记住三种方法的分工：操作单个对象状态用实例方法（`self`），做构造工厂或读类属性用 `@classmethod`（`cls`），纯工具函数用 `@staticmethod`。"
            "明天咱们玩继承和多态，把不同大模型厂商统一收编！"
        ),
        "business_prd": {
            "background": "星辰智脑对话引擎需要统一的消息领域对象，替代容易拼错键名的裸字典，并支持单会话多轮记忆管理、Token 统计与上下文窗口裁剪。",
            "pain_points": [
                "裸字典无法在创建时校验 `role` 是否属于 `system/user/assistant`。",
                "每条消息的 Token 估算、时间戳记录、OpenAI 协议序列化逻辑散落在各处。",
                "缺乏统一的会话容器来管理多轮消息追加、清空和超长历史裁剪。"
            ],
            "goals": [
                "理解类（Class）与实例（Instance）、`__init__` 构造方法与 `self` 绑定机制。",
                "掌握实例方法、类方法（`@classmethod`）与静态方法（`@staticmethod`）的区别与应用场景。",
                "完成 `ChatMessage` 与 `ChatSession` 两个核心领域类并通过单元测试。"
            ],
            "acceptance_criteria": [
                "`ChatMessage` 在初始化时校验合法角色与非空内容，提供 `to_api_dict()` 与 `from_dict()` 工厂方法。",
                "`ChatSession` 支持追加消息、保留 system prompt 的窗口裁剪、总 Token 统计及导出 OpenAI messages 列表。",
                "所有正常与异常用例通过 pytest。"
            ],
            "non_functional": [
                "类属性 `VALID_ROLES` 共享只读，实例属性互不干扰。",
                "提供清晰可读的 `__repr__` 便于终端调试。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "类与对象、__init__ 及三大方法对比", "detail": "讲解封装思想、类属性 vs 实例属性、self/cls 语义及静态方法使用时机。"},
            {"slot": "下午 14:00-17:30", "topic": "领域建模实战：ChatMessage 与 ChatSession", "detail": "编码实现带校验的消息类、工厂反序列化方法与滑动窗口会话管理器。"},
            {"slot": "晚间 19:00-20:30", "topic": "单元测试与对象状态隔离验证", "detail": "测试非法角色拦截、多会话实例隔离与超长历史裁剪保留系统指令。"},
            {"slot": "复盘 20:30-21:00", "topic": "OOP 设计评审与课后题", "detail": "梳理何时用类、何时用纯函数，完成 3 道梯度课后作业。"}
        ],
        "architecture_design": (
            "在领域驱动设计（DDD）中，把「数据 + 围绕数据的行为」内聚成一个对象是消除面条代码的第一步：\n"
            "1. **值对象 `ChatMessage`（day08_chat_message.py）**：封装 `role`、`content`、`created_at` 与估算 `tokens`，在 `__init__` 中立刻执行不变式校验（非法 role 直接抛 `ValueError`），并提供 `from_dict` 类方法作为统一反序列化工厂。\n"
            "2. **聚合根 `ChatSession`（day08_chat_session.py）**：持有 `session_id`、可选 `system_prompt` 和 `messages: List[ChatMessage]`。当对话轮次超过 `max_history` 时，自动裁剪最早的 user/assistant 消息，同时永远保留开头的 `system` 角色设定——这是所有生产级多轮聊天机器人的标配内存管理机制。"
        ),
        "diagrams": [
            {
                "title": "ChatSession 多轮对话与窗口裁剪流程图",
                "kind": "flowchart",
                "caption": "展示新消息封装为 ChatMessage 加入会话后，如何触发最大轮次检查并安全保留 System Prompt。",
                "nodes": [
                    {"id": "n1", "label": "接收角色与正文", "sub": "role + content", "color": "#3b82f6"},
                    {"id": "n2", "label": "ChatMessage 构造校验", "sub": "校验 role 合法性与非空", "color": "#8b5cf6"},
                    {"id": "n3", "label": "追加至 Session", "sub": "self._messages.append", "color": "#f59e0b"},
                    {"id": "n4", "label": "窗口上限检查", "sub": "超限则裁剪最早历史", "color": "#ef4444"},
                    {"id": "n5", "label": "导出 API messages", "sub": "system + 最近 N 条", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "实例化"},
                    {"from": "n2", "to": "n3", "label": "入队"},
                    {"from": "n3", "to": "n4", "label": "防超长"},
                    {"from": "n4", "to": "n5", "label": "to_api_payload()"}
                ]
            },
            {
                "title": "ChatMessage 与 ChatSession 类结构设计图",
                "kind": "architecture",
                "caption": "展示两个核心类的属性、实例方法、类方法与静态方法之间的协作关系。",
                "nodes": [
                    {"id": "a1", "label": "ChatMessage 类", "sub": "VALID_ROLES 类属性", "color": "#3b82f6"},
                    {"id": "a2", "label": "静态/类方法", "sub": "estimate_tokens / from_dict", "color": "#8b5cf6"},
                    {"id": "a3", "label": "ChatSession 类", "sub": "持有 List[ChatMessage]", "color": "#10b981"},
                    {"id": "a4", "label": "OpenAI 兼容字典列表", "sub": "[{role, content}, ...]", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "a2", "to": "a1", "label": "校验与构造"},
                    {"from": "a3", "to": "a1", "label": "组合 1..N"},
                    {"from": "a3", "to": "a4", "label": "序列化输出"}
                ]
            },
            {
                "title": "类属性与实例属性内存布局示意图",
                "kind": "schematic",
                "caption": "解释为什么 VALID_ROLES 定义在类上全员共享，而 self.content 必须写在 __init__ 里独立存储。",
                "nodes": [
                    {"id": "s1", "label": "类对象 ChatMessage", "sub": "VALID_ROLES = ('system',...)", "color": "#8b5cf6"},
                    {"id": "s2", "label": "实例 msg1", "sub": "role='user', content='你好'", "color": "#3b82f6"},
                    {"id": "s3", "label": "实例 msg2", "sub": "role='assistant', content='在的'", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "s2", "to": "s1", "label": "__class__ 共享方法与常量"},
                    {"from": "s3", "to": "s1", "label": "__class__ 共享方法与常量"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 类、实例与 self 的本质",
                "content": (
                    "类是蓝图，实例是根据蓝图造出来的具体对象。`__init__(self, ...)` 在对象创建后自动执行初始化。"
                    "`self` 就是当前实例本身的引用，调用 `msg.to_api_dict()` 时 Python 会自动把 `msg` 作为第一个参数 `self` 传进去。"
                ),
                "pitfalls": "千万不要把可变容器（如 `messages = []`）直接写在类体顶层当作实例属性！那样所有会话实例会共享同一个列表，导致不同用户聊天记录互相串台！实例独享的可变容器必须写在 `__init__` 的 `self.messages = []` 里。"
            },
            {
                "heading": "2. 实例方法 vs @classmethod vs @staticmethod",
                "content": (
                    "- **实例方法** `(self, ...)`：读写当前对象的状态（如 `msg.to_api_dict()`）。\n"
                    "- **类方法** `@classmethod (cls, ...)`：接收类本身 `cls`，最常用来写「替代构造器/工厂方法」（如 `ChatMessage.from_dict(data)`），且子类继承时会自动返回子类实例。\n"
                    "- **静态方法** `@staticmethod (...)`：既不需要 `self` 也不需要 `cls`，纯粹归类到类命名空间下的工具函数（如 `ChatMessage.estimate_tokens(text)`）。"
                ),
                "pitfalls": "在 `@classmethod` 中构造对象请写 `cls(...)` 而不是写死类名 `ChatMessage(...)`，这样以后被子类继承才不会返回错误类型。"
            },
            {
                "heading": "3. 封装与不变式（Invariant）保护",
                "content": (
                    "把数据合法性检查放在 `__init__` 入口，就能保证内存中存在的每一个 `ChatMessage` 对象都是 100% 合法的，下游代码无需再反复判空或查角色拼写。"
                ),
                "pitfalls": "约定俗成：以单下划线开头的属性（如 `self._messages`）表示内部受保护状态，外部应通过公开方法操作而非直接乱改。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：实现星辰智脑核心领域类 ChatMessage",
                "file_path": "src/day08_chat_message.py",
                "narration": "咱们亲手写星辰智脑的第一个正式领域类 `ChatMessage`，把角色校验、Token 估算、JSON 工厂构造全部优雅封装。",
                "code": r'''"""
STARMIND-008 模块一：核心领域模型 ChatMessage。
演示类属性、__init__ 初始化与不变式校验、实例方法、@classmethod 与 @staticmethod。
"""

from datetime import datetime, timezone
from typing import Dict, Any, Tuple


class ChatMessage:
    """表示大模型多轮对话中的单条标准化消息。"""

    # 类属性：所有消息实例共享的合法角色白名单（不可变元组）
    VALID_ROLES: Tuple[str, ...] = ("system", "user", "assistant", "tool")

    def __init__(self, role: str, content: str, created_at: str | None = None) -> None:
        normalized_role = role.strip().lower()
        # 构造期不变式校验：杜绝非法角色进入系统
        if normalized_role not in self.VALID_ROLES:
            raise ValueError(f"非法角色 '{role}'，允许的角色: {self.VALID_ROLES}")

        cleaned_content = content.strip()
        if not cleaned_content:
            raise ValueError("消息正文 content 不能为空")

        # 实例属性：每条消息独立拥有
        self.role: str = normalized_role
        self.content: str = cleaned_content
        self.created_at: str = created_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.tokens: int = self.estimate_tokens(self.content)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """静态工具方法：粗略估算文本 Token 数量。"""
        if not text:
            return 0
        return max(1, (len(text) * 3 + 3) // 4)

    def to_api_dict(self) -> Dict[str, str]:
        """实例方法：转换为 OpenAI/DeepSeek 兼容的最小 API 消息字典。"""
        return {"role": self.role, "content": self.content}

    def to_storage_dict(self) -> Dict[str, Any]:
        """实例方法：转换为包含元数据的完整持久化字典。"""
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "tokens": self.tokens,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """类方法工厂：从字典反序列化构造 ChatMessage 实例。"""
        return cls(
            role=str(data.get("role", "")),
            content=str(data.get("content", "")),
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        preview = self.content if len(self.content) <= 20 else self.content[:17] + "..."
        return f"ChatMessage(role={self.role!r}, tokens={self.tokens}, content={preview!r})"


if __name__ == "__main__":
    m1 = ChatMessage("user", "你好，请介绍一下杭州星辰数科")
    m2 = ChatMessage.from_dict({"role": "assistant", "content": "您好！星辰数科专注于企业级大模型应用研发。"})
    print(m1)
    print("API 协议格式:", m1.to_api_dict())
    print("反序列化对象:", m2)
''',
                "explanation": (
                    "1. `VALID_ROLES` 用元组定义在类上，全员共享且不可篡改。\n"
                    "2. `from_dict` 使用 `cls(...)` 而不是 `ChatMessage(...)`，保证明天做继承时子类也能直接复用这个工厂方法。\n"
                    "3. `__repr__` 截断超长正文并展示角色和 Token 数，调试时打印列表非常清爽。"
                ),
                "expected_output": (
                    "ChatMessage(role='user', tokens=11, content='你好，请介绍一下杭州星辰数科')\n"
                    "API 协议格式: {'role': 'user', 'content': '你好，请介绍一下杭州星辰数科'}\n"
                    "反序列化对象: ChatMessage(role='assistant', tokens=17, content='您好！星辰数科专注于企业级大模型...')"
                )
            },
            {
                "step_title": "步骤二：实现多轮会话记忆容器 ChatSession",
                "file_path": "src/day08_chat_session.py",
                "narration": "有了单条消息 `ChatMessage`，咱们再用「组合（Composition）」封装一个 `ChatSession` 会话管理器，自动管理历史记忆和窗口裁剪。",
                "code": r'''"""
STARMIND-008 模块二：多轮会话记忆容器 ChatSession。
演示对象组合（ChatSession 持有多个 ChatMessage）、窗口裁剪与受保护状态管理。
"""

from typing import List, Dict, Optional
from day08_chat_message import ChatMessage


class ChatSession:
    """管理单个用户的多轮对话上下文与滑动窗口裁剪。"""

    def __init__(
        self,
        session_id: str,
        system_prompt: Optional[str] = None,
        max_history: int = 10,
    ) -> None:
        self.session_id: str = session_id
        self.max_history: int = max(1, int(max_history))
        # 系统指令单独保管，裁剪历史时绝不误删
        self._system_msg: Optional[ChatMessage] = (
            ChatMessage("system", system_prompt) if system_prompt else None
        )
        # 实例独享的消息历史列表（绝不能写成类属性！）
        self._messages: List[ChatMessage] = []

    def add_message(self, role: str, content: str) -> ChatMessage:
        """向会话追加一条非 system 消息，并在超出窗口上限时自动裁剪最早消息。"""
        msg = ChatMessage(role, content)
        if msg.role == "system":
            self._system_msg = msg
            return msg

        self._messages.append(msg)
        # 滑动窗口裁剪：仅保留最近 max_history 条对话
        if len(self._messages) > self.max_history:
            self._messages = self._messages[-self.max_history :]
        return msg

    def total_tokens(self) -> int:
        """统计当前会话上下文（含系统指令）的估算总 Token 数。"""
        sys_tokens = self._system_msg.tokens if self._system_msg else 0
        return sys_tokens + sum(m.tokens for m in self._messages)

    def to_api_messages(self) -> List[Dict[str, str]]:
        """导出可直接传给大模型 API 的 messages 字典列表。"""
        payload: List[Dict[str, str]] = []
        if self._system_msg:
            payload.append(self._system_msg.to_api_dict())
        payload.extend(m.to_api_dict() for m in self._messages)
        return payload

    def clear(self) -> None:
        """清空历史对话，但保留 system_prompt 人设设定。"""
        self._messages.clear()


if __name__ == "__main__":
    session = ChatSession("sess-001", system_prompt="你是星辰智脑助手", max_history=2)
    session.add_message("user", "第一句提问")
    session.add_message("assistant", "第一句回复")
    session.add_message("user", "第二句提问")
    print("当前窗口消息数(不含system):", len(session.to_api_messages()) - 1)
    print("总 Token 估算:", session.total_tokens())
    print("导出 API Payload:", session.to_api_messages())
''',
                "explanation": (
                    "1. 把 `_system_msg` 和 `_messages` 分开存储是极其聪明的架构决定：无论对话进行了 100 轮还是用户执行了 `/clear`，AI 的系统人设都不会被冲掉。\n"
                    "2. `self._messages[-self.max_history:]` 用负向切片一行完成滑动窗口截断。"
                ),
                "expected_output": (
                    "当前窗口消息数(不含system): 2\n"
                    "总 Token 估算: 16\n"
                    "导出 API Payload: [{'role': 'system', 'content': '你是星辰智脑助手'}, {'role': 'assistant', 'content': '第一句回复'}, {'role': 'user', 'content': '第二句提问'}]"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-008 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day08_chat_message import ChatMessage
from day08_chat_session import ChatSession


def test_chat_message_validation_and_factory():
    msg = ChatMessage("USER", "  测试消息  ")
    assert msg.role == "user"
    assert msg.content == "测试消息"
    assert msg.to_api_dict() == {"role": "user", "content": "测试消息"}

    rebuilt = ChatMessage.from_dict(msg.to_storage_dict())
    assert rebuilt.role == "user"
    assert rebuilt.content == "测试消息"

    with pytest.raises(ValueError):
        ChatMessage("boss", "非法角色")
    with pytest.raises(ValueError):
        ChatMessage("user", "   ")


def test_chat_session_window_and_isolation():
    s1 = ChatSession("s1", system_prompt="人设A", max_history=2)
    s2 = ChatSession("s2", system_prompt="人设B", max_history=2)

    s1.add_message("user", "q1")
    s1.add_message("assistant", "a1")
    s1.add_message("user", "q2")

    # s1 窗口裁剪后应保留 system + a1 + q2
    api_msgs = s1.to_api_messages()
    assert [m["content"] for m in api_msgs] == ["人设A", "a1", "q2"]
    # s2 应完全隔离不受 s1 影响
    assert [m["content"] for m in s2.to_api_messages()] == ["人设B"]

    s1.clear()
    assert [m["content"] for m in s1.to_api_messages()] == ["人设A"]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "把 system_msg 独立保管避免滑动窗口误删，这是生产级多轮对话的标配细节！`from_dict` 用 `cls()` 很规范。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "验证了多会话实例隔离、非法角色拦截和 `/clear` 后保留人设，pytest 全绿。",
                "resolution": "验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：API Token 账单计数器类",
                "difficulty": "基础巩固",
                "requirement": "设计类 `TokenTracker`，记录每次调用的输入与输出 Token 数，提供 `record(in_tokens, out_tokens)`、`total_tokens()` 和 `estimated_rmb(in_price=0.002, out_price=0.008)` 方法。",
                "hint": "在 `__init__` 中初始化 `self.input_total = 0` 和 `self.output_total = 0`。",
                "solution_code": r'''"""Day 8 课后题 1：Token 账单追踪器类。"""


class TokenTracker:
    """累计单个会话或用户的 Token 消耗并估算人民币费用。"""

    def __init__(self) -> None:
        self.input_total: int = 0
        self.output_total: int = 0
        self.call_count: int = 0

    def record(self, in_tokens: int, out_tokens: int) -> None:
        """记录单次调用消耗。"""
        self.input_total += max(0, int(in_tokens))
        self.output_total += max(0, int(out_tokens))
        self.call_count += 1

    def total_tokens(self) -> int:
        return self.input_total + self.output_total

    def estimated_rmb(self, in_price_per_1k: float = 0.002, out_price_per_1k: float = 0.008) -> float:
        cost = (self.input_total / 1000.0) * in_price_per_1k + (self.output_total / 1000.0) * out_price_per_1k
        return round(cost, 6)


if __name__ == "__main__":
    tracker = TokenTracker()
    tracker.record(500, 200)
    tracker.record(800, 400)
    print(f"调用 {tracker.call_count} 次，总 Token: {tracker.total_tokens()}，费用: ¥{tracker.estimated_rmb()}")
''',
                "solution_analysis": "典型有状态计数器类，将状态与计费逻辑内聚在一起，后续可直接挂载到 `ChatSession` 中。"
            },
            {
                "title": "企业实战：带过期标记的提示词模板类",
                "difficulty": "企业实战",
                "requirement": "设计 `PromptAsset` 类，包含 `name`、`version`、`template` 和类计数器 `total_created`（记录一共创建过多少个模板实例），提供 `render(**kwargs)` 方法与 `@classmethod get_total_created()`。",
                "hint": "在 `__init__` 中执行 `type(self).total_created += 1`。",
                "solution_code": r'''"""Day 8 课后题 2：带实例计数的提示词资产类。"""


class PromptAsset:
    """企业级 Prompt 资产管理对象。"""

    total_created: int = 0

    def __init__(self, name: str, version: str, template: str) -> None:
        self.name = name
        self.version = version
        self.template = template
        type(self).total_created += 1

    def render(self, **kwargs) -> str:
        return self.template.format(**kwargs)

    @classmethod
    def get_total_created(cls) -> int:
        return cls.total_created


if __name__ == "__main__":
    p1 = PromptAsset("客服问候", "v1.0", "你好 {user}，请问有什么可以帮您？")
    p2 = PromptAsset("工单总结", "v1.2", "请用一句话总结：{text}")
    print(p1.render(user="林产品"))
    print("累计创建模板数:", PromptAsset.get_total_created())
''',
                "solution_analysis": "区分了类级共享状态 `total_created` 与实例独享状态 `name/version/template`。"
            },
            {
                "title": "架构进阶：支持上下文 Token 预算自动裁剪的会话类",
                "difficulty": "架构进阶",
                "requirement": "比按条数裁剪更贴近生产的是「按总 Token 上限裁剪」。设计 `BudgetSession`，当新增消息后总 Token 超过 `max_tokens` 时，持续弹出最早的消息直到满足预算（至少保留最新一条用户消息）。",
                "hint": "用 `while len(self._messages) > 1 and self.total_tokens() > self.max_tokens: self._messages.pop(0)`。",
                "solution_code": r'''"""Day 8 课后题 3：按 Token 预算动态裁剪的会话容器。"""

from typing import List


class BudgetSession:
    """按最大 Token 预算自动淘汰最早历史消息的会话管理器。"""

    def __init__(self, max_tokens: int = 30) -> None:
        self.max_tokens = max_tokens
        self._messages: List[str] = []

    @staticmethod
    def _count(text: str) -> int:
        return max(1, len(text))

    def total_tokens(self) -> int:
        return sum(self._count(m) for m in self._messages)

    def add(self, text: str) -> None:
        self._messages.append(text)
        # 持续淘汰最早消息，但至少保留刚输入的最新一条
        while len(self._messages) > 1 and self.total_tokens() > self.max_tokens:
            self._messages.pop(0)

    def messages(self) -> List[str]:
        return list(self._messages)


if __name__ == "__main__":
    bs = BudgetSession(max_tokens=15)
    for m in ["消息一12345", "消息二12345", "消息三12345"]:
        bs.add(m)
    print("裁剪后保留:", bs.messages(), "当前总Token:", bs.total_tokens())
''',
                "solution_analysis": "真实大模型上下文窗口（如 8K/32K/128K）是以 Token 计费和截断的，本题用 `while` 循环实现了生产级预算裁剪。"
            }
        ],
        "extra_deep_dive": (
            "【架构师忠告：组合优于继承（Composition over Inheritance）】\n"
            "注意今天我们设计 `ChatSession` 时，是让它**持有**一个 `List[ChatMessage]`（组合），而不是让 `ChatSession` 去继承 `list`！"
            "如果继承 `list`，外部就能直接调用 `session.pop()` 把你的 `system_prompt` 删掉，彻底破坏封装。记住：只有明确的「is-a」关系才用继承，「has-a」关系一律用组合！"
        )
    },
])


DAYS_STAGE_1.extend([
    # =========================================================================
    # DAY 9: 面向对象编程(下)
    # =========================================================================
    {
        "day": 9,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "面向对象编程（下）",
        "subtitle": "精通继承、多态、魔术方法与 @property，构建星辰智脑统一模型适配层 BaseModel",
        "gitlab_ticket": "STARMIND-009",
        "git_branch": "feat/day09-oop-model-adapter",
        "git_commit": "feat(day09): 实现BaseModel抽象基类、OpenAIModel/QwenModel多态适配与@property安全校验",
        "prev_recap": "昨天咱们封装了 ChatMessage 与 ChatSession 领域对象，解决了裸字典无校验的痛点。",
        "next_preview": "明天（Day 10）咱们把单文件脚本拆分成多文件工程包（Package），引入自定义异常体系与 venv 依赖管理。",
        "narrator_opening": (
            "昨天刚说完封装，今天一早 CTO 在群里下发了一个硬指标：星辰智脑不能被任何一家大模型厂商绑死！"
            "业务层写代码时，只管调 `model.generate(prompt)`，底层今天想切 DeepSeek/OpenAI、明天想切通义千问 Qwen，业务代码一行都不许改！"
            "这正是面向对象最迷人的杀手锏——**继承、抽象基类与多态**！"
            "今天 STARMIND-009 咱们亲手设计 `BaseModel -> OpenAIModel / QwenModel` 统一适配层，再配上 `@property` 管住 `temperature` 合法范围，加上 `__str__`、`__len__`、`__call__` 魔术方法，写完你就彻底懂什么叫大厂架构感了。"
        ),
        "narrator_closing": (
            "看看咱们刚写完的 `ModelRouter`：不管传进来的是 `OpenAIModel` 还是 `QwenModel`，它根本不关心具体类型，只要都是 `BaseModel` 的子类就能无缝切换，这就是多态（Polymorphism）的威力！"
            "明天咱们学习模块化分包、异常处理和虚拟环境，正式向多文件工程迈进。"
        ),
        "business_prd": {
            "background": "企业 AI 平台需同时接入多家大模型供应商以实现高可用容灾与成本优化，但各家接口细节与计费参数不同，需要统一的抽象适配层屏蔽差异。",
            "pain_points": [
                "业务代码里充斥大量 `if vendor == 'openai': ... elif vendor == 'qwen': ...`，每接入一个新模型就得改几十个文件。",
                "外部可以直接把 `model.temperature = 999` 改爆，缺少属性写入拦截校验。",
                "模型对象缺乏统一的字符串展示与便捷调用方式。"
            ],
            "goals": [
                "掌握继承、`super()`、抽象基类（`abc.ABC` / `@abstractmethod`）与多态分发。",
                "熟练使用 `@property` 与 `@xxx.setter` 实现带范围校验的安全属性。",
                "理解高频魔术方法 `__str__`、`__repr__`、`__len__`、`__call__` 的工程用法。"
            ],
            "acceptance_criteria": [
                "定义 `BaseModel` 抽象基类，禁止直接实例化，强制子类实现 `generate()` 方法。",
                "实现 `OpenAIModel` 与 `QwenModel` 两个子类，重写各自请求头构造与本地模拟生成逻辑。",
                "通过 `@property` 限制 `temperature` 必须在 `[0.0, 2.0]` 之间，越界抛 `ValueError`；pytest 全绿。"
            ],
            "non_functional": [
                "全离线本地模拟生成，零外部 API Key 依赖。",
                "新增第三家厂商（如 DeepSeekModel）只需新增子类，无需修改路由器代码（开闭原则）。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "继承、super()、ABC 抽象基类与多态思想", "detail": "讲解面向对象三大特性、方法重写（Override）、MRO 查找顺序与多态解耦。"},
            {"slot": "下午 14:00-17:30", "topic": "@property 与魔术方法实战：BaseModel 适配层", "detail": "编写 BaseModel、OpenAIModel、QwenModel 及多模型路由器 ModelRouter。"},
            {"slot": "晚间 19:00-20:30", "topic": "多态与属性越界单元测试", "detail": "用 pytest 验证抽象类防实例化、temperature 越界拦截与多模型无缝切换。"},
            {"slot": "复盘 20:30-21:00", "topic": "开闭原则复盘与课后作业", "detail": "梳理 LangChain BaseChatModel 源码设计共鸣，完成 3 道梯度课后题。"}
        ],
        "architecture_design": (
            "今天的 `BaseModel` 设计就是业界著名的**模板方法 + 策略多态模式**（LangChain 的 `BaseChatModel` 和 LlamaIndex 的 `LLM` 基类都是这个套路）：\n"
            "1. **抽象基类 `BaseModel`（day09_base_model.py）**：统一保管 `model_name`、`temperature`（带 `@property` 范围校验）和调用次数统计 `_call_count`，并定义抽象方法 `generate(prompt)` 与公共魔术方法 `__call__`（让对象可以直接像函数一样 `model('你好')` 调用！）。\n"
            "2. **多态子类与路由层（day09_model_providers.py）**：`OpenAIModel` 和 `QwenModel` 各自通过 `super().__init__()` 复用父类初始化，仅重写厂商专属的鉴权头格式与回复生成逻辑。上层 `ModelRouter` 只面向 `BaseModel` 编程，彻底消灭 `if/elif` 供应商判断。"
        ),
        "diagrams": [
            {
                "title": "多模型统一路由与多态调用流程图",
                "kind": "flowchart",
                "caption": "展示业务请求进入 ModelRouter 后，按名称动态分发给不同厂商子类并统一记账的流程。",
                "nodes": [
                    {"id": "n1", "label": "业务层发起提问", "sub": "router.ask('qwen', prompt)", "color": "#3b82f6"},
                    {"id": "n2", "label": "ModelRouter 查找", "sub": "从注册表获取 BaseModel", "color": "#8b5cf6"},
                    {"id": "n3", "label": "多态调用 model(prompt)", "sub": "触发 __call__ -> generate", "color": "#f59e0b"},
                    {"id": "n4", "label": "子类执行厂商逻辑", "sub": "OpenAIModel / QwenModel", "color": "#10b981"},
                    {"id": "n5", "label": "返回统一响应字典", "sub": "含 provider/model/reply", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "路由寻址"},
                    {"from": "n2", "to": "n3", "label": "统一接口"},
                    {"from": "n3", "to": "n4", "label": "动态分派"},
                    {"from": "n4", "to": "n5", "label": "标准封装"}
                ]
            },
            {
                "title": "BaseModel 继承体系与多态架构图",
                "kind": "architecture",
                "caption": "展示抽象基类 BaseModel 与具体厂商实现类之间的继承与接口契约关系。",
                "nodes": [
                    {"id": "a1", "label": "BaseModel (ABC)", "sub": "@property temperature / __call__", "color": "#8b5cf6"},
                    {"id": "a2", "label": "OpenAIModel", "sub": "Bearer Token + GPT/DeepSeek", "color": "#3b82f6"},
                    {"id": "a3", "label": "QwenModel", "sub": "DashScope + 通义千问系列", "color": "#10b981"},
                    {"id": "a4", "label": "ModelRouter", "sub": "面向 BaseModel 统一调度", "color": "#f59e0b"}
                ],
                "edges": [
                    {"from": "a2", "to": "a1", "label": "继承并实现 generate"},
                    {"from": "a3", "to": "a1", "label": "继承并实现 generate"},
                    {"from": "a4", "to": "a1", "label": "依赖抽象接口"}
                ]
            },
            {
                "title": "@property 读写拦截与校验原理图",
                "kind": "schematic",
                "caption": "展示外部执行 model.temperature = 2.5 时，setter 如何拦截非法赋值并保护私有字段 _temperature。",
                "nodes": [
                    {"id": "s1", "label": "外部赋值", "sub": "model.temperature = val", "color": "#3b82f6"},
                    {"id": "s2", "label": "@temperature.setter", "sub": "检查 0.0 <= val <= 2.0", "color": "#f59e0b"},
                    {"id": "s3", "label": "校验失败", "sub": "抛出 ValueError 拦截", "color": "#ef4444"},
                    {"id": "s4", "label": "校验通过", "sub": "写入 self._temperature", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "自动路由"},
                    {"from": "s2", "to": "s3", "label": "越界拒绝"},
                    {"from": "s2", "to": "s4", "label": "合法更新"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 抽象基类（ABC）与 super() 继承",
                "content": (
                    "继承 `abc.ABC` 并用 `@abstractmethod` 装饰的方法，相当于给所有子类签下「军令状」：子类必须实现该方法，否则无法实例化。"
                    "子类重写 `__init__` 时，务必第一行调用 `super().__init__(...)`，确保父类初始化的属性全部就绪。"
                ),
                "pitfalls": "如果父类定义了 `self.temperature = temperature` 走的是 `@property` setter，那么子类通过 `super().__init__` 传入非法温度值时也会自动触发校验，一处编写全族受益！"
            },
            {
                "heading": "2. @property 让方法像属性一样自然读写",
                "content": (
                    "相比 Java 满屏的 `getTemperature()` / `setTemperature()`，Python 用 `@property` 和 `@temperature.setter` 保持 `obj.temperature` 的简洁语法，同时在背后悄悄完成范围校验或延迟计算。"
                ),
                "pitfalls": "在 setter 里千万不要写 `self.temperature = value`（会无限递归自己调用自己导致 `RecursionError`），必须写入带下划线的底层属性 `self._temperature = value`！"
            },
            {
                "heading": "3. 常用魔术方法（Dunder Methods）",
                "content": (
                    "- `__str__`：面向用户的友好打印（`print(obj)`）；`__repr__`：面向开发者的精确调试展示。\n"
                    "- `__len__`：支持 `len(router)` 查看注册了多少个模型。\n"
                    "- `__call__`：让对象实例可以像函数一样被括号调用 `model('你好')`，PyTorch 的 `nn.Module` 和 LangChain 的 `Runnable` 都在用！"
                ),
                "pitfalls": "重写 `__eq__` 后如果还想把对象放进 `set` 或当作 `dict` 键，必须同时实现 `__hash__`。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：定义星辰智脑抽象基类 BaseModel（含 @property 与魔术方法）",
                "file_path": "src/day09_base_model.py",
                "narration": "先立规矩！定义抽象基类 `BaseModel`，管好 `temperature` 合法范围、统一调用计数与 `__call__` 便捷入口。",
                "code": r'''"""
STARMIND-009 模块一：大模型统一抽象基类 BaseModel。
演示 abc.ABC 抽象基类、@property 范围校验、模板方法与 __call__ / __str__ 魔术方法。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseModel(ABC):
    """星辰智脑所有大模型适配器的抽象基类。"""

    provider: str = "base"

    def __init__(self, model_name: str, temperature: float = 0.7) -> None:
        self.model_name: str = model_name
        # 通过 @temperature.setter 触发构造期范围校验
        self.temperature = temperature
        self._call_count: int = 0

    @property
    def temperature(self) -> float:
        """读取采样温度（只通过受控接口暴露私有字段 _temperature）。"""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """拦截写入：强制限制温度必须在 [0.0, 2.0] 合法区间内。"""
        val = float(value)
        if not (0.0 <= val <= 2.0):
            raise ValueError(f"temperature 必须在 [0.0, 2.0] 之间，当前传入: {val}")
        self._temperature = val

    @property
    def call_count(self) -> int:
        """只读属性：返回当前模型实例累计被调用的次数。"""
        return self._call_count

    @abstractmethod
    def build_headers(self) -> Dict[str, str]:
        """抽象方法：子类必须实现各自厂商的 HTTP 鉴权请求头。"""

    @abstractmethod
    def _do_generate(self, prompt: str) -> str:
        """抽象方法：子类实现具体的文本生成逻辑（本地模拟或真实 API）。"""

    def generate(self, prompt: str) -> Dict[str, Any]:
        """模板方法：统一完成空值检查、计数统计并委托子类生成回复。"""
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("提示词 prompt 不能为空")
        self._call_count += 1
        reply_text = self._do_generate(cleaned)
        return {
            "provider": self.provider,
            "model": self.model_name,
            "temperature": self.temperature,
            "reply": reply_text,
            "call_index": self._call_count,
        }

    def __call__(self, prompt: str) -> Dict[str, Any]:
        """魔术方法：支持直接将模型实例当作函数调用 model('你好')。"""
        return self.generate(prompt)

    def __str__(self) -> str:
        return f"[{self.provider}] {self.model_name} (temp={self.temperature}, calls={self._call_count})"


if __name__ == "__main__":
    print("BaseModel 抽象基类定义完成，禁止直接实例化，请继承后使用。")
''',
                "explanation": (
                    "1. `generate()` 是经典的「模板方法」：把通用的空串校验、调用次数自增、结果字典包装留在父类，只把有差异的 `_do_generate()` 交给子类实现。\n"
                    "2. `call_count` 只定义了 `@property` 没写 setter，天然变成了只读属性，外部无法伪造调用次数。"
                ),
                "expected_output": "BaseModel 抽象基类定义完成，禁止直接实例化，请继承后使用。"
            },
            {
                "step_title": "步骤二：实现 OpenAIModel / QwenModel 多态子类与 ModelRouter",
                "file_path": "src/day09_model_providers.py",
                "narration": "现在让 `OpenAIModel` 和 `QwenModel` 继承 `BaseModel`，再写一个支持 `len(router)` 的 `ModelRouter`，体验一行代码无痛切换模型的丝滑感。",
                "code": r'''"""
STARMIND-009 模块二：OpenAIModel / QwenModel 多态实现与多模型路由器。
演示继承、super() 调用、方法重写、多态分发以及 __len__ / __contains__ 魔术方法。
"""

from typing import Dict, Any
from day09_base_model import BaseModel


class OpenAIModel(BaseModel):
    """OpenAI / DeepSeek 兼容协议适配器（本地离线模拟版）。"""

    provider: str = "openai"

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.7, api_key: str = "mock-openai-key") -> None:
        super().__init__(model_name=model_name, temperature=temperature)
        self._api_key = api_key

    def build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _do_generate(self, prompt: str) -> str:
        return f"[OpenAI:{self.model_name}|t={self.temperature}] 已收到指令「{prompt}」，建议采用结构化分步解答。"


class QwenModel(BaseModel):
    """阿里云通义千问（DashScope）适配器（本地离线模拟版）。"""

    provider: str = "qwen"

    def __init__(self, model_name: str = "qwen-plus", temperature: float = 0.5, api_key: str = "mock-qwen-key") -> None:
        super().__init__(model_name=model_name, temperature=temperature)
        self._api_key = api_key

    def build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "X-DashScope-SSE": "disable",
            "Content-Type": "application/json",
        }

    def _do_generate(self, prompt: str) -> str:
        return f"[通义千问:{self.model_name}|t={self.temperature}] 您好！针对「{prompt}」，星辰智脑中文知识库已为您整理完毕。"


class ModelRouter:
    """多模型统一路由器：面向 BaseModel 抽象接口编程，屏蔽厂商差异。"""

    def __init__(self) -> None:
        self._registry: Dict[str, BaseModel] = {}

    def register(self, alias: str, model: BaseModel) -> None:
        if not isinstance(model, BaseModel):
            raise TypeError("注册对象必须是 BaseModel 的子类实例")
        self._registry[alias] = model

    def ask(self, alias: str, prompt: str) -> Dict[str, Any]:
        if alias not in self._registry:
            raise KeyError(f"未注册的模型别名: {alias}")
        model = self._registry[alias]
        # 多态调用：触发 BaseModel.__call__ -> 具体子类的 _do_generate
        return model(prompt)

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, alias: str) -> bool:
        return alias in self._registry


if __name__ == "__main__":
    router = ModelRouter()
    router.register("fast", OpenAIModel("gpt-4o-mini", temperature=0.3))
    router.register("cn_pro", QwenModel("qwen-plus", temperature=0.5))

    print(f"已注册模型数量: {len(router)} | 包含 cn_pro: {'cn_pro' in router}")
    for alias in ("fast", "cn_pro"):
        res = router.ask(alias, "总结一下杭州星辰数科的核心优势")
        print(f"-> {alias}: {res['reply']}")
''',
                "explanation": (
                    "1. `ModelRouter.register` 用 `isinstance(model, BaseModel)` 守住类型边界，确保只有遵守契约的模型才能注册进来。\n"
                    "2. 实现 `__len__` 和 `__contains__` 后，路由器原生支持 `len(router)` 和 `'cn_pro' in router`，Pythonic 十足。"
                ),
                "expected_output": (
                    "已注册模型数量: 2 | 包含 cn_pro: True\n"
                    "-> fast: [OpenAI:gpt-4o-mini|t=0.3] 已收到指令「总结一下杭州星辰数科的核心优势」，建议采用结构化分步解答。\n"
                    "-> cn_pro: [通义千问:qwen-plus|t=0.5] 您好！针对「总结一下杭州星辰数科的核心优势」，星辰智脑中文知识库已为您整理完毕。"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-009 自动化单元测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day09_base_model import BaseModel
from day09_model_providers import OpenAIModel, QwenModel, ModelRouter


def test_cannot_instantiate_abstract_base_model():
    with pytest.raises(TypeError):
        BaseModel("abstract-only")  # type: ignore


def test_temperature_property_validation():
    m = OpenAIModel("gpt-4o-mini", temperature=0.8)
    assert m.temperature == 0.8
    m.temperature = 0.0
    assert m.temperature == 0.0

    with pytest.raises(ValueError):
        m.temperature = 2.5
    with pytest.raises(ValueError):
        QwenModel("qwen-plus", temperature=-0.1)


def test_polymorphic_router_and_dunder_methods():
    router = ModelRouter()
    oai = OpenAIModel("gpt-4o-mini", temperature=0.2)
    qwen = QwenModel("qwen-max", temperature=0.6)

    router.register("oai", oai)
    router.register("qwen", qwen)
    assert len(router) == 2
    assert "qwen" in router

    r1 = router.ask("oai", "测试多态")
    r2 = router.ask("qwen", "测试多态")
    assert r1["provider"] == "openai" and oai.call_count == 1
    assert r2["provider"] == "qwen" and qwen.call_count == 1
    assert "X-DashScope-SSE" in qwen.build_headers()
    assert "openai" in str(oai)
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "这套 `BaseModel -> OpenAIModel / QwenModel` + `ModelRouter` 已经非常接近生产级 LLM 网关骨架了！模板方法和只读 `call_count` 属性设计得很扎实。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "确认直接实例化 `BaseModel` 会抛 `TypeError`，温度超界会抛 `ValueError`，多态切换无副作用。",
                "resolution": "验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：扩展 DeepSeekModel 子类",
                "difficulty": "基础巩固",
                "requirement": "继承一个简化的 `SimpleBaseLLM`，实现 `DeepSeekModel` 子类，新增 `enable_thinking: bool` 属性；当 `enable_thinking=True` 时，回复前自动加上 `<think>深度推理中...</think>` 前缀。",
                "hint": "在子类 `__init__` 中调用 `super().__init__(model_name)` 并保存 `self.enable_thinking`。",
                "solution_code": r'''"""Day 9 课后题 1：扩展支持思考模式的 DeepSeekModel 子类。"""


class SimpleBaseLLM:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class DeepSeekModel(SimpleBaseLLM):
    def __init__(self, model_name: str = "deepseek-reasoner", enable_thinking: bool = True) -> None:
        super().__init__(model_name)
        self.enable_thinking = enable_thinking

    def generate(self, prompt: str) -> str:
        prefix = "<think>正在拆解问题逻辑...</think> " if self.enable_thinking else ""
        return f"{prefix}[{self.model_name}] 回答: {prompt}"


if __name__ == "__main__":
    ds = DeepSeekModel(enable_thinking=True)
    print(ds.generate("解释什么是多态"))
''',
                "solution_analysis": "考查 `super().__init__` 复用父类初始化以及子类扩展特有行为属性。"
            },
            {
                "title": "企业实战：带只读余额与充值拦截的 ApiWallet 类",
                "difficulty": "企业实战",
                "requirement": "设计 `ApiWallet` 类，使用 `@property` 暴露只读余额 `balance`，提供 `deposit(amount)` 与 `charge(amount)` 方法，禁止负数充值、禁止余额透支。",
                "hint": "底层用 `self._balance` 存储，任何非法金额均抛出 `ValueError`。",
                "solution_code": r'''"""Day 9 课后题 2：受保护的企业 API 余额钱包类。"""


class ApiWallet:
    def __init__(self, initial_balance: float = 0.0) -> None:
        if initial_balance < 0:
            raise ValueError("初始余额不能为负数")
        self._balance = float(initial_balance)

    @property
    def balance(self) -> float:
        return round(self._balance, 4)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("充值金额必须大于 0")
        self._balance += amount

    def charge(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("扣费金额必须大于 0")
        if amount > self._balance:
            raise ValueError(f"余额不足: 当前 {self.balance}，需扣 {amount}")
        self._balance -= amount


if __name__ == "__main__":
    w = ApiWallet(10.0)
    w.deposit(5.5)
    w.charge(3.2)
    print("剩余余额:", w.balance)
''',
                "solution_analysis": "资金与配额类对象绝不允许外部直接赋值 `w.balance = 99999`，必须通过只读 `@property` + 受控方法变更状态。"
            },
            {
                "title": "架构进阶：支持上下文管理器（with 语句）的耗时统计器",
                "difficulty": "架构进阶",
                "requirement": "利用魔术方法 `__enter__` 与 `__exit__` 实现 `TimerContext` 类，使调用方可以用 `with TimerContext('LLM调用') as t:` 自动测量代码块执行耗时（毫秒）。",
                "hint": "`__enter__` 记录 `time.perf_counter()` 并返回 `self`；`__exit__` 计算差值存入 `self.elapsed_ms`。",
                "solution_code": r'''"""Day 9 课后题 3：基于 __enter__ / __exit__ 的模型调用耗时监控器。"""

import time


class TimerContext:
    def __init__(self, label: str) -> None:
        self.label = label
        self.elapsed_ms: float = 0.0
        self._start: float = 0.0

    def __enter__(self) -> "TimerContext":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.elapsed_ms = round((time.perf_counter() - self._start) * 1000.0, 3)
        # 返回 False 表示不吞掉代码块内部的异常
        return False


if __name__ == "__main__":
    with TimerContext("模拟推理") as timer:
        _ = sum(range(10000))
    print(f"[{timer.label}] 耗时: {timer.elapsed_ms} ms")
''',
                "solution_analysis": "掌握上下文管理器协议是读懂数据库连接池、文件句柄、分布式锁源码的必备技能。"
            }
        ],
        "extra_deep_dive": (
            "【源码视角：LangChain 的 `BaseChatModel` 为什么长得跟咱们今天写的这么像？】\n"
            "如果你去翻 LangChain 的核心源码，会发现 `ChatOpenAI`、`ChatTongyi`、`ChatDeepSeek` 全部继承自同一个 `BaseChatModel`，"
            "父类管好了回调、缓存、重试、统一输入输出格式，子类只管实现 `_generate()`！今天你亲手写出的架构，就是一线开源框架的同款基因。"
        )
    },

    # =========================================================================
    # DAY 10: 模块、包与异常处理
    # =========================================================================
    {
        "day": 10,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "模块、包与异常处理",
        "subtitle": "搭建星辰智脑自定义异常体系、模块化包结构与 venv / requirements.txt 工程规范",
        "gitlab_ticket": "STARMIND-010",
        "git_branch": "feat/day10-modules-exceptions-venv",
        "git_commit": "feat(day10): 构建StarMind自定义异常层级、降级容错执行器与依赖清单校验工具",
        "prev_recap": "昨天咱们用继承和多态搭出了多模型适配层，但目前还没处理调用超时、限流、密钥无效等生产异常。",
        "next_preview": "明天（Day 11）咱们学习文件操作（txt/csv/json）与 os/pathlib/datetime/re 常用标准库，给星辰智脑打造批量文档读取与关键词统计工具。",
        "narrator_opening": (
            "聊个真事：去年隔壁部门一个新人把 `try: ... except: pass` 写进了线上 AI 服务里，结果 API 密钥过期了整整两天，用户全收到空回复，监控一条报警都没发，复盘会被批得体无完肤！"
            "记住老陈的红线：**裸 `except:` 吞掉所有异常是大厂头号大忌！**\n"
            "今天 STARMIND-010 咱们干两件让项目真正具备「工程化骨架」的事：\n"
            "1）吃透 Python 的模块（Module）、包（Package / `__init__.py`）、虚拟环境 `venv` 与 `requirements.txt` 依赖锁规范；\n"
            "2）为星辰智脑设计一套层次清晰的自定义异常树（`StarMindError -> RateLimitError / AuthError / ContextLengthError`），并写出支持「主模型限流自动切备用模型」的容错调度器！"
        ),
        "narrator_closing": (
            "今天这套自定义异常体系 + 自动降级容错器，才是真正的企业级 AI 工程思维。"
            "记住三条铁律：1）异常要精准捕获，绝不 `except: pass`；2）区分可重试/可降级异常（如 429 限流）与致命异常（如 401 鉴权失败）；3）每个独立项目必建专属 `venv` 并导出 `requirements.txt`。"
        ),
        "business_prd": {
            "background": "星辰智脑接入多模型后，生产环境频繁面临上游 429 限流、401 密钥失效、输入超长等故障，需要统一的自定义异常体系、优雅降级机制与标准化依赖隔离方案。",
            "pain_points": [
                "所有错误都抛出泛化的 `Exception`，调用方无法区分该重试、该切模型还是该立即报警。",
                "裸 `except Exception: pass` 掩盖了真实故障根因。",
                "团队成员全局 pip 装包互相打架，缺少 `venv` 与 `requirements.txt` 规范检查。"
            ],
            "goals": [
                "掌握 `import` 搜索路径、包结构（`__init__.py`）、`venv` 虚拟环境与 `requirements.txt` 管理。",
                "熟练运用 `try / except / else / finally` 与 `raise ... from exc` 异常链保留原始堆栈。",
                "设计 `StarMindError` 自定义异常层级并实现主备模型自动降级执行器。"
            ],
            "acceptance_criteria": [
                "自定义异常树包含 `StarMindError` 基类及 `AuthError`、`RateLimitError`、`ModelTimeoutError` 子类，携带 `error_code` 与 `retryable` 标记。",
                "容错执行器在主模型抛出 `RateLimitError` 时自动无缝切换至备用模型；遇到 `AuthError` 时立即向上抛出不盲目降级。",
                "依赖清单解析工具能校验 `requirements.txt` 是否锁定版本号，pytest 全绿。"
            ],
            "non_functional": [
                "严禁使用裸 `except:`，所有异常流转均有结构化日志记录。",
                "完整保留异常上下文链，便于排查根因。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "模块/包机制、sys.path 与 venv 依赖隔离", "detail": "讲解绝对导入 vs 相对导入、`__name__ == '__main__'`、`python -m venv` 与 `pip freeze`。"},
            {"slot": "下午 14:00-17:30", "topic": "异常处理机制与自定义异常体系实战", "detail": "编写 StarMind 异常树、主备模型容错降级器与 requirements.txt 合规扫描器。"},
            {"slot": "晚间 19:00-20:30", "topic": "故障注入单元测试（Fault Injection）", "detail": "用 pytest 模拟主模型限流、超时、鉴权失败与全链路故障等 4 种灾难场景。"},
            {"slot": "复盘 20:30-21:00", "topic": "异常最佳实践复盘与课后题", "detail": "总结 try/except/else/finally 执行顺序，完成 3 道梯度课后作业。"}
        ],
        "architecture_design": (
            "在大厂微服务与 AI 网关架构中，异常不是「程序崩了」，而是「受控的业务控制流协议」：\n"
            "1. **分层异常体系（day10_exceptions.py）**：所有业务异常继承自 `StarMindError`，并内置 `code`（如 `E429`、`E401`）和 `retryable: bool` 元数据。上游框架只需要检查 `exc.retryable`，就能决定走降级重试还是直接熔断告警。\n"
            "2. **主备降级与依赖审计层（day10_resilient_runner.py）**：利用 `try / except / else / finally` 实现主模型调用、限流/超时自动切备用模型、审计收尾；附带 `audit_requirements_text` 帮团队在 CI 阶段拦截未锁版本的 `requirements.txt`。"
        ),
        "diagrams": [
            {
                "title": "主备模型异常捕获与自动降级流程图",
                "kind": "flowchart",
                "caption": "展示主模型遭遇可重试故障时如何自动切换至备用模型，而遭遇鉴权错误时快速失败。",
                "nodes": [
                    {"id": "n1", "label": "调用主模型", "sub": "try: primary(prompt)", "color": "#3b82f6"},
                    {"id": "n2", "label": "成功返回", "sub": "else: 记录主通道成功", "color": "#10b981"},
                    {"id": "n3", "label": "捕获可重试异常", "sub": "RateLimit / Timeout", "color": "#f59e0b"},
                    {"id": "n4", "label": "切换备用模型", "sub": "fallback(prompt)", "color": "#8b5cf6"},
                    {"id": "n5", "label": "捕获不可重试异常", "sub": "AuthError 直接上抛", "color": "#ef4444"},
                    {"id": "n6", "label": "finally 清理审计", "sub": "无论成败必记账", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "无异常"},
                    {"from": "n1", "to": "n3", "label": "限流/超时"},
                    {"from": "n3", "to": "n4", "label": "自动降级"},
                    {"from": "n1", "to": "n5", "label": "401 鉴权错"},
                    {"from": "n2", "to": "n6", "label": "收尾"},
                    {"from": "n4", "to": "n6", "label": "收尾"}
                ]
            },
            {
                "title": "StarMind 多文件工程包与 venv 隔离架构图",
                "kind": "architecture",
                "caption": "展示标准 Python 项目的虚拟环境、依赖锁文件与多模块包目录组织方式。",
                "nodes": [
                    {"id": "a1", "label": ".venv 虚拟环境", "sub": "隔离项目专属 Python/pip", "color": "#3b82f6"},
                    {"id": "a2", "label": "requirements.txt", "sub": "精确锁定包版本 ==x.y.z", "color": "#f59e0b"},
                    {"id": "a3", "label": "starmind/ 包", "sub": "__init__.py + exceptions.py", "color": "#8b5cf6"},
                    {"id": "a4", "label": "tests/ 测试包", "sub": "pytest 自动化故障注入", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "a2", "to": "a1", "label": "pip install -r"},
                    {"from": "a1", "to": "a3", "label": "运行时解释"},
                    {"from": "a4", "to": "a3", "label": "import 验证"}
                ]
            },
            {
                "title": "StarMind 自定义异常继承层级示意图",
                "kind": "schematic",
                "caption": "清晰的异常继承树让上层代码既能按基类兜底捕获，也能按具体子类精细化处理。",
                "nodes": [
                    {"id": "s1", "label": "Exception", "sub": "Python 内置异常基类", "color": "#64748b"},
                    {"id": "s2", "label": "StarMindError", "sub": "平台根异常 (code, retryable)", "color": "#3b82f6"},
                    {"id": "s3", "label": "RateLimitError", "sub": "E429, retryable=True", "color": "#f59e0b"},
                    {"id": "s4", "label": "ModelTimeoutError", "sub": "E504, retryable=True", "color": "#8b5cf6"},
                    {"id": "s5", "label": "AuthError", "sub": "E401, retryable=False", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "s2", "to": "s1", "label": "继承"},
                    {"from": "s3", "to": "s2", "label": "继承"},
                    {"from": "s4", "to": "s2", "label": "继承"},
                    {"from": "s5", "to": "s2", "label": "继承"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 模块、包与 __name__ == '__main__'",
                "content": (
                    "一个 `.py` 文件就是一个模块（Module）；包含 `__init__.py` 的文件夹就是一个包（Package）。"
                    "每个模块都应把演示代码放进 `if __name__ == '__main__':` 块里，否则别人 `import` 你的模块时会意外执行你的演示打印甚至触发网络请求！"
                ),
                "pitfalls": "切忌把自己的业务文件命名为 `json.py`、`random.py` 或 `requests.py`！那会遮蔽（Shadow）同名标准库或第三方库，引发极其诡异的 `AttributeError`。"
            },
            {
                "heading": "2. try / except / else / finally 完整语义",
                "content": (
                    "- `try`：放可能出错的最小范围代码；\n"
                    "- `except SpecificError as e`：精准捕获并处理；\n"
                    "- `else`：仅当 `try` 块**完全没有异常**时执行；\n"
                    "- `finally`：**无论是否发生异常（甚至有 return）**都必然执行，用来关闭文件、释放锁、记录审计日志。"
                ),
                "pitfalls": "重新包装异常时务必使用 `raise StarMindError('调用失败') from orig_exc`，这样 traceback 会保留原始报错链，排查效率翻倍。"
            },
            {
                "heading": "3. venv 虚拟环境与 requirements.txt",
                "content": (
                    "标准三步：`python3 -m venv .venv` 创建隔离环境 -> 激活后安装依赖 -> `pip freeze > requirements.txt` 锁定版本。"
                    "团队新人拉下代码后只需 `pip install -r requirements.txt` 即可 100% 复现一致环境。"
                ),
                "pitfalls": "千万别在 `requirements.txt` 里只写包名不锁版本（如只写 `pydantic`），某天上游发了个不兼容大版本，你的线上镜像一重新构建直接挂掉！"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：构建星辰智脑自定义异常体系",
                "file_path": "src/day10_exceptions.py",
                "narration": "先建异常树！给每个异常挂上标准错误码 `code` 和 `retryable` 标记，让下游调用方一眼看懂该不该重试或降级。",
                "code": r'''"""
STARMIND-010 模块一：星辰智脑自定义异常体系。
演示异常类继承、结构化错误元数据（code/retryable）以及标准错误字典序列化。
"""

from typing import Dict, Any


class StarMindError(Exception):
    """星辰智脑平台所有业务异常的统一基类。"""

    code: str = "E500"
    retryable: bool = False

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def to_error_dict(self) -> Dict[str, Any]:
        """将异常转为前后端统一的 JSON 错误响应结构。"""
        return {
            "ok": False,
            "error_code": self.code,
            "message": self.message,
            "detail": self.detail,
            "retryable": self.retryable,
        }


class RateLimitError(StarMindError):
    """上游大模型触发限流（HTTP 429），支持退避重试或切备用模型。"""

    code = "E429"
    retryable = True


class ModelTimeoutError(StarMindError):
    """上游大模型推理超时（HTTP 504），支持降级重试。"""

    code = "E504"
    retryable = True


class AuthError(StarMindError):
    """API Key 无效或已过期（HTTP 401），不可重试，需立即告警人工介入。"""

    code = "E401"
    retryable = False


if __name__ == "__main__":
    err = RateLimitError("DeepSeek 主通道触发 TPM 限流", detail="retry-after: 3s")
    print("异常字典:", err.to_error_dict())
''',
                "explanation": (
                    "给异常加上 `to_error_dict()` 后，后续在 Day 23 写 FastAPI 接口时，全局异常处理器可以直接把异常对象一键转成规范的 JSON 错误响应。"
                ),
                "expected_output": (
                    "异常字典: {'ok': False, 'error_code': 'E429', 'message': 'DeepSeek 主通道触发 TPM 限流', 'detail': 'retry-after: 3s', 'retryable': True}"
                )
            },
            {
                "step_title": "步骤二：实现主备模型容错降级器与 requirements.txt 审计工具",
                "file_path": "src/day10_resilient_runner.py",
                "narration": "现在把 `try / except / else / finally` 用到极致：主模型限流或超时自动切备用模型，401 鉴权错立刻熔断报警，同时附带一个 CI 依赖锁检查器。",
                "code": r'''"""
STARMIND-010 模块二：主备模型容错执行器与 requirements.txt 规范审计工具。
演示 try/except/else/finally、精准异常分流、异常链 raise...from 与工程依赖检查。
"""

from typing import Callable, Dict, Any, List
from day10_exceptions import StarMindError, AuthError


def call_with_fallback(
    primary_fn: Callable[[str], str],
    fallback_fn: Callable[[str], str],
    prompt: str,
) -> Dict[str, Any]:
    """
    高可用模型调用调度器：
    - 主模型正常：直接返回 primary 结果；
    - 主模型抛出可重试 StarMindError（如 RateLimitError/Timeout）：自动降级至备用模型；
    - 主模型抛出 AuthError 等不可重试异常：立即透传上抛，绝不掩盖根因。
    """
    audit_events: List[str] = []
    try:
        audit_events.append("try_primary")
        reply = primary_fn(prompt)
    except AuthError:
        # 鉴权失败属于配置事故，不降级直接暴露
        audit_events.append("auth_abort")
        raise
    except StarMindError as exc:
        if not exc.retryable:
            audit_events.append("non_retryable_abort")
            raise
        # 可重试/可降级异常：自动切换备用模型
        audit_events.append(f"fallback_on_{exc.code}")
        try:
            reply = fallback_fn(prompt)
            channel = "fallback"
        except Exception as fb_exc:
            raise StarMindError("主备模型均调用失败", detail=str(fb_exc)) from fb_exc
    else:
        # 仅当 try 块完全无异常时执行
        channel = "primary"
        audit_events.append("primary_ok")
    finally:
        # 无论成功、降级还是抛异常，审计收尾钩子必然执行
        audit_events.append("audit_closed")

    return {
        "ok": True,
        "channel": channel,
        "reply": reply,
        "audit_events": audit_events,
    }


def audit_requirements_text(req_content: str) -> Dict[str, List[str]]:
    """检查 requirements.txt 文本，识别已锁版本与未锁版本的风险依赖。"""
    pinned: List[str] = []
    unpinned: List[str] = []
    for raw_line in req_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" in line:
            pinned.append(line)
        else:
            unpinned.append(line)
    return {"pinned": pinned, "unpinned": unpinned}


if __name__ == "__main__":
    from day10_exceptions import RateLimitError

    def mock_primary(_p: str) -> str:
        raise RateLimitError("主通道 429 限流")

    def mock_fallback(p: str) -> str:
        return f"[备用通义千问兜底] 已处理: {p}"

    print("降级结果:", call_with_fallback(mock_primary, mock_fallback, "查询报销流程"))
    sample_req = "# 核心依赖\nfastapi==0.115.0\npydantic\nuvicorn==0.30.0\n"
    print("依赖审计:", audit_requirements_text(sample_req))
''',
                "explanation": (
                    "1. 注意 `except AuthError:` 写在 `except StarMindError:` 前面——因为 `AuthError` 是 `StarMindError` 的子类，异常捕获必须遵循「先子类、后父类」的顺序。\n"
                    "2. `raise StarMindError(...) from fb_exc` 保留了备用模型崩溃的原始原因，线上排障一目了然。"
                ),
                "expected_output": (
                    "降级结果: {'ok': True, 'channel': 'fallback', 'reply': '[备用通义千问兜底] 已处理: 查询报销流程', 'audit_events': ['try_primary', 'fallback_on_E429', 'audit_closed']}\n"
                    "依赖审计: {'pinned': ['fastapi==0.115.0', 'uvicorn==0.30.0'], 'unpinned': ['pydantic']}"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-010 自动化单元测试（含故障注入）。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day10_exceptions import StarMindError, RateLimitError, ModelTimeoutError, AuthError
from day10_resilient_runner import call_with_fallback, audit_requirements_text


def test_primary_success():
    res = call_with_fallback(lambda p: f"P:{p}", lambda p: f"F:{p}", "hi")
    assert res["channel"] == "primary"
    assert res["reply"] == "P:hi"
    assert res["audit_events"] == ["try_primary", "primary_ok", "audit_closed"]


def test_fallback_on_rate_limit_and_timeout():
    def fail_429(_p):
        raise RateLimitError("too many requests")

    def fail_504(_p):
        raise ModelTimeoutError("gateway timeout")

    r1 = call_with_fallback(fail_429, lambda p: f"BACKUP:{p}", "hello")
    assert r1["channel"] == "fallback"
    assert "fallback_on_E429" in r1["audit_events"]

    r2 = call_with_fallback(fail_504, lambda p: f"BACKUP:{p}", "hello")
    assert r2["channel"] == "fallback"
    assert "fallback_on_E504" in r2["audit_events"]


def test_auth_error_never_falls_back():
    def fail_401(_p):
        raise AuthError("invalid key")

    with pytest.raises(AuthError) as exc_info:
        call_with_fallback(fail_401, lambda p: "should not run", "hello")
    assert exc_info.value.to_error_dict()["error_code"] == "E401"


def test_audit_requirements_text():
    res = audit_requirements_text("# comment\npytest==8.3.0\nhttpx\n")
    assert res["pinned"] == ["pytest==8.3.0"]
    assert res["unpinned"] == ["httpx"]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "异常捕获先子类 AuthError 再父类 StarMindError，结构非常严谨；`raise ... from` 保留根因链也很到位。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (QA 测试)",
                "role": "QA Verification",
                "comment": "4 组故障注入用例（正常、429 降级、504 降级、401 快速失败）全部通过。",
                "resolution": "验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：安全数值解析器",
                "difficulty": "基础巩固",
                "requirement": "编写 `safe_parse_int(value: str, default: int = 0) -> int`，尝试将字符串转为整数，捕获 `ValueError` 和 `TypeError` 返回默认值（绝不使用裸 `except:`）。",
                "hint": "使用 `except (ValueError, TypeError):` 同时精准捕获两种异常。",
                "solution_code": r'''"""Day 10 课后题 1：精准异常捕获的安全整数解析器。"""


def safe_parse_int(value: object, default: int = 0) -> int:
    """将任意输入安全解析为整数，失败时返回 default。"""
    try:
        return int(value)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


if __name__ == "__main__":
    for sample in ["42", "3.14", "abc", None]:
        print(f"{sample!r:8s} -> {safe_parse_int(sample, default=-1)}")
''',
                "solution_analysis": "演示元组形式同时捕获多种指定异常 `except (ValueError, TypeError)`，既安全又不会误吞 `KeyboardInterrupt`。"
            },
            {
                "title": "企业实战：带最大重试次数的同步重试函数",
                "difficulty": "企业实战",
                "requirement": "编写 `retry_call(fn, max_attempts=3)`，当 `fn()` 抛出 `TimeoutError` 时自动重试，若超过最大次数仍失败则将最后一次异常抛出。",
                "hint": "循环 `range(1, max_attempts + 1)`，在最后一次迭代直接 `raise`。",
                "solution_code": r'''"""Day 10 课后题 2：指定异常重试执行器。"""

from typing import Callable, TypeVar

T = TypeVar("T")


def retry_call(fn: Callable[[], T], max_attempts: int = 3) -> T:
    """遇到 TimeoutError 时自动重试，最多执行 max_attempts 次。"""
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except TimeoutError:
            if attempt == max_attempts:
                raise
    raise RuntimeError("unreachable")


if __name__ == "__main__":
    state = {"count": 0}

    def flaky_api() -> str:
        state["count"] += 1
        if state["count"] < 3:
            raise TimeoutError(f"第 {state['count']} 次超时")
        return "第 3 次调用成功！"

    print(retry_call(flaky_api, max_attempts=3))
''',
                "solution_analysis": "这是后续 Day 13 装饰器版重试与 `tenacity` 库的原型，注意最后一次失败必须原样 `raise` 保留完整堆栈。"
            },
            {
                "title": "架构进阶：自定义上下文超长异常与自动截断恢复",
                "difficulty": "架构进阶",
                "requirement": "定义 `ContextOverflowError(StarMindError)` 携带 `max_chars` 属性；编写调用包装器，当捕获到该异常时自动将 prompt 截断至 `max_chars` 后重新调用一次。",
                "hint": "捕获 `ContextOverflowError as e:` 后用 `prompt[:e.max_chars]` 二次尝试。",
                "solution_code": r'''"""Day 10 课后题 3：上下文超长自愈恢复机制。"""


class ContextOverflowError(Exception):
    def __init__(self, max_chars: int) -> None:
        super().__init__(f"上下文超过最大长度 {max_chars}")
        self.max_chars = max_chars


def invoke_with_auto_truncate(model_fn, prompt: str) -> str:
    try:
        return model_fn(prompt)
    except ContextOverflowError as exc:
        trimmed = prompt[: exc.max_chars]
        return model_fn(trimmed)


if __name__ == "__main__":
    def strict_model(text: str) -> str:
        if len(text) > 10:
            raise ContextOverflowError(max_chars=10)
        return f"OK({text})"

    print(invoke_with_auto_truncate(strict_model, "这是一段超过十个字符的长提问文本"))
''',
                "solution_analysis": "异常对象携带业务参数 `max_chars`，让外层容错逻辑具备「自愈能力」，非常贴近真实 LLM 网关处理超长上下文的做法。"
            }
        ],
        "extra_deep_dive": (
            "【生产血泪教训：循环导入（Circular Import）怎么破？】\n"
            "项目文件一多，经常出现 `a.py` import `b.py`，`b.py` 又 import `a.py`，一运行直接 `ImportError: cannot import name ... from partially initialized module`。\n"
            "大厂根治三板斧：1）把公共类型、常量、异常抽到最底层独立的 `exceptions.py` / `schemas.py`；2）保证模块依赖是单向有向无环图（DAG）；3）仅做类型标注时用 `if TYPE_CHECKING:` 延迟导入。"
        )
    },

    # =========================================================================
    # DAY 11: 文件操作与常用标准库
    # =========================================================================
    {
        "day": 11,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "文件操作与常用标准库",
        "subtitle": "精通 pathlib/csv/json/datetime/re，打造星辰知识库批量文档扫描与关键词统计引擎",
        "gitlab_ticket": "STARMIND-011",
        "git_branch": "feat/day11-files-stdlib-kb-scanner",
        "git_commit": "feat(day11): 实现基于pathlib/re/csv/datetime的批量文档读取与关键词统计导出工具",
        "prev_recap": "昨天咱们搭好了 StarMind 自定义异常体系和主备容错调度器，工程骨架已经立起来了。",
        "next_preview": "明天（Day 12）激动人心的时刻到了——咱们学习 HTTP 协议与 API 调用，亲手对接 DeepSeek / 通义千问协议写出第一版命令行 AI 问答小程序！",
        "narrator_opening": (
            "今天咱们把 Python「自带电池（Batteries Included）」的威力彻底释放出来！"
            "星辰数科知识库目录里躺着上百份 `.txt` 和 `.md` 制度文档，林产品想做一个上线前的数据摸底（STARMIND-011）："
            "自动递归扫描整个文件夹，用正则表达式提取所有文档里的邮箱、工单号和核心关键词出现频次，打上 `datetime` 时间戳，最终同时导出 JSON 摘要报告和给运营看的 CSV 报表！"
            "今天你学会了 `pathlib`、`csv`、`datetime` 和 `re` 正则这四把标准库神兵，以后做 RAG 批量文档导入轻轻松松。"
        ),
        "narrator_closing": (
            "记住今天的两条现代 Python 铁律：1）写路径操作无脑用 `pathlib.Path`，彻底告别满屏 `os.path.join` 的斜杠地狱；"
            "2）写 CSV 报表在 Windows 下如果怕 Excel 打开中文乱码，把编码设为 `utf-8-sig`（带 BOM 的 UTF-8），运营同学双击打开绝不乱码！"
            "明天咱们就要联网调大模型 API 了，保持状态！"
        ),
        "business_prd": {
            "background": "在搭建 RAG 知识库前，运营与算法团队需要对存量散落的本地 Markdown/TXT 文档进行批量内容扫描、敏感信息抽检与高频业务词统计，并生成可供 Excel 打开的 CSV 统计表。",
            "pain_points": [
                "人工逐个打开几十份文档统计关键词效率极低且易漏。",
                "Windows 与 Linux 路径分隔符不一致（`\\` vs `/`），硬编码路径跨平台必挂。",
                "缺少使用正则表达式批量抽取文档中隐藏的手机号、邮箱与工单编号的能力。"
            ],
            "goals": [
                "掌握 `with open(..., encoding='utf-8')`、`pathlib.Path` 跨平台目录遍历与文件读写。",
                "熟练使用 `csv.DictWriter/DictReader`、`datetime` 时间戳格式化与 `re` 正则表达式。",
                "交付批量文档扫描、关键词频次统计、实体抽取与 CSV/JSON 双格式报表导出工具。"
            ],
            "acceptance_criteria": [
                "能递归扫描指定目录下所有 `.txt` / `.md` 文件并正确统计字符数与指定关键词命中次数。",
                "能用正则准确提取文档中出现的邮箱地址与 `STARMIND-xxx` 工单号。",
                "能将统计结果无乱码导出为 CSV 与 JSON 报告，并在隔离 `tmp_path` 下通过 pytest。"
            ],
            "non_functional": [
                "全流程使用 `pathlib.Path` 保证 Windows/macOS/Linux 跨平台一致。",
                "CSV 写出使用 `newline=''` 防止 Windows 出现多余空行。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "pathlib 现代路径操作与 txt/csv/json 读写", "detail": "对比 os.path 与 pathlib，精讲 with 上下文自动关闭句柄、UTF-8 编码与 csv.DictWriter。"},
            {"slot": "下午 14:00-17:30", "topic": "datetime 时间处理与 re 正则表达式实战", "detail": "编写知识库批量文档扫描器、正则实体抽取器与双格式报表导出器。"},
            {"slot": "晚间 19:00-20:30", "topic": "跨平台文件读写单元测试", "detail": "用 pytest + tmp_path 构造多层测试文档树，验证扫描统计与 CSV/JSON 导出。"},
            {"slot": "复盘 20:30-21:00", "topic": "常用正则速查表整理与课后题", "detail": "整理邮箱/手机号/工单号/Markdown代码块提取正则，完成 3 道课后作业。"}
        ],
        "architecture_design": (
            "本模块是后续第三阶段 RAG「文档加载器（Document Loader）」的直接前身，采用清晰的两段式流水线：\n"
            "1. **正则实体抽取与文本分析器（day11_regex_extractor.py）**：预编译（`re.compile`）常用业务正则表达式（邮箱、工单号、中国大陆手机号），提供高性能的单文档统计与实体提取纯函数。\n"
            "2. **批量目录扫描与报表导出器（day11_doc_scanner.py）**：基于 `pathlib.Path.rglob('*')` 递归发现目标扩展名文件，逐个调用分析器收集指标，打上 `datetime` 生成时间，分别写入 `.csv`（含 `newline=''`）和 `.json` 报表。"
        ),
        "diagrams": [
            {
                "title": "批量文档扫描与关键词统计导出流程图",
                "kind": "flowchart",
                "caption": "展示从递归发现本地文档、正则实体抽取、关键词计数到双格式报表落盘的完整数据流。",
                "nodes": [
                    {"id": "n1", "label": "Path.rglob 扫描", "sub": "筛选 .txt / .md 文件", "color": "#3b82f6"},
                    {"id": "n2", "label": "UTF-8 安全读取", "sub": "with open 自动关句柄", "color": "#8b5cf6"},
                    {"id": "n3", "label": "re 正则与关键词统计", "sub": "提取工单/邮箱/词频", "color": "#f59e0b"},
                    {"id": "n4", "label": "datetime 打标汇总", "sub": "记录扫描时间与总览", "color": "#06b6d4"},
                    {"id": "n5", "label": "导出 CSV + JSON", "sub": "运营表格 + 程序接口", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "文件路径列表"},
                    {"from": "n2", "to": "n3", "label": "文档正文"},
                    {"from": "n3", "to": "n4", "label": "单文件指标"},
                    {"from": "n4", "to": "n5", "label": "持久化报表"}
                ]
            },
            {
                "title": "Python 常用标准库协作架构图",
                "kind": "architecture",
                "caption": "展示 pathlib、re、csv、json、datetime 五大高频标准库在文档处理系统中的职责分工。",
                "nodes": [
                    {"id": "a1", "label": "pathlib", "sub": "跨平台路径与递归扫描", "color": "#3b82f6"},
                    {"id": "a2", "label": "re 正则引擎", "sub": "模式匹配与实体抽取", "color": "#8b5cf6"},
                    {"id": "a3", "label": "datetime", "sub": "ISO 时间戳与审计记录", "color": "#f59e0b"},
                    {"id": "a4", "label": "csv & json", "sub": "表格报表与结构化落盘", "color": "#10b981"},
                    {"id": "a5", "label": "DocScanner 引擎", "sub": "组合编排输出报告", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "a1", "to": "a5", "label": "文件发现"},
                    {"from": "a2", "to": "a5", "label": "内容抽取"},
                    {"from": "a3", "to": "a5", "label": "时间标记"},
                    {"from": "a4", "to": "a5", "label": "双格式导出"}
                ]
            },
            {
                "title": "正则表达式编译与匹配工作原理解析图",
                "kind": "schematic",
                "caption": "以 STARMIND-\\d{3} 为例展示预编译 Pattern 对象如何避免循环内重复编译正则带来的性能浪费。",
                "nodes": [
                    {"id": "s1", "label": "正则模板字符串", "sub": "r'STARMIND-\\d{3}'", "color": "#3b82f6"},
                    {"id": "s2", "label": "re.compile() 预编译", "sub": "生成可复用 Pattern 状态机", "color": "#8b5cf6"},
                    {"id": "s3", "label": "pattern.findall(text)", "sub": "扫描千份文档零重复编译", "color": "#f59e0b"},
                    {"id": "s4", "label": "去重排序结果", "sub": "['STARMIND-001', ...]", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "模块加载时一次编译"},
                    {"from": "s2", "to": "s3", "label": "高速复用匹配"},
                    {"from": "s3", "to": "s4", "label": "输出命中集合"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. pathlib.Path：现代 Python 文件路径唯一推荐写法",
                "content": (
                    "用 `/` 运算符优雅拼接路径：`base = Path('data') / 'kb' / 'guide.md'`；"
                    "常用属性与方法：`.exists()`、`.suffix`（扩展名）、`.stem`（不含扩展名的文件名）、`.read_text(encoding='utf-8')`、`.rglob('*.md')` 递归搜索。"
                ),
                "pitfalls": "尽量避免手写反斜杠 `'C:\\new\\test.txt'`（`\\n` 和 `\\t` 会被当成转义符），用 `Path` 或原始字符串 `r'...'` 彻底免疫转义坑。"
            },
            {
                "heading": "2. CSV 读写与 Excel 中文防乱码技巧",
                "content": (
                    "写 CSV 务必用 `open(path, 'w', encoding='utf-8-sig', newline='')` 搭配 `csv.DictWriter`。"
                    "其中 `newline=''` 交给 csv 模块自己控制换行，避免 Windows 下每两行之间多出一条空白行；`utf-8-sig` 带 BOM 头，微软 Excel 直接双击打开不乱码。"
                ),
                "pitfalls": "用 `csv.DictReader` 读回数据时，所有列默认都是字符串 `str`，数值列记得手动 `int()` / `float()` 转换。"
            },
            {
                "heading": "3. re 正则表达式与 datetime 时区意识",
                "content": (
                    "正则字符串一律加 `r` 前缀（原始字符串），高频函数：`re.findall` 提取全部、`re.sub` 替换脱敏、`re.compile` 预编译提速。"
                    "时间处理在 Python 3.11+ 推荐 `datetime.now(timezone.utc)`（带时区感知），避免使用已废弃的 `datetime.utcnow()`。"
                ),
                "pitfalls": "正则表达式里的 `.*` 默认是**贪婪匹配**，提取两个标签之间的内容时请用非贪婪 `.*?`，否则会把整篇文章吞成一大段！"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：编写预编译正则实体抽取与关键词频次分析器",
                "file_path": "src/day11_regex_extractor.py",
                "narration": "先用 `re.compile` 预编译好星辰数科常用的邮箱、工单号和关键词统计函数，单文档分析逻辑全部做成纯函数。",
                "code": r'''"""
STARMIND-011 模块一：预编译正则实体抽取与关键词频次统计器。
演示 re.compile、re.findall、大小写不敏感匹配与边界词频统计。
"""

import re
from typing import Dict, List, Any

# 预编译高频业务正则表达式，批量扫描时避免重复编译开销
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
TICKET_PATTERN = re.compile(r"STARMIND-\d{3,4}", re.IGNORECASE)


def extract_entities(text: str) -> Dict[str, List[str]]:
    """从文档正文中抽取去重排序后的邮箱地址与星辰工单号。"""
    emails = sorted(set(EMAIL_PATTERN.findall(text)))
    # 工单号统一标准化为大写
    tickets = sorted({t.upper() for t in TICKET_PATTERN.findall(text)})
    return {"emails": emails, "tickets": tickets}


def count_keywords(text: str, keywords: List[str]) -> Dict[str, int]:
    """统计指定关键词列表在文本中出现的总次数（大小写不敏感）。"""
    lowered = text.lower()
    counts: Dict[str, int] = {}
    for kw in keywords:
        clean_kw = kw.strip()
        if not clean_kw:
            continue
        counts[clean_kw] = lowered.count(clean_kw.lower())
    return counts


def analyze_document_text(name: str, text: str, keywords: List[str]) -> Dict[str, Any]:
    """汇总单篇文档的字数、行数、实体及关键词命中明细。"""
    entities = extract_entities(text)
    kw_counts = count_keywords(text, keywords)
    return {
        "file_name": name,
        "char_count": len(text),
        "line_count": len(text.splitlines()),
        "emails": entities["emails"],
        "tickets": entities["tickets"],
        "keyword_counts": kw_counts,
        "total_keyword_hits": sum(kw_counts.values()),
    }


if __name__ == "__main__":
    sample = "需求 STARMIND-011 由 lin@starmind.cn 提出，关联 starmind-005，重点关注 RAG 与 Python 性能优化。"
    print(analyze_document_text("demo.md", sample, ["RAG", "Python", "Agent"]))
''',
                "explanation": (
                    "1. `re.compile` 放在模块顶层，程序启动只编译一次，后续扫描一万份文档速度极快。\n"
                    "2. 工单号正则加了 `re.IGNORECASE`，然后统一 `.upper()` 归一化，防止文档里有人手滑写成 `starmind-005` 漏统计。"
                ),
                "expected_output": (
                    "{'file_name': 'demo.md', 'char_count': 54, 'line_count': 1, 'emails': ['lin@starmind.cn'], 'tickets': ['STARMIND-005', 'STARMIND-011'], 'keyword_counts': {'RAG': 1, 'Python': 1, 'Agent': 0}, 'total_keyword_hits': 2}"
                )
            },
            {
                "step_title": "步骤二：实现批量文档递归扫描器与 CSV / JSON 双格式报表导出",
                "file_path": "src/day11_doc_scanner.py",
                "narration": "现在把 `pathlib`、`csv`、`json`、`datetime` 串起来，实现目录批量扫描并一键生成运营 CSV 和系统 JSON 报告。",
                "code": r'''"""
STARMIND-011 模块二：知识库批量文档扫描与 CSV/JSON 双报表导出器。
演示 pathlib.Path 递归扫描、datetime 时区时间戳、csv.DictWriter(utf-8-sig) 与 json.dump。
"""

import csv
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

from day11_regex_extractor import analyze_document_text

SUPPORTED_SUFFIXES: Tuple[str, ...] = (".txt", ".md")


def scan_directory(root_dir: Path, keywords: List[str]) -> Dict[str, Any]:
    """递归扫描目录下所有 .txt / .md 文件，生成完整统计报告。"""
    if not root_dir.exists() or not root_dir.is_dir():
        raise FileNotFoundError(f"扫描目录不存在: {root_dir}")

    doc_reports: List[Dict[str, Any]] = []
    global_keyword_totals: Dict[str, int] = {kw: 0 for kw in keywords}

    # 使用 pathlib.rglob 递归遍历并按相对路径排序，确保结果稳定
    matched_files = sorted(
        p for p in root_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )

    for file_path in matched_files:
        text = file_path.read_text(encoding="utf-8")
        rel_name = file_path.relative_to(root_dir).as_posix()
        report = analyze_document_text(rel_name, text, keywords)
        doc_reports.append(report)
        for kw, cnt in report["keyword_counts"].items():
            global_keyword_totals[kw] = global_keyword_totals.get(kw, 0) + cnt

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scanned_dir": root_dir.as_posix(),
        "total_files": len(doc_reports),
        "global_keyword_totals": global_keyword_totals,
        "documents": doc_reports,
    }


def export_reports(summary: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
    """将扫描结果同时导出为 JSON 完整报告与 CSV 运营明细表。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "kb_scan_report.json"
    csv_path = output_dir / "kb_scan_summary.csv"

    # 1. 导出 JSON
    with json_path.open("w", encoding="utf-8") as jf:
        json.dump(summary, jf, ensure_ascii=False, indent=2)

    # 2. 导出 CSV（utf-8-sig 确保 Excel 打开中文不乱码，newline='' 防多余空行）
    fieldnames = ["file_name", "char_count", "line_count", "total_keyword_hits", "tickets", "emails"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        for doc in summary["documents"]:
            writer.writerow(
                {
                    "file_name": doc["file_name"],
                    "char_count": doc["char_count"],
                    "line_count": doc["line_count"],
                    "total_keyword_hits": doc["total_keyword_hits"],
                    "tickets": ";".join(doc["tickets"]),
                    "emails": ";".join(doc["emails"]),
                }
            )

    return {"json": json_path, "csv": csv_path}


if __name__ == "__main__":
    # 使用临时目录自包含演示，运行完自动清理不留垃圾文件
    with tempfile.TemporaryDirectory() as tmp:
        kb_dir = Path(tmp) / "kb"
        (kb_dir / "tech").mkdir(parents=True)
        (kb_dir / "readme.md").write_text("星辰智脑 Python RAG 指南，联系人 chen@starmind.cn", encoding="utf-8")
        (kb_dir / "tech" / "api.txt").write_text("工单 STARMIND-011：Python 与 FastAPI 接口规范", encoding="utf-8")

        summary = scan_directory(kb_dir, ["Python", "RAG", "FastAPI"])
        paths = export_reports(summary, Path(tmp) / "out")
        print(f"扫描完成: {summary['total_files']} 份文档 | 全局词频: {summary['global_keyword_totals']}")
        print("CSV 预览:\n" + paths["csv"].read_text(encoding="utf-8-sig").strip())
''',
                "explanation": (
                    "1. `file_path.relative_to(root_dir).as_posix()` 无论在 Windows 还是 Linux 上都输出统一的 `/` 相对路径，报表格式跨平台一致。\n"
                    "2. `__main__` 演示块使用 `tempfile.TemporaryDirectory()`，跑完自动销毁临时目录，极度干净。"
                ),
                "expected_output": (
                    "扫描完成: 2 份文档 | 全局词频: {'Python': 2, 'RAG': 1, 'FastAPI': 1}\n"
                    "CSV 预览:\n"
                    "file_name,char_count,line_count,total_keyword_hits,tickets,emails\n"
                    "readme.md,34,1,2,,chen@starmind.cn\n"
                    "tech/api.txt,34,1,2,STARMIND-011,"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-011 自动化单元测试。"""

import csv
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day11_regex_extractor import extract_entities, count_keywords
from day11_doc_scanner import scan_directory, export_reports


def test_regex_extraction_and_keywords():
    text = "联系 hr@starmind.cn 或 dev@starmind.cn，参考 starmind-008 和 STARMIND-011。Python 很好用，python！"
    ent = extract_entities(text)
    assert ent["emails"] == ["dev@starmind.cn", "hr@starmind.cn"]
    assert ent["tickets"] == ["STARMIND-008", "STARMIND-011"]
    assert count_keywords(text, ["Python", "Java"]) == {"Python": 2, "Java": 0}


def test_scan_directory_and_export_csv_json(tmp_path: Path):
    kb = tmp_path / "docs"
    (kb / "sub").mkdir(parents=True)
    (kb / "a.md").write_text("星辰智脑 RAG 方案 STARMIND-001", encoding="utf-8")
    (kb / "sub" / "b.txt").write_text("RAG 与 Agent 结合 dev@starmind.cn", encoding="utf-8")
    (kb / "ignore.bin").write_bytes(b"\x00\x01")  # 非文本文件应自动忽略

    summary = scan_directory(kb, ["RAG", "Agent"])
    assert summary["total_files"] == 2
    assert summary["global_keyword_totals"] == {"RAG": 2, "Agent": 1}

    out = export_reports(summary, tmp_path / "reports")
    loaded_json = json.loads(out["json"].read_text(encoding="utf-8"))
    assert loaded_json["total_files"] == 2

    with out["csv"].open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["file_name"] == "a.md"
    assert rows[1]["file_name"] == "sub/b.txt"

    with pytest.raises(FileNotFoundError):
        scan_directory(tmp_path / "not_exist", ["RAG"])
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "全线采用 `pathlib` + `utf-8-sig` + `newline=''`，还贴心过滤掉了 `.bin` 二进制杂文件，可以直接复用进后面的 RAG 导入器。",
                "resolution": "Approved。"
            },
            {
                "reviewer": "林产品 (PM)",
                "role": "Product Acceptance",
                "comment": "导出的 CSV 用 Excel 双击直接打开中文完美显示，工单号和邮箱也全抓出来了！",
                "resolution": "产品验收通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：正则表达式批量脱敏手机号",
                "difficulty": "基础巩固",
                "requirement": "编写 `mask_phones_in_text(text: str) -> str`，使用 `re.sub` 将任意长文本中出现的所有 11 位中国大陆手机号（1 开头）自动替换为前 3 后 4 脱敏格式（如 `138****8899`）。",
                "hint": "使用捕获组 `r'(1[3-9]\\d)\\d{4}(\\d{4})'` 配合替换串 `r'\\1****\\2'`。",
                "solution_code": r'''"""Day 11 课后题 1：正则捕获组批量脱敏文本中的手机号。"""

import re

PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)")


def mask_phones_in_text(text: str) -> str:
    """将文本中所有独立的 11 位手机号替换为中间四位掩码。"""
    return PHONE_RE.sub(r"\1****\2", text)


if __name__ == "__main__":
    raw = "客户手机 13857108899，备用 18612345678，订单号 13857108899001 不应误伤。"
    print(mask_phones_in_text(raw))
''',
                "solution_analysis": "利用负向环视 `(?<!\\d)` 与 `(?!\\d)` 精准匹配独立 11 位手机号，不会误伤 14 位数字订单号！"
            },
            {
                "title": "企业实战：日志文件按日期归档命名器",
                "difficulty": "企业实战",
                "requirement": "编写 `build_log_path(base_dir: Path, service_name: str, dt: datetime) -> Path`，返回形如 `base_dir/2026/05/starmind_20260511.log` 的分层归档路径。",
                "hint": "用 `dt.strftime('%Y')`、`dt.strftime('%m')` 和 `dt.strftime('%Y%m%d')` 拼接 `Path`。",
                "solution_code": r'''"""Day 11 课后题 2：按年月分目录的日志归档路径生成器。"""

from datetime import datetime, timezone
from pathlib import Path


def build_log_path(base_dir: Path, service_name: str, dt: datetime) -> Path:
    """生成按 年/月 分层的标准日志文件路径。"""
    return base_dir / dt.strftime("%Y") / dt.strftime("%m") / f"{service_name}_{dt.strftime('%Y%m%d')}.log"


if __name__ == "__main__":
    now = datetime(2026, 5, 11, 10, 30, tzinfo=timezone.utc)
    print(build_log_path(Path("logs"), "starmind", now).as_posix())
''',
                "solution_analysis": "按年月分桶存放日志是运维标配，避免单目录塞进几十万个文件导致 `ls` 卡死。"
            },
            {
                "title": "架构进阶：从大模型回复中提取所有 Markdown 代码块",
                "difficulty": "架构进阶",
                "requirement": "大模型经常在回答中夹杂多个 ```` ```python ... ``` ```` 代码块。编写 `extract_code_blocks(markdown_text: str) -> list[dict]`，用非贪婪正则提取每个代码块的语言标识 `lang` 和纯代码正文 `code`。",
                "hint": "使用 `re.compile(r'```(\\w*)\\n(.*?)```', re.DOTALL)` 配合 `findall`。",
                "solution_code": r'''"""Day 11 课后题 3：大模型 Markdown 回复代码块提取器。"""

import re
from typing import List, Dict

CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)


def extract_code_blocks(markdown_text: str) -> List[Dict[str, str]]:
    """提取 Markdown 中所有围栏代码块及其语言类型。"""
    blocks: List[Dict[str, str]] = []
    for lang, code in CODE_BLOCK_RE.findall(markdown_text):
        blocks.append({"lang": lang.lower() or "text", "code": code.strip()})
    return blocks


if __name__ == "__main__":
    reply = "示例如下：\n```python\nprint('hello')\n```\n配置：\n```json\n{\"ok\": true}\n```"
    print(extract_code_blocks(reply))
''',
                "solution_analysis": "本题直接可用于代码执行 Agent（Code Interpreter）自动抽取大模型生成的 Python 代码并送入沙盒运行！注意 `re.DOTALL` 让 `.` 能跨行匹配，非贪婪 `.*?` 防止把两个代码块合并成一个。"
            }
        ],
        "extra_deep_dive": (
            "【大厂避坑：大文件读写千万别一次性 `.read_text()`！】\n"
            "今天扫描的是几 KB 的制度文档，`.read_text()` 一行很爽；但以后遇到 5GB 的服务器访问日志或百万行 JSONL 微调数据集，直接 `.read()` 会瞬间把内存打爆（OOM Killer 直接杀进程）。"
            "大文件标准写法是逐行流式迭代：`with path.open('r', encoding='utf-8') as f: for line in f: ...`，内存占用永远只有几 KB！"
        )
    },

    # =========================================================================
    # DAY 12: 网络请求与 API 调用
    # =========================================================================
    {
        "day": 12,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "网络请求与 API 调用",
        "subtitle": "吃透 HTTP 协议与 OpenAI 兼容规范，封装支持本地 Mock 降级的 DeepSeek/通义千问命令行问答工具",
        "gitlab_ticket": "STARMIND-012",
        "git_branch": "feat/day12-http-llm-api-client",
        "git_commit": "feat(day12): 封装OpenAI兼容HTTP大模型客户端与本地Mock降级命令行问答小程序",
        "prev_recap": "昨天咱们用 `pathlib`、`re`、`csv`、`datetime` 撸完了星辰知识库批量文档扫描与报表导出工具，本地文件处理这一关已经彻底打通。",
        "next_preview": "明天（Day 13）咱们进入 Python 工程化进阶语法——装饰器、生成器 `yield`、`python-dotenv` 密钥管理与 `asyncio` 异步并发，给今天刚调通的 API 客户端加上自动重试、超时控制与流式输出！",
        "narrator_opening": (
            "兄弟们，今天是个里程碑！前 11 天咱们都在本地捣鼓数据结构、类和文件，今天终于要「通网」调用大模型 API 了（工单 STARMIND-012）！\n"
            "先说一个国内 AI 工程界的超级利好：不管是 DeepSeek、阿里通义千问（DashScope）、智谱 GLM 还是硅基流动，几乎全部兼容 OpenAI 的 `/v1/chat/completions` HTTP 接口规范——"
            "只要你吃透 HTTP POST 请求、Bearer Token 鉴权和 JSON 报文解析，换一家厂商只需要改两行配置（`base_url` 和 `model`）！\n"
            "老陈还要教你一个大厂极其看重的习惯：**无 Key 自动降级本地 Mock 模式**。开发机没配外网 Key、或者 GitLab CI 跑自动化测试时，绝不能因为连不上外网就报错挂掉，更不能在单元测试里白白烧公司的 Token 钱！"
        ),
        "narrator_closing": (
            "今天你不仅搞懂了 HTTP 请求头、状态码和 JSON 报文，还亲手写出了一套「有 Key 走真实 HTTPS、无 Key 自动走本地 Mock、单测用 `httpx.MockTransport` 精准模拟 200/401/429」的生产级客户端骨架。\n"
            "记住老陈一句话：**永远不要把真实 API Key 硬编码写进 `.py` 文件里提交到 Git！**明天咱们就用 `python-dotenv` + 重试装饰器 + 异步并发，把这套客户端武装到牙齿！"
        ),
        "business_prd": {
            "background": "星辰智脑项目需要正式打通大模型推理能力，首期计划接入 DeepSeek 与通义千问（OpenAI 兼容接口）。但在内网开发和自动化测试环境下无法保证随时拥有外网 API Key，需要客户端具备平滑的本地 Mock 降级能力。",
            "pain_points": [
                "新手直接裸拼 HTTP 请求容易漏掉 `Authorization: Bearer` 请求头或忘记设置 `timeout` 导致进程永久卡死。",
                "直接硬编码某一家大模型 SDK，后期切换 DeepSeek/通义千问成本极高。",
                "本地开发和 CI 流水线没有外网 API Key 时无法运行和验证问答主流程。"
            ],
            "goals": [
                "理解 HTTP 协议核心要素（URL、POST Method、Headers、JSON Body、状态码 200/401/429/5xx）。",
                "掌握 `httpx` / `urllib` / `requests` 的区别与 OpenAI 兼容协议 `/chat/completions` 报文封装。",
                "交付具备「真实 HTTP 调用 + 无 Key 自动本地 Mock 降级」的客户端类与第一版命令行 AI 问答小程序。"
            ],
            "acceptance_criteria": [
                "当 `api_key` 为空或开启 `mock_mode=True` 时，自动返回符合 OpenAI 协议格式的本地 Mock 回复且不发起任何外网请求。",
                "当传入 `api_key` 时，能按标准格式组装 `Authorization: Bearer ...` 与 JSON 请求体并发送 POST 请求，正确解析 `choices[0].message.content` 与 `usage`。",
                "能准确拦截 401 鉴权失败、429 触发限流、5xx 服务端异常，并给出清晰中文错误提示；通过 `httpx.MockTransport` 离线单测。"
            ],
            "non_functional": [
                "所有网络请求必须显式设置 `timeout` 超时时间，严禁无限等待。",
                "命令行问答入口函数支持脚本化输入参数，确保自动化测试不阻塞在 `input()`。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "HTTP 协议精讲与 urllib/requests/httpx 选型", "detail": "拆解 HTTP 请求响应报文、常见状态码含义，以及为什么 OpenAI 官方 SDK 全面选用 httpx。"},
            {"slot": "下午 14:00-17:30", "topic": "封装 OpenAI 兼容 HTTP 客户端与 CLI 问答工具", "detail": "编写请求体构造、响应解析、Mock 降级引擎与命令行问答小程序。"},
            {"slot": "晚间 19:00-20:30", "topic": "基于 httpx.MockTransport 的零外网单测", "detail": "离线模拟 200 成功、401 鉴权失败、429 限流响应，验证客户端健壮性。"},
            {"slot": "复盘 20:30-21:00", "topic": "国内主流大模型厂商接口对照与课后作业", "detail": "梳理 DeepSeek/通义千问/智谱 Base URL 差异，完成 3 道梯度课后题。"}
        ],
        "architecture_design": (
            "本模块采用「协议与传输解耦 + 本地降级」的清晰两层架构，为后续接入任意 OpenAI 兼容模型打下基石：\n"
            "1. **大模型 HTTP 客户端层（day12_llm_http_client.py）**：\n"
            "   - 使用 `@dataclass` 定义强类型的 `LLMRequestConfig` 与 `LLMResponse`，彻底告别散落的字典 key 拼写错误。\n"
            "   - 将 `build_chat_payload()`（请求体构建）与 `parse_chat_response()`（响应体解析）抽离为纯函数，无论数据来自远程 HTTPS 还是本地 Mock，走的是同一套校验与解析管线。\n"
            "   - 底层默认使用现代异步/同步通吃的 `httpx.Client`，并支持注入自定义 `transport`（测试时直接注入 `httpx.MockTransport`，不发真实网络包也能覆盖 100% HTTP 分支逻辑）。\n"
            "2. **命令行 AI 问答交互层（day12_cli_qa.py）**：\n"
            "   - 封装 `ask_once()` 单轮提问与 `run_cli_qa()` 交互循环，支持通过 `inputs` 参数注入测试脚本，彻底规避顶层阻塞 `input()` 的工程坏习惯。"
        ),
        "diagrams": [
            {
                "title": "大模型 API 调用与本地 Mock 降级流程图",
                "kind": "flowchart",
                "caption": "展示客户端如何根据 api_key 与 mock_mode 自动路由至真实 HTTPS 请求或本地 Mock 响应，并统一进入响应解析器。",
                "nodes": [
                    {"id": "n1", "label": "用户输入问题", "sub": "组装 messages 列表", "color": "#3b82f6"},
                    {"id": "n2", "label": "检查 API Key / Mock", "sub": "无 Key 自动安全降级", "color": "#8b5cf6"},
                    {"id": "n3", "label": "httpx POST 请求", "sub": "Bearer 鉴权 + timeout", "color": "#f59e0b"},
                    {"id": "n4", "label": "本地 Mock 引擎", "sub": "生成兼容 JSON 报文", "color": "#06b6d4"},
                    {"id": "n5", "label": "统一解析与异常处理", "sub": "提取回复与 Token 统计", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "build_chat_payload"},
                    {"from": "n2", "to": "n3", "label": "有 Key 且非 Mock"},
                    {"from": "n2", "to": "n4", "label": "无 Key 或 Mock 模式"},
                    {"from": "n3", "to": "n5", "label": "检查状态码 200/401/429"},
                    {"from": "n4", "to": "n5", "label": "同构 JSON 响应"}
                ]
            },
            {
                "title": "StarMind LLM HTTP 客户端分层架构图",
                "kind": "architecture",
                "caption": "展示 CLI 交互层、协议封装层、传输适配层（httpx / MockTransport / LocalMock）的清晰解耦。",
                "nodes": [
                    {"id": "a1", "label": "CLI 问答小程序", "sub": "day12_cli_qa.py", "color": "#3b82f6"},
                    {"id": "a2", "label": "StarMindHTTPClient", "sub": "统一 chat() 调用入口", "color": "#8b5cf6"},
                    {"id": "a3", "label": "Payload & Parser", "sub": "纯函数构造与校验", "color": "#f59e0b"},
                    {"id": "a4", "label": "httpx Transport", "sub": "真实 HTTPS / MockTransport", "color": "#10b981"},
                    {"id": "a5", "label": "DeepSeek / 通义千问", "sub": "OpenAI 兼容云端 API", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "ask_once()"},
                    {"from": "a2", "to": "a3", "label": "报文编解码"},
                    {"from": "a2", "to": "a4", "label": "发送 POST 请求"},
                    {"from": "a4", "to": "a5", "label": "/v1/chat/completions"}
                ]
            },
            {
                "title": "OpenAI 兼容协议请求与响应报文示意图",
                "kind": "schematic",
                "caption": "直观拆解 POST /v1/chat/completions 的请求头、请求体字段与返回 JSON 中回复正文和用量统计的层级路径。",
                "nodes": [
                    {"id": "s1", "label": "HTTP Headers", "sub": "Authorization: Bearer sk-...", "color": "#3b82f6"},
                    {"id": "s2", "label": "Request JSON Body", "sub": "model / messages / temperature", "color": "#8b5cf6"},
                    {"id": "s3", "label": "云端大模型推理", "sub": "HTTP 200 OK", "color": "#f59e0b"},
                    {"id": "s4", "label": "Response JSON", "sub": "choices[0].message.content + usage", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "s1", "to": "s3", "label": "身份认证"},
                    {"from": "s2", "to": "s3", "label": "对话上下文"},
                    {"from": "s3", "to": "s4", "label": "返回结构化回复"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. HTTP 协议核心：调用大模型 API 必懂的 4 个要素",
                "content": (
                    "调用大模型本质上就是发一次标准 HTTP POST 请求：\n"
                    "- **URL**：如 DeepSeek 的 `https://api.deepseek.com/v1/chat/completions` 或通义千问兼容地址 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`。\n"
                    "- **Headers**：必须携带 `Authorization: Bearer <API_KEY>` 与 `Content-Type: application/json`。\n"
                    "- **Body**：JSON 对象，包含 `model`、`messages`（角色+内容列表）、`temperature` 等参数。\n"
                    "- **状态码**：`200` 成功、`401` Key 无效或过期、`429` 触发 QPS 限流或余额不足、`500/502/503` 模型服务端抖动。"
                ),
                "pitfalls": "调用外部 HTTP API 一定要显式传 `timeout=30.0`！默认不设超时一旦对端网络黑洞，你的服务线程就会永远卡死直到被运维重启。"
            },
            {
                "heading": "2. urllib vs requests vs httpx：现代 AI 工程怎么选？",
                "content": (
                    "- `urllib.request`：Python 标准库，零第三方依赖，写轻量脚本够用，但 API 略繁琐。\n"
                    "- `requests`：老牌国民级同步 HTTP 库，写法优雅，但**不支持 `async/await` 异步和 HTTP/2**。\n"
                    "- `httpx`：新一代主力库，接口几乎 100% 兼容 `requests`，同时原生支持同步 `Client`、异步 `AsyncClient` 以及 `MockTransport` 离线测试。OpenAI 官方 Python SDK 和 FastAPI 测试客户端底层全用 `httpx`！"
                ),
                "pitfalls": "高频调用同一个 API 域名时，不要每次请求都临时新建客户端，尽量复用 `httpx.Client()` 连接池（Keep-Alive），能省掉大量 TCP+TLS 握手耗时。"
            },
            {
                "heading": "3. 为什么企业级 AI 客户端必须内置 Mock Fallback？",
                "content": (
                    "1）新同学入职第一天还没审批下来正式 API Key，也能立刻跑通全套业务代码；\n"
                    "2）CI/CD 自动化测试每天跑几百次单测，用本地 Mock 或 `httpx.MockTransport` 可以实现零成本、毫秒级、100% 确定性通过，不受外网波动影响。"
                ),
                "pitfalls": "Mock 数据结构必须严格对齐真实 API 的返回 Schema（包含 `choices` 和 `usage`），让 Mock 和真实请求走同一套解析函数，否则「测试全绿、上线解析报错」。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：封装 OpenAI 兼容 HTTP 大模型客户端（含本地 Mock 降级）",
                "file_path": "src/day12_llm_http_client.py",
                "narration": "先写核心客户端 `day12_llm_http_client.py`：用 `dataclass` 定义配置与响应，纯函数负责报文构造与解析，`StarMindHTTPClient` 在无 Key 时无缝降级为本地 Mock，有 Key 时走标准 `httpx` POST 请求。",
                "code": r'''"""
STARMIND-012 模块一：OpenAI 兼容协议 HTTP 大模型客户端（支持本地 Mock 降级）。
兼容 DeepSeek / 通义千问 DashScope / 智谱等 /v1/chat/completions 接口。
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


class LLMAPIError(RuntimeError):
    """大模型 HTTP 接口调用异常基类，携带 HTTP 状态码便于上层区分处理。"""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass
class LLMRequestConfig:
    """大模型 API 连接配置。"""

    base_url: str = "https://api.deepseek.com/v1"
    api_key: str = ""
    model: str = "deepseek-chat"
    timeout: float = 15.0
    temperature: float = 0.7


@dataclass
class LLMResponse:
    """标准化大模型响应对象。"""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    source: str  # "remote" 或 "mock"


def build_chat_payload(
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """构造标准 OpenAI 兼容 /chat/completions 请求体。"""
    if not messages:
        raise ValueError("messages 不能为空")
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }


def parse_chat_response(
    raw_data: Dict[str, Any],
    latency_ms: float,
    source: str = "remote",
) -> LLMResponse:
    """解析 OpenAI 兼容响应 JSON 为强类型 LLMResponse。"""
    choices = raw_data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("接口返回格式异常：缺少有效的 choices 字段")

    first_message = choices[0].get("message", {})
    content = first_message.get("content")
    if not isinstance(content, str):
        raise ValueError("接口返回格式异常：缺少 message.content 文本")

    usage = raw_data.get("usage", {})
    prompt_tokens = int(usage.get("prompt_tokens", 0))
    completion_tokens = int(usage.get("completion_tokens", 0))
    total_tokens = int(usage.get("total_tokens", prompt_tokens + completion_tokens))

    return LLMResponse(
        content=content.strip(),
        model=str(raw_data.get("model", "unknown")),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        latency_ms=round(latency_ms, 2),
        source=source,
    )


class StarMindHTTPClient:
    """星辰智脑 OpenAI 兼容 HTTP 客户端（支持无 Key 本地 Mock 降级）。"""

    def __init__(
        self,
        config: Optional[LLMRequestConfig] = None,
        mock_mode: bool = False,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.config = config or LLMRequestConfig()
        # 如果显式开启 mock_mode 或者未配置 api_key，自动启用本地 Mock 模式
        self.mock_mode = mock_mode or (not self.config.api_key.strip())
        self._transport = transport

    def _mock_chat_completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """离线本地 Mock 引擎：返回与真实 OpenAI 协议 100% 同构的 JSON 报文。"""
        messages = payload["messages"]
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )

        # 针对星辰数科常见演示问题给出贴近业务的回答
        if "报销" in last_user:
            reply = "【本地Mock】星辰数科差旅报销请在钉钉发起「费用报销单」，500元以上需直属主管+财务双审批。"
        elif "DeepSeek" in last_user or "兼容" in last_user or "通义" in last_user:
            reply = "【本地Mock】DeepSeek 与通义千问均兼容 OpenAI /v1/chat/completions 协议，切换厂商只需修改 base_url 与 model。"
        elif "年假" in last_user:
            reply = "【本地Mock】入职满 1 年享 5 天带薪年假，系统按自然年每年 1 月 1 日自动发放。"
        else:
            reply = f"【本地Mock】已收到你的提问：「{last_user}」。当前未配置线上 API Key，已自动降级为离线模拟回复。"

        prompt_tokens = sum(len(m.get("content", "")) for m in messages)
        completion_tokens = len(reply)
        return {
            "id": "chatcmpl-starmind-mock-001",
            "object": "chat.completion",
            "model": f"{payload['model']}-mock",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": reply},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }

    def chat(self, messages: List[Dict[str, str]]) -> LLMResponse:
        """发送对话请求并返回标准化 LLMResponse。"""
        payload = build_chat_payload(
            messages=messages,
            model=self.config.model,
            temperature=self.config.temperature,
        )
        start = time.perf_counter()

        if self.mock_mode:
            raw_data = self._mock_chat_completion(payload)
            elapsed_ms = (time.perf_counter() - start) * 1000
            return parse_chat_response(raw_data, latency_ms=elapsed_ms, source="mock")

        endpoint = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(
                timeout=self.config.timeout,
                transport=self._transport,
            ) as client:
                resp = client.post(endpoint, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise LLMAPIError(f"请求大模型超时（>{self.config.timeout}s）") from exc
        except httpx.HTTPError as exc:
            raise LLMAPIError(f"网络请求失败：{exc}") from exc

        if resp.status_code == 401:
            raise LLMAPIError("API Key 无效或已过期（HTTP 401）", status_code=401)
        if resp.status_code == 429:
            raise LLMAPIError("触发接口频率限制或余额不足（HTTP 429）", status_code=429)
        if resp.status_code >= 500:
            raise LLMAPIError(
                f"大模型服务端暂时不可用（HTTP {resp.status_code}）",
                status_code=resp.status_code,
            )
        if resp.status_code != 200:
            raise LLMAPIError(
                f"接口返回异常状态码 HTTP {resp.status_code}: {resp.text[:120]}",
                status_code=resp.status_code,
            )

        elapsed_ms = (time.perf_counter() - start) * 1000
        return parse_chat_response(resp.json(), latency_ms=elapsed_ms, source="remote")


if __name__ == "__main__":
    # 默认不传 api_key，自动触发本地 Mock 降级模式
    client = StarMindHTTPClient(LLMRequestConfig(model="deepseek-chat"))
    result = client.chat([
        {"role": "system", "content": "你是杭州星辰数科企业知识助手。"},
        {"role": "user", "content": "星辰数科差旅报销怎么走流程？"},
    ])
    print(f"[{result.source}] 模型: {result.model} | 耗时: {result.latency_ms}ms | Tokens: {result.total_tokens}")
    print(f"回复: {result.content}")
''',
                "explanation": (
                    "1. `self.mock_mode = mock_mode or (not self.config.api_key.strip())` 实现了极度丝滑的无 Key 自动降级，开发者零配置即可跑通。\n"
                    "2. 无论走 `mock` 还是 `remote`，最终都经过 `parse_chat_response()` 统一解析，保证数据结构 100% 一致。\n"
                    "3. 针对 HTTP 401/429/5xx 做了细粒度状态码翻译，线上排障一眼就能定位是 Key 错、限流还是厂商挂了。"
                ),
                "expected_output": (
                    "[mock] 模型: deepseek-chat-mock | 耗时: 0.05ms | Tokens: 78\n"
                    "回复: 【本地Mock】星辰数科差旅报销请在钉钉发起「费用报销单」，500元以上需直属主管+财务双审批。"
                )
            },
            {
                "step_title": "步骤二：组装第一版命令行 AI 问答小程序（支持脚本化非阻塞测试）",
                "file_path": "src/day12_cli_qa.py",
                "narration": "客户端就绪后，咱们把它包装成一个干净的命令行 AI 问答小程序。注意老陈的工程铁律：交互循环必须支持注入测试输入列表 `inputs`，绝对不能让代码一导入或一测试就卡死在 `input()` 里！",
                "code": r'''"""
STARMIND-012 模块二：星辰智脑命令行 AI 问答小程序 v0.1。
演示单轮提问封装、控制台格式化输出与可测试的 CLI 交互循环。
"""

from typing import List, Optional

from day12_llm_http_client import LLMAPIError, LLMRequestConfig, LLMResponse, StarMindHTTPClient

DEFAULT_SYSTEM_PROMPT = "你是杭州星辰数科内部 AI 助手「星辰智脑」，请用简洁专业中文回答问题。"


def ask_once(
    client: StarMindHTTPClient,
    question: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> LLMResponse:
    """发起一次单轮 AI 问答。"""
    cleaned = question.strip()
    if not cleaned:
        raise ValueError("提问内容不能为空")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": cleaned},
    ]
    return client.chat(messages)


def format_qa_panel(question: str, response: LLMResponse) -> str:
    """将问答结果格式化为清晰的终端展示文本。"""
    return (
        f"问：{question}\n"
        f"答：{response.content}\n"
        f"—— [来源: {response.source} | 模型: {response.model} | "
        f"Tokens: {response.total_tokens} | 耗时: {response.latency_ms}ms]"
    )


def run_cli_qa(
    client: StarMindHTTPClient,
    inputs: Optional[List[str]] = None,
) -> List[str]:
    """
    运行命令行问答循环。
    - 传入 inputs 列表时按脚本逐条执行（适合演示与自动化测试，不阻塞）；
    - inputs 为 None 时进入终端交互式 input() 模式。
    """
    outputs: List[str] = []
    script_iter = iter(inputs) if inputs is not None else None

    while True:
        if script_iter is not None:
            try:
                raw_q = next(script_iter)
            except StopIteration:
                break
        else:
            raw_q = input("请输入问题（输入 /exit 退出）> ")

        q = raw_q.strip()
        if q.lower() in {"/exit", "exit", "quit"}:
            outputs.append("已退出星辰智脑问答小程序。")
            break
        if not q:
            outputs.append("提示：问题不能为空，请重新输入。")
            continue

        try:
            resp = ask_once(client, q)
            outputs.append(format_qa_panel(q, resp))
        except (ValueError, LLMAPIError) as exc:
            outputs.append(f"调用失败：{exc}")

    return outputs


if __name__ == "__main__":
    # 使用预设问题脚本运行演示，无需手动按键输入
    demo_client = StarMindHTTPClient(LLMRequestConfig(model="deepseek-chat"))
    demo_questions = [
        "星辰数科差旅报销流程是什么？",
        "DeepSeek API 兼容什么协议格式？",
        "/exit",
    ]
    for block in run_cli_qa(demo_client, inputs=demo_questions):
        print(block)
        print("-" * 50)
''',
                "explanation": (
                    "1. `run_cli_qa(client, inputs=...)` 把「数据来源」抽象出来，传入 `inputs` 列表就能全自动跑完多条问答并收集输出，既方便演示又方便 `pytest` 断言。\n"
                    "2. 在循环内捕获 `(ValueError, LLMAPIError)`，哪怕某一次请求遇到 429 限流或空输入，程序也只会给出友好提示而不会闪退崩溃。"
                ),
                "expected_output": (
                    "问：星辰数科差旅报销流程是什么？\n"
                    "答：【本地Mock】星辰数科差旅报销请在钉钉发起「费用报销单」，500元以上需直属主管+财务双审批。\n"
                    "—— [来源: mock | 模型: deepseek-chat-mock | Tokens: 96 | 耗时: 0.04ms]\n"
                    "--------------------------------------------------\n"
                    "问：DeepSeek API 兼容什么协议格式？\n"
                    "答：【本地Mock】DeepSeek 与通义千问均兼容 OpenAI /v1/chat/completions 协议，切换厂商只需修改 base_url 与 model。\n"
                    "—— [来源: mock | 模型: deepseek-chat-mock | Tokens: 109 | 耗时: 0.03ms]\n"
                    "--------------------------------------------------\n"
                    "已退出星辰智脑问答小程序。\n"
                    "--------------------------------------------------"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-012 自动化单元测试（全程离线，零外网依赖）。"""

import sys
from pathlib import Path
import httpx
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day12_llm_http_client import (
    LLMAPIError,
    LLMRequestConfig,
    StarMindHTTPClient,
    build_chat_payload,
    parse_chat_response,
)
from day12_cli_qa import ask_once, run_cli_qa


def test_payload_and_response_parser():
    payload = build_chat_payload([{"role": "user", "content": "你好"}], model="qwen-plus", temperature=0.3)
    assert payload["model"] == "qwen-plus"
    assert payload["temperature"] == 0.3

    raw = {
        "model": "qwen-plus",
        "choices": [{"message": {"role": "assistant", "content": "  你好，星辰同事！  "}}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
    }
    resp = parse_chat_response(raw, latency_ms=12.345, source="remote")
    assert resp.content == "你好，星辰同事！"
    assert resp.total_tokens == 15
    assert resp.latency_ms == 12.35

    with pytest.raises(ValueError):
        parse_chat_response({"choices": []}, latency_ms=1.0)


def test_auto_mock_fallback_without_api_key():
    client = StarMindHTTPClient(LLMRequestConfig(api_key="", model="deepseek-chat"))
    assert client.mock_mode is True
    resp = ask_once(client, "年假有多少天？")
    assert resp.source == "mock"
    assert "年假" in resp.content


def test_remote_http_success_and_error_codes_with_mock_transport():
    # 1. 模拟 HTTP 200 正常返回并校验 Authorization 请求头
    def ok_handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer sk-test-key"
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={
                "model": "deepseek-chat",
                "choices": [{"message": {"role": "assistant", "content": "来自远程模拟节点的回复"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 18, "total_tokens": 30},
            },
        )

    cfg = LLMRequestConfig(api_key="sk-test-key", model="deepseek-chat")
    client_ok = StarMindHTTPClient(cfg, transport=httpx.MockTransport(ok_handler))
    resp = client_ok.chat([{"role": "user", "content": "测试远程调用"}])
    assert resp.source == "remote"
    assert resp.content == "来自远程模拟节点的回复"
    assert resp.total_tokens == 30

    # 2. 模拟 HTTP 401 鉴权失败与 HTTP 429 限流
    client_401 = StarMindHTTPClient(
        cfg,
        transport=httpx.MockTransport(lambda req: httpx.Response(401, json={"error": "invalid key"})),
    )
    with pytest.raises(LLMAPIError) as exc_401:
        client_401.chat([{"role": "user", "content": "hi"}])
    assert exc_401.value.status_code == 401

    client_429 = StarMindHTTPClient(
        cfg,
        transport=httpx.MockTransport(lambda req: httpx.Response(429, json={"error": "rate limit"})),
    )
    with pytest.raises(LLMAPIError) as exc_429:
        client_429.chat([{"role": "user", "content": "hi"}])
    assert exc_429.value.status_code == 429


def test_run_cli_qa_scripted():
    client = StarMindHTTPClient(LLMRequestConfig(api_key=""))
    logs = run_cli_qa(client, inputs=["", "报销流程", "/exit"])
    assert "不能为空" in logs[0]
    assert "费用报销单" in logs[1]
    assert "已退出" in logs[2]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "用 `httpx.MockTransport` 把 200/401/429 三条 HTTP 分支全测透了，还不花一分钱 Token，这才是大厂写 API 客户端的标准姿势！",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (后端主程)",
                "role": "Code Quality",
                "comment": "`run_cli_qa` 把 `inputs` 参数化做得很好，CI 流水线跑测试完全不会卡死在 `input()` 上。",
                "resolution": "LGTM，合并入主干。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：HTTP 状态码智能诊断器",
                "difficulty": "基础巩固",
                "requirement": "编写函数 `diagnose_http_status(status_code: int) -> dict`，根据输入的状态码返回 `{'category': ..., 'retryable': bool, 'advice': ...}`。要求正确区分 200（成功，不可重试）、401/403（鉴权错误，不可重试）、429（限流，可重试）、500~599（服务端错误，可重试）。",
                "hint": "用范围判断 `200 <= status_code < 300` 和 `500 <= status_code < 600` 处理类别，429 单独标为 `retryable=True`。",
                "solution_code": r'''"""Day 12 课后题 1：大模型 API HTTP 状态码智能诊断器。"""

from typing import Any, Dict


def diagnose_http_status(status_code: int) -> Dict[str, Any]:
    """根据 HTTP 状态码返回故障分类、是否建议重试及排查建议。"""
    if 200 <= status_code < 300:
        return {"category": "success", "retryable": False, "advice": "请求成功，正常解析响应即可。"}
    if status_code in (401, 403):
        return {"category": "auth_error", "retryable": False, "advice": "检查 API Key 是否正确、过期或缺少权限。"}
    if status_code == 429:
        return {"category": "rate_limit", "retryable": True, "advice": "触发限流或配额不足，建议指数退避重试或检查账户余额。"}
    if 500 <= status_code < 600:
        return {"category": "server_error", "retryable": True, "advice": "大模型厂商服务端抖动，建议稍后重试或切换备用模型。"}
    return {"category": "client_error", "retryable": False, "advice": f"客户端请求异常（HTTP {status_code}），请检查 URL 与请求体格式。"}


if __name__ == "__main__":
    for code in (200, 401, 429, 503):
        print(code, "->", diagnose_http_status(code))
''',
                "solution_analysis": "区分「可重试错误（429/5xx）」和「不可重试错误（400/401/403）」是写好重试中间件的第一步——对着 401 疯狂重试只会浪费算力甚至被封 IP。"
            },
            {
                "title": "企业实战：国内多厂商 OpenAI 兼容配置工厂",
                "difficulty": "企业实战",
                "requirement": "编写 `create_provider_config(provider: str, api_key: str) -> dict`，支持 `'deepseek'`、`'qwen'`（通义千问）、`'zhipu'`（智谱）三种国内主流厂商，自动填入对应的兼容 `base_url` 与默认推荐模型名；遇到未知厂商抛出 `ValueError`。",
                "hint": "定义一个 `PROVIDER_PRESETS` 常量字典，对传入的 `provider.strip().lower()` 做查表校验。",
                "solution_code": r'''"""Day 12 课后题 2：国内多厂商 OpenAI 兼容配置工厂。"""

from typing import Dict

PROVIDER_PRESETS: Dict[str, Dict[str, str]] = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    "qwen": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "zhipu": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
    },
}


def create_provider_config(provider: str, api_key: str) -> Dict[str, str]:
    """根据厂商名称生成标准 OpenAI 兼容客户端配置。"""
    key = provider.strip().lower()
    if key not in PROVIDER_PRESETS:
        supported = ", ".join(sorted(PROVIDER_PRESETS))
        raise ValueError(f"不支持的厂商 '{provider}'，当前仅支持: {supported}")
    preset = PROVIDER_PRESETS[key]
    return {
        "provider": key,
        "base_url": preset["base_url"],
        "model": preset["model"],
        "api_key": api_key,
    }


if __name__ == "__main__":
    print(create_provider_config("DeepSeek", "sk-demo"))
    print(create_provider_config("qwen", "sk-demo"))
''',
                "solution_analysis": "利用 OpenAI 协议兼容特性，通过工厂字典集中管理各家 `base_url` 和默认模型，业务代码零耦合，切换供应商一行配置搞定。"
            },
            {
                "title": "架构进阶：带自定义 Trace-ID 的 httpx 拦截测试封装",
                "difficulty": "架构进阶",
                "requirement": "编写函数 `send_traced_request(url: str, trace_id: str, transport: httpx.BaseTransport) -> dict`，发送携带 `X-Trace-Id` 请求头的 GET 请求，校验响应 JSON 中是否正确回显了该 `trace_id`，并用 `httpx.MockTransport` 编写自包含运行验证。",
                "hint": "在 `httpx.MockTransport` 的回调函数里从 `request.headers.get('X-Trace-Id')` 取出追踪号并放入返回 JSON。",
                "solution_code": r'''"""Day 12 课后题 3：带 X-Trace-Id 链路追踪头的 httpx 请求与离线 Mock 验证。"""

from typing import Any, Dict
import httpx


def send_traced_request(
    url: str,
    trace_id: str,
    transport: httpx.BaseTransport,
) -> Dict[str, Any]:
    """发送带链路追踪 ID 的 GET 请求并校验回显。"""
    with httpx.Client(timeout=5.0, transport=transport) as client:
        resp = client.get(url, headers={"X-Trace-Id": trace_id})
        resp.raise_for_status()
        data = resp.json()
    if data.get("echo_trace_id") != trace_id:
        raise ValueError("服务端未正确回显 X-Trace-Id")
    return data


if __name__ == "__main__":
    def mock_server(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"status": "ok", "echo_trace_id": request.headers.get("X-Trace-Id")},
        )

    result = send_traced_request(
        "https://api.starmind.local/health",
        trace_id="trace-20260512-001",
        transport=httpx.MockTransport(mock_server),
    )
    print("链路追踪验证通过:", result)
''',
                "solution_analysis": "在微服务和 AI 网关中，每次请求携带 `X-Trace-Id` 是排查全链路耗时的命根子，而 `httpx.MockTransport` 让我们无需起真实服务器就能在毫秒级验证请求头透传逻辑。"
            }
        ],
        "extra_deep_dive": (
            "【大厂实战经验：为什么调用大模型 API 千万别用默认无限超时，也别把 timeout 设成 3 秒？】\n"
            "普通 CRUD 接口 200ms 就返回了，但大模型生成 800 字长回答（尤其开启思考链的推理模型）非流式等待 15~60 秒非常正常！\n"
            "在 `httpx` 中最佳实践是**拆细超时配置**：`httpx.Timeout(connect=5.0, read=60.0, write=10.0, pool=5.0)`——"
            "连不上服务器 5 秒快速失败，连上之后给足 60 秒等待模型慢慢生成内容，既防假死又不误杀长回复！"
        )
    },

    # =========================================================================
    # DAY 13: 进阶语法与异步入门
    # =========================================================================
    {
        "day": 13,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "进阶语法与异步入门",
        "subtitle": "掌握装饰器、yield 生成器、typing、python-dotenv 与 asyncio 并发，为 AI 客户端打造重试与超时护盾",
        "gitlab_ticket": "STARMIND-013",
        "git_branch": "feat/day13-decorators-generators-asyncio",
        "git_commit": "feat(day13): 实现指数退避重试装饰器、yield流式生成器、dotenv配置加载与asyncio并发调度器",
        "prev_recap": "昨天咱们成功封装了 OpenAI 兼容 HTTP 客户端并跑通了本地 Mock 降级命令行问答，还用 `httpx.MockTransport` 覆盖了 401/429 异常测试。",
        "next_preview": "明天（Day 14）就是第一阶段收官大考！咱们要把前 13 天的全部内功融会贯通，独立交付阶段考核项目一——**命令行多轮对话 AI 助手（带上下文记忆、JSON 持久化与 `/clear` `/save` `/exit` 指令）**！",
        "narrator_opening": (
            "今天（STARMIND-013）咱们给代码做一次「从新手脚本到工程组件」的脱胎换骨升级！\n"
            "回想昨天调大模型 API 遇到的三个真实痛点：1）万一遇到 429 限流或短暂网络抖动，总不能每次都在业务代码里手写 `for` 循环重试吧？用**装饰器** `@retry_with_backoff` 一行搞定！\n"
            "2）大模型生成几百字回答时用户不想傻等 10 秒，怎么像 ChatGPT 那样一个字一个字往外吐？靠 **`yield` 生成器**！\n"
            "3）运营要批量让 AI 总结 20 篇文档，同步串行一篇 2 秒要等 40 秒，用 **`asyncio` 异步并发** + `Semaphore` 限流 + `wait_for` 超时控制，3 秒全搞定！\n"
            "再加上 `python-dotenv` 安全管理 `.env` 里的密钥，今天学完你写出来的 Python 代码一眼就能看出是大厂工程师水准！"
        ),
        "narrator_closing": (
            "今天这五把利器——**装饰器、`yield` 生成器、`typing` 类型注解、`python-dotenv`、`asyncio` 异步**——在后面第二阶段的 FastAPI、第三阶段的 RAG 批量向量化、第四阶段的 Agent 工具流里每天都会高频用到。\n"
            "回去把指数退避重试和 `asyncio.gather` 再手敲一遍，明天咱们直接上第一阶段毕业考核项目！"
        ),
        "business_prd": {
            "background": "随着星辰智脑开始对接外部大模型接口与批量文档分析任务，团队需要一套通用的底层可靠性与性能组件：避免密钥泄露、自动应对接口偶发抖动、支持流式分块输出以及多任务异步并发提速。",
            "pain_points": [
                "重试逻辑、耗时统计散落在各个业务函数里，代码重复臃肿。",
                "API Key 容易被误写进源码提交到 GitLab 造成安全事故。",
                "批量调用大模型采用同步串行方式，总耗时随任务数线性暴涨，且缺少单任务超时熔断。"
            ],
            "goals": [
                "掌握 `functools.wraps` 编写带参数的指数退避重试装饰器与耗时统计装饰器。",
                "掌握 `yield` 生成器实现低内存流式文本分块输出，配合 `typing` 清晰标注类型。",
                "掌握 `python-dotenv` 安全读取 `.env` 配置，以及 `asyncio.gather`、`asyncio.wait_for`、`asyncio.Semaphore` 实现带超时与并发上限的异步调用。"
            ],
            "acceptance_criteria": [
                "重试装饰器能在函数前 N-1 次抛异常、第 N 次成功时自动恢复，超过上限后准确抛出原异常。",
                "`.env` 配置加载器能读取本地 `.env` 文件且在文件缺失时安全回退到默认配置。",
                "`yield` 流式生成器返回标准 `Generator` 对象，逐块输出不一次性占用多余内存。",
                "异步批量调度器能并发执行多个任务（总耗时远小于串行总和），并对超时的单个任务进行 `asyncio.TimeoutError` 隔离降级。"
            ],
            "non_functional": [
                "重试延迟与异步模拟延时在测试中使用毫秒级数值，确保单元测试 1 秒内跑完。",
                "所有公共函数与装饰器具备完整 `typing` 类型注解与文档字符串。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "装饰器、yield 生成器与 typing / python-dotenv", "detail": "手写耗时与指数退避重试装饰器、流式分块生成器及 .env 安全配置加载器。"},
            {"slot": "下午 14:00-17:30", "topic": "asyncio 异步并发、超时控制与信号量限流", "detail": "深入理解事件循环、await 挂起让权、asyncio.gather 并发与 wait_for 超时兜底。"},
            {"slot": "晚间 19:00-20:30", "topic": "可靠性与异步并发单元测试", "detail": "用 pytest 验证重试次数、异常透传、生成器惰性吐字、并发提速与超时降级。"},
            {"slot": "复盘 20:30-21:00", "topic": "同步阻塞误区排查与课后作业", "detail": "牢记 async 函数内严禁调 time.sleep，完成 3 道梯度课后作业。"}
        ],
        "architecture_design": (
            "今天构建的是星辰智脑的基础设施工具箱（Infrastructure Toolkit），采用完全解耦的两个模块：\n"
            "1. **配置与横切中间件模块（day13_decorators_and_env.py）**：\n"
            "   - 使用 `dotenv.dotenv_values()` 解析 `.env` 文件并映射到强类型 `EnvSettings` 数据类，避免直接污染全局 `os.environ`，天然适配多环境隔离与单元测试。\n"
            "   - 基于高阶函数闭包与 `@functools.wraps` 实现 `@retry_with_backoff`（指数退避重试）和 `@measure_latency`（耗时审计），实现业务逻辑与容错逻辑彻底解耦（AOP 思想）。\n"
            "   - 使用 `yield` 实现 `stream_text_chunks()` 流式生成器，模拟大模型 SSE 打字机逐块输出。\n"
            "2. **异步并发调度引擎（day13_async_llm_runner.py）**：\n"
            "   - 基于 Python 原生 `asyncio` 事件循环，组合 `asyncio.Semaphore`（控制最大并发数防止把大模型 API 打爆触发 429）、`asyncio.wait_for`（单请求超时熔断）与 `asyncio.gather`（并发汇聚结果），在单线程内实现极高 I/O 吞吐。"
        ),
        "diagrams": [
            {
                "title": "指数退避重试装饰器（@retry_with_backoff）流程图",
                "kind": "flowchart",
                "caption": "展示函数调用失败后如何按 base_delay * 2^attempt 递增休眠并重试，直到成功或耗尽次数抛出异常。",
                "nodes": [
                    {"id": "n1", "label": "调用被装饰函数", "sub": "attempt = 0", "color": "#3b82f6"},
                    {"id": "n2", "label": "是否抛出目标异常？", "sub": "如 RuntimeError / Timeout", "color": "#8b5cf6"},
                    {"id": "n3", "label": "直接返回结果", "sub": "调用成功", "color": "#10b981"},
                    {"id": "n4", "label": "达到 max_retries？", "sub": "检查剩余重试额度", "color": "#f59e0b"},
                    {"id": "n5", "label": "指数退避休眠后重试", "sub": "sleep(base * 2^attempt)", "color": "#06b6d4"},
                    {"id": "n6", "label": "抛出最终异常", "sub": "交由上层兜底", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "执行"},
                    {"from": "n2", "to": "n3", "label": "否（成功）"},
                    {"from": "n2", "to": "n4", "label": "是（捕获异常）"},
                    {"from": "n4", "to": "n5", "label": "否（继续重试）"},
                    {"from": "n5", "to": "n1", "label": "attempt += 1"},
                    {"from": "n4", "to": "n6", "label": "是（耗尽）"}
                ]
            },
            {
                "title": "Python 工程化进阶组件协作架构图",
                "kind": "architecture",
                "caption": "展示 .env 密钥加载、横切装饰器、yield 流式生成器与 asyncio 并发引擎在 AI 应用中的分层位置。",
                "nodes": [
                    {"id": "a1", "label": ".env 配置文件", "sub": "python-dotenv 隔离密钥", "color": "#3b82f6"},
                    {"id": "a2", "label": "装饰器中间件", "sub": "@retry / @measure_latency", "color": "#8b5cf6"},
                    {"id": "a3", "label": "yield 流式生成器", "sub": "低内存逐块吐字", "color": "#06b6d4"},
                    {"id": "a4", "label": "asyncio 并发调度器", "sub": "Semaphore + wait_for + gather", "color": "#f59e0b"},
                    {"id": "a5", "label": "高可用 AI 业务层", "sub": "快速、抗抖动、不泄露密钥", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "a1", "to": "a5", "label": "注入安全配置"},
                    {"from": "a2", "to": "a5", "label": "无侵入增强容错"},
                    {"from": "a3", "to": "a5", "label": "流式输出体验"},
                    {"from": "a4", "to": "a5", "label": "批量 I/O 并发加速"}
                ]
            },
            {
                "title": "同步串行 vs asyncio 异步并发耗时对比示意图",
                "kind": "schematic",
                "caption": "5 个各耗时 50ms 的 I/O 请求：同步串行需要累加等待 250ms，而 asyncio 在 await 等待期切换协程，总耗时仅约 50ms。",
                "nodes": [
                    {"id": "s1", "label": "同步串行模式", "sub": "T1(50ms)->T2(50ms)->...->T5", "color": "#ef4444"},
                    {"id": "s2", "label": "同步总耗时", "sub": "≈ 250ms（线性累加）", "color": "#f59e0b"},
                    {"id": "s3", "label": "asyncio 事件循环", "sub": "T1~T5 同时发起并在 await 让权", "color": "#3b82f6"},
                    {"id": "s4", "label": "异步总耗时", "sub": "≈ 50ms（约等于最慢单任务）", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "s1", "to": "s2", "label": "阻塞等待"},
                    {"from": "s3", "to": "s4", "label": "非阻塞并发重叠"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 装饰器（@decorator）与 functools.wraps",
                "content": (
                    "装饰器本质是「接收一个函数、返回一个增强版新函数」的高阶函数。写带参数的装饰器（如 `@retry_with_backoff(max_retries=3)`）需要三层嵌套：`工厂层(参数) -> 装饰器层(func) -> 包装执行层(*args, **kwargs)`。\n"
                    "务必在最内层 `wrapper` 上加 `@functools.wraps(func)`，否则原函数的 `__name__` 和 `__doc__` 会被覆盖成 `wrapper`，排查日志和生成文档时会一团糟。"
                ),
                "pitfalls": "重试装饰器不要裸抓 `Exception` 后无脑重试所有错误——像参数写错的 `ValueError` 或 401 鉴权失败重试一百次也没用，应通过 `exceptions=(...)` 参数精准指定可重试的异常类型。"
            },
            {
                "heading": "2. 生成器（yield）与惰性求值",
                "content": (
                    "普通函数 `return` 会一次性把整个列表算完塞进内存；含 `yield` 的函数调用后返回一个生成器对象，每次 `next()` 或 `for` 循环才执行到下一个 `yield` 暂停并吐出一个元素。\n"
                    "在 AI 开发中，大模型流式响应（SSE）和 GB 级语料逐行清洗几乎全部依赖生成器。"
                ),
                "pitfalls": "生成器是**一次性消耗品**！遍历完一遍就空了，第二次 `for` 遍历什么都拿不到；如果确实需要多次复用，记得显式转为 `list()`（仅限小数据）。"
            },
            {
                "heading": "3. python-dotenv 与 asyncio 异步入门",
                "content": (
                    "- `python-dotenv`：把 `DEEPSEEK_API_KEY=...` 写在项目根目录的 `.env` 文件里（并将 `.env` 加入 `.gitignore` 永不提交），代码里用 `dotenv_values()` 或 `load_dotenv()` 读取。\n"
                    "- `asyncio`：`async def` 定义协程函数，`await` 挂起当前协程把控制权交还给事件循环；`asyncio.gather(*tasks)` 并发跑多个协程；`asyncio.wait_for(coro, timeout=...)` 做超时控制；`asyncio.Semaphore(n)` 限制最大并发数。"
                ),
                "pitfalls": "在 `async def` 协程里**绝对不要调用 `time.sleep()` 或同步 `requests.get()`**！它们会把整个事件循环线程卡死，所有并发瞬间退化成串行；请改用 `await asyncio.sleep()` 和 `httpx.AsyncClient`。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：实现 .env 配置加载、指数退避重试装饰器与 yield 流式生成器",
                "file_path": "src/day13_decorators_and_env.py",
                "narration": "先打造三件工程利器：`load_env_settings()` 安全加载 `.env`、`@retry_with_backoff` 实现指数退避重试、`stream_text_chunks()` 用 `yield` 模拟大模型流式分块吐字。",
                "code": r'''"""
STARMIND-013 模块一：dotenv 配置加载、指数退避重试装饰器与 yield 流式生成器。
演示 python-dotenv、functools.wraps、typing 类型注解与生成器惰性求值。
"""

import functools
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Tuple, Type, TypeVar

from dotenv import dotenv_values

T = TypeVar("T")


@dataclass
class EnvSettings:
    """从 .env 安全加载的应用配置。"""

    model_name: str = "deepseek-chat"
    api_key: str = ""
    timeout_sec: float = 15.0
    max_retries: int = 3


def load_env_settings(env_path: Optional[Path] = None) -> EnvSettings:
    """
    安全解析 .env 文件并返回强类型 EnvSettings。
    文件不存在时平滑回退到默认配置，不污染全局 os.environ。
    """
    raw: dict[str, Optional[str]] = {}
    if env_path is not None and env_path.exists():
        raw = dict(dotenv_values(env_path))

    return EnvSettings(
        model_name=(raw.get("STARMIND_MODEL") or "deepseek-chat").strip(),
        api_key=(raw.get("STARMIND_API_KEY") or "").strip(),
        timeout_sec=float(raw.get("STARMIND_TIMEOUT") or 15.0),
        max_retries=int(raw.get("STARMIND_MAX_RETRIES") or 3),
    )


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 0.01,
    exceptions: Tuple[Type[BaseException], ...] = (RuntimeError, TimeoutError),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    指数退避重试装饰器。
    当被装饰函数抛出指定 exceptions 时，按 base_delay * 2^attempt 休眠后重试。
    """
    if max_retries < 1:
        raise ValueError("max_retries 必须 >= 1")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc: Optional[BaseException] = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == max_retries - 1:
                        break
                    sleep_sec = base_delay * (2 ** attempt)
                    if sleep_sec > 0:
                        time.sleep(sleep_sec)
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator


def stream_text_chunks(text: str, chunk_size: int = 4) -> Generator[str, None, None]:
    """使用 yield 按固定块大小惰性吐出文本，模拟大模型流式输出。"""
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须为正整数")
    for idx in range(0, len(text), chunk_size):
        yield text[idx : idx + chunk_size]


if __name__ == "__main__":
    # 1. 演示重试装饰器：前两次模拟接口抖动，第三次成功
    state = {"calls": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.005, exceptions=(RuntimeError,))
    def flaky_api_call(prompt: str) -> str:
        state["calls"] += 1
        if state["calls"] < 3:
            raise RuntimeError(f"第 {state['calls']} 次调用触发临时限流")
        return f"第 {state['calls']} 次成功返回：{prompt}"

    print(flaky_api_call("总结星辰数科年假制度"))

    # 2. 演示 yield 流式分块输出
    chunks = list(stream_text_chunks("星辰智脑正在流式生成回答！", chunk_size=4))
    print("流式分块结果:", chunks)
''',
                "explanation": (
                    "1. `dotenv_values(env_path)` 只读取指定 `.env` 文件并返回字典，比全局修改环境变量的 `load_dotenv()` 更干净、更易于并发和测试隔离。\n"
                    "2. `@retry_with_backoff` 保留了原函数元信息（`@functools.wraps`），并且仅重试 `exceptions` 元组中声明的可恢复异常。\n"
                    "3. `stream_text_chunks` 的返回类型标注为 `Generator[str, None, None]`，配合 `yield` 实现按需产出，零多余内存拷贝。"
                ),
                "expected_output": (
                    "第 3 次成功返回：总结星辰数科年假制度\n"
                    "流式分块结果: ['星辰智脑', '正在流式', '生成回答', '！']"
                )
            },
            {
                "step_title": "步骤二：编写基于 asyncio 的并发大模型批量调用与超时控制引擎",
                "file_path": "src/day13_async_llm_runner.py",
                "narration": "接下来咱们用 `asyncio` 写一个批量并发调用引擎：用 `asyncio.Semaphore` 限制最大并发度，用 `asyncio.wait_for` 给每个请求戴上超时安全帽，单个超时绝不拖垮整批任务！",
                "code": r'''"""
STARMIND-013 模块二：asyncio 异步并发大模型调用与超时控制引擎。
演示 async/await、asyncio.wait_for 超时兜底、asyncio.Semaphore 并发限流与 asyncio.gather。
"""

import asyncio
import time
from typing import Any, Dict, List


async def async_mock_llm_call(prompt: str, delay_sec: float = 0.04) -> Dict[str, Any]:
    """模拟异步大模型 I/O 推理请求（非阻塞等待）。"""
    await asyncio.sleep(delay_sec)
    return {
        "prompt": prompt,
        "status": "ok",
        "answer": f"[异步回复] 已处理：{prompt}",
    }


async def invoke_with_timeout(
    prompt: str,
    delay_sec: float,
    timeout_sec: float,
) -> Dict[str, Any]:
    """为单次异步大模型调用增加超时保护，超时后优雅降级而不抛出未捕获异常。"""
    try:
        return await asyncio.wait_for(
            async_mock_llm_call(prompt, delay_sec=delay_sec),
            timeout=timeout_sec,
        )
    except asyncio.TimeoutError:
        return {
            "prompt": prompt,
            "status": "timeout",
            "answer": f"请求超时（>{timeout_sec}s），已触发降级兜底。",
        }


async def batch_ask_concurrently(
    prompts: List[str],
    delay_sec: float = 0.04,
    timeout_sec: float = 0.2,
    max_concurrency: int = 5,
) -> List[Dict[str, Any]]:
    """
    带并发上限控制的异步批量提问调度器。
    通过 asyncio.Semaphore 防止瞬时并发过高打爆上游 API 限流。
    """
    if max_concurrency < 1:
        raise ValueError("max_concurrency 必须 >= 1")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def _bounded_task(p: str) -> Dict[str, Any]:
        async with semaphore:
            return await invoke_with_timeout(
                prompt=p,
                delay_sec=delay_sec,
                timeout_sec=timeout_sec,
            )

    tasks = [_bounded_task(p) for p in prompts]
    return list(await asyncio.gather(*tasks))


if __name__ == "__main__":
    questions = [f"批量问题 #{i}" for i in range(1, 6)]
    t0 = time.perf_counter()
    results = asyncio.run(
        batch_ask_concurrently(questions, delay_sec=0.05, timeout_sec=0.3, max_concurrency=5)
    )
    elapsed = (time.perf_counter() - t0) * 1000
    print(f"并发完成 {len(results)} 个任务（单个 50ms），总耗时仅 {elapsed:.1f}ms")
    print("首条结果:", results[0])
''',
                "explanation": (
                    "1. `asyncio.Semaphore(max_concurrency)` 是生产环境必备保护阀：哪怕一次性丢进来 1000 篇文档，同一时刻也只会放行 `max_concurrency` 个请求去调 API，绝不把自己打进 429 黑名单。\n"
                    "2. `asyncio.wait_for()` 在协程超过 `timeout_sec` 时会自动取消它并抛出 `asyncio.TimeoutError`，我们在函数内部接住并转成 `status='timeout'` 结构化结果，保证其他 99 个正常任务不受牵连。"
                ),
                "expected_output": (
                    "并发完成 5 个任务（单个 50ms），总耗时仅 52.3ms\n"
                    "首条结果: {'prompt': '批量问题 #1', 'status': 'ok', 'answer': '[异步回复] 已处理：批量问题 #1'}"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-013 自动化单元测试。"""

import asyncio
import inspect
import sys
import time
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day13_decorators_and_env import (
    load_env_settings,
    retry_with_backoff,
    stream_text_chunks,
)
from day13_async_llm_runner import batch_ask_concurrently, invoke_with_timeout


def test_load_env_settings_with_and_without_file(tmp_path: Path):
    # 缺失 .env 文件应平滑返回默认值
    default_cfg = load_env_settings(tmp_path / "missing.env")
    assert default_cfg.model_name == "deepseek-chat"
    assert default_cfg.api_key == ""

    # 存在 .env 文件时正确解析
    env_file = tmp_path / ".env"
    env_file.write_text(
        "STARMIND_MODEL=qwen-plus\nSTARMIND_API_KEY=sk-local-123\nSTARMIND_TIMEOUT=25.5\nSTARMIND_MAX_RETRIES=4\n",
        encoding="utf-8",
    )
    loaded = load_env_settings(env_file)
    assert loaded.model_name == "qwen-plus"
    assert loaded.api_key == "sk-local-123"
    assert loaded.timeout_sec == 25.5
    assert loaded.max_retries == 4


def test_retry_with_backoff_success_and_exhaustion():
    attempts = {"n": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.001, exceptions=(RuntimeError,))
    def recover_on_third() -> str:
        """恢复测试文档字符串。"""
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient error")
        return "recovered"

    assert recover_on_third.__name__ == "recover_on_third"
    assert recover_on_third() == "recovered"
    assert attempts["n"] == 3

    @retry_with_backoff(max_retries=2, base_delay=0.001, exceptions=(RuntimeError,))
    def always_fail() -> str:
        raise RuntimeError("permanent error")

    with pytest.raises(RuntimeError, match="permanent error"):
        always_fail()


def test_stream_text_chunks_generator():
    gen = stream_text_chunks("星辰智脑AI助手", chunk_size=3)
    assert inspect.isgenerator(gen)
    parts = list(gen)
    assert parts == ["星辰智", "脑AI", "助手"]
    assert "".join(parts) == "星辰智脑AI助手"


def test_async_concurrent_batch_and_timeout():
    prompts = [f"Q{i}" for i in range(5)]
    start = time.perf_counter()
    results = asyncio.run(
        batch_ask_concurrently(prompts, delay_sec=0.04, timeout_sec=0.3, max_concurrency=5)
    )
    elapsed = time.perf_counter() - start
    assert len(results) == 5
    assert all(r["status"] == "ok" for r in results)
    # 5 个 40ms 任务并发执行，总耗时应明显小于串行的 200ms
    assert elapsed < 0.16

    # 验证单请求超时优雅降级
    timeout_res = asyncio.run(invoke_with_timeout("慢查询", delay_sec=0.1, timeout_sec=0.02))
    assert timeout_res["status"] == "timeout"
    assert "超时" in timeout_res["answer"]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Architecture Review",
                "comment": "`Semaphore` 并发限流 + `wait_for` 超时隔离 + `dotenv_values` 零污染加载，三板斧非常稳健，后面第二阶段写 FastAPI 异步网关可以直接搬过去！",
                "resolution": "Approved。"
            },
            {
                "reviewer": "阿杰 (后端主程)",
                "role": "Performance Review",
                "comment": "单测里不仅测了功能正确性，还校验了并发耗时确实小于串行总耗时，这种带性能断言的异步测试很赞。",
                "resolution": "已合入主分支。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：带调用计数统计的装饰器 @count_calls",
                "difficulty": "基础巩固",
                "requirement": "编写一个装饰器 `count_calls(func)`，使用 `functools.wraps` 保留函数元信息，并在包装函数上维护 `wrapper.call_count` 属性，每次调用自动加 1。",
                "hint": "在定义完 `wrapper` 后初始化 `wrapper.call_count = 0`，在 `wrapper` 内部先 `wrapper.call_count += 1` 再调用原函数。",
                "solution_code": r'''"""Day 13 课后题 1：函数调用次数统计装饰器。"""

import functools
from typing import Any, Callable


def count_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    """统计被装饰函数的累计调用次数，挂载在 wrapper.call_count 属性上。"""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        wrapper.call_count += 1  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    wrapper.call_count = 0  # type: ignore[attr-defined]
    return wrapper


@count_calls
def greet(name: str) -> str:
    return f"你好，{name}"


if __name__ == "__main__":
    print(greet("林产品"))
    print(greet("阿杰"))
    print("累计调用次数:", greet.call_count)
''',
                "solution_analysis": "Python 中函数也是对象，可以直接挂载自定义属性（如 `call_count`），配合 `@functools.wraps` 既优雅又便于监控埋点。"
            },
            {
                "title": "企业实战：基于 yield 的流式错误日志过滤生成器",
                "difficulty": "企业实战",
                "requirement": "编写生成器函数 `iter_error_lines(lines: Iterable[str], level: str = 'ERROR') -> Generator[str, None, None]`，惰性遍历海量日志行，仅 `yield` 去除首尾空白后包含 `[ERROR]`（或指定 level）的日志行。",
                "hint": "在 `for line in lines:` 中判断 `f'[{level.upper()}]' in line`，命中则 `yield line.strip()`。",
                "solution_code": r'''"""Day 13 课后题 2：低内存流式错误日志过滤生成器。"""

from typing import Generator, Iterable


def iter_error_lines(
    lines: Iterable[str],
    level: str = "ERROR",
) -> Generator[str, None, None]:
    """惰性过滤包含指定日志级别的日志行，适合处理 GB 级大日志文件。"""
    tag = f"[{level.upper()}]"
    for line in lines:
        if tag in line:
            yield line.strip()


if __name__ == "__main__":
    sample_logs = [
        "2026-05-13 10:00:01 [INFO] 服务启动完成\n",
        "2026-05-13 10:00:05 [ERROR] 模型接口返回 429 限流\n",
        "2026-05-13 10:00:08 [WARN] 响应延迟偏高\n",
        "2026-05-13 10:00:12 [ERROR] 数据库连接超时\n",
    ]
    for err in iter_error_lines(sample_logs):
        print("捕获告警:", err)
''',
                "solution_analysis": "传入 `Iterable[str]`（既可以是打开的文件对象也可以是列表），配合 `yield` 实现 O(1) 恒定内存占用过滤大日志。"
            },
            {
                "title": "架构进阶：带并发限流的异步多节点健康探活器",
                "difficulty": "架构进阶",
                "requirement": "编写异步函数 `async_health_check_all(services: list[tuple[str, float]], timeout_sec: float = 0.05, max_concurrency: int = 3) -> dict[str, str]`。其中每个元组为 `(服务名, 模拟响应耗时秒数)`，在超时内响应记为 `'healthy'`，超时记为 `'unhealthy'`，返回服务名到状态的映射字典。",
                "hint": "结合 `asyncio.Semaphore(max_concurrency)`、`asyncio.wait_for(asyncio.sleep(delay), timeout=timeout_sec)` 和 `asyncio.gather`。",
                "solution_code": r'''"""Day 13 课后题 3：带并发限流与超时判定的异步服务探活器。"""

import asyncio
from typing import Dict, List, Tuple


async def async_health_check_all(
    services: List[Tuple[str, float]],
    timeout_sec: float = 0.05,
    max_concurrency: int = 3,
) -> Dict[str, str]:
    """并发探活多个微服务节点，按超时阈值标记 healthy / unhealthy。"""
    sem = asyncio.Semaphore(max_concurrency)

    async def _probe(name: str, latency: float) -> Tuple[str, str]:
        async with sem:
            try:
                await asyncio.wait_for(asyncio.sleep(latency), timeout=timeout_sec)
                return name, "healthy"
            except asyncio.TimeoutError:
                return name, "unhealthy"

    pairs = await asyncio.gather(*(_probe(n, d) for n, d in services))
    return dict(pairs)


if __name__ == "__main__":
    nodes = [
        ("deepseek-gateway", 0.01),
        ("qwen-gateway", 0.02),
        ("slow-legacy-rag", 0.12),
    ]
    print(asyncio.run(async_health_check_all(nodes, timeout_sec=0.05)))
''',
                "solution_analysis": "这道题直接对应生产级 AI 网关的定时探活后台协程：并发探测几十个上游模型节点，自动摘除超时慢节点。"
            }
        ],
        "extra_deep_dive": (
            "【源码级避坑：什么时候用 asyncio，什么时候用多进程 multiprocessing？】\n"
            "很多同学学完 `asyncio` 以为它能加速一切，结果拿它去跑 CPU 密集型的本地图片压缩或矩阵乘法，发现一点没变快！\n"
            "记住铁律：**`asyncio` 跑在单线程事件循环里，只加速 I/O 密集型任务（调大模型 API、查数据库、读网络文件）**，因为在 `await` 等网卡回包时 CPU 可以去伺候其他几百个请求；"
            "而纯 CPU 密集型计算（本地模型推理、大体积加密压缩）会霸占 CPU 不放权，必须交给 `ProcessPoolExecutor` 多进程或底层 C++/Rust 扩展去跑！"
        )
    },

    # =========================================================================
    # DAY 14: 阶段考核项目一——命令行多轮对话 AI 助手
    # =========================================================================
    {
        "day": 14,
        "stage": 1,
        "stage_name": "第一阶段：Python 编程基础",
        "week": 2,
        "week_name": "第 2 周：面向对象、工程化与命令行 AI 助手实战",
        "title": "阶段考核项目一——命令行多轮对话 AI 助手",
        "subtitle": "综合运用 OOP、JSON 持久化、异常处理与斜杠指令系统，交付星辰智脑 CLI 多轮对话助手 v1.0",
        "gitlab_ticket": "STARMIND-014",
        "git_branch": "feat/day14-milestone1-cli-chat-assistant",
        "git_commit": "feat(day14): 交付阶段考核项目一——支持多轮记忆、JSON持久化与斜杠指令的命令行AI助手v1.0",
        "prev_recap": "昨天咱们拿下了装饰器、`yield` 生成器、`python-dotenv` 和 `asyncio` 异步并发，第一阶段所有的核心技术拼图已经全部集齐。",
        "next_preview": "恭喜通关第一阶段（14 天 Python 工程基础）！下周一（Day 15，第二阶段：Web 后端与数据库工程）咱们将把今天这个命令行助手正式升级成企业级 **FastAPI + 数据库持久化** 的多人在线 Web 服务！",
        "narrator_opening": (
            "不知不觉来到第 14 天——**第一阶段毕业考核日（STARMIND-014）**！\n"
            "林产品今天亲自来验收咱们的「星辰智脑 CLI 多轮对话助手 v1.0」。需求很明确，不再是 Day 12 那种问完就忘的单轮玩具，而是真正能连续聊天的生产力工具：\n"
            "1）**多轮上下文记忆**：维护标准 `messages` 对话数组，并带滑动窗口裁剪，防止聊久了 Token 爆炸；\n"
            "2）**JSON 对话持久化**：敲 `/save` 一键把整段对话保存到本地 JSON，下次还能 `load_from_json` 完整恢复接着聊；\n"
            "3）**完整斜杠指令集**：`/help`、`/history`、`/stats`、`/clear`（清空历史但保留系统人设）、`/exit`；\n"
            "4）**生产级异常处理**：后端报错不闪退，而且必须把刚才塞进去却没拿到回复的那条 `user` 消息**事务回滚**掉！\n"
            "今天把这两份代码和全套 pytest 验收测试跑绿，你的第一阶段就圆满毕业了！"
        ),
        "narrator_closing": (
            "啪啪啪！老陈给你鼓个掌——从 Day 1 连虚拟环境都不熟，到 Day 14 独立交付一个架构清晰、记忆可控、支持 JSON 持久化与异常回滚的多轮对话 CLI 助手，两周时间你已经跨过了 80% 自学者倒下的工程门槛！\n"
            "周末好好复盘一下 `ConversationMemory` 和 `StarMindCLIAssistant` 的解耦设计：正是因为今天把「记忆存储」「模型后端」「交互外壳」拆得干干净净，下周咱们迁移到 FastAPI Web 接口时，核心业务代码几乎一行不用重写！"
        ),
        "business_prd": {
            "background": "作为星辰智脑第一阶段里程碑考核交付物，研发团队需要交付一个可独立运行、可测试、具备完整多轮对话体验的命令行 AI 助手 v1.0，作为后续 Web 版与 Agent 版的最小可行内核（MVP）。",
            "pain_points": [
                "Day 12 的单轮问答工具没有记忆，用户追问「刚才那个流程要几天？」时模型完全不知道上下文。",
                "终端一关闭，有价值的问答记录全部丢失，无法归档或下次续聊。",
                "用户缺少快捷管理指令（清屏重置话题、查看 Token 消耗、导出存档），且模型异常时容易留下残缺的孤立 user 消息污染上下文。"
            ],
            "goals": [
                "实现 `ConversationMemory` 类：管理 `system` 人设、`messages` 多轮历史、滑动窗口裁剪、Token 估算与 JSON 持久化读写。",
                "实现 `StarMindCLIAssistant` 类：内置斜杠指令路由（`/help`、`/history`、`/stats`、`/clear`、`/save`、`/exit`）与可替换的对话后端接口。",
                "实现异常事务回滚机制：模型调用失败时不崩溃退出，并自动撤销本次未完成的 `user` 消息。"
            ],
            "acceptance_criteria": [
                "连续多轮提问时，后端能接收到完整历史 `messages`（含首条 `system` 消息），且超出窗口上限时自动保留最新 N 条对话。",
                "`/clear` 清空对话历史但保留 `system_prompt`；`/save` 成功落盘 UTF-8 JSON 并可通过 `load_from_json` 完整还原。",
                "模型后端抛出异常时，助手返回友好错误提示、不崩溃，且记忆中不会残留失败的 `user` 消息。",
                "全部核心类与斜杠指令通过无阻塞 `pytest` 自动化验收测试。"
            ],
            "non_functional": [
                "零外网依赖即可运行完整多轮演示与测试，同时通过 `BaseChatBackend` 接口无缝兼容 Day 12 的真实 HTTP 大模型客户端。",
                "JSON 持久化文件使用 `utf-8` 编码与 `ensure_ascii=False` 缩进格式化，人类可直接阅读。"
            ]
        },
        "schedule": [
            {"slot": "上午 09:00-12:00", "topic": "多轮对话记忆引擎与 JSON 持久化设计", "detail": "编写 ConversationMemory，实现 messages 管理、滑动窗口、回滚机制与 JSON 存取。"},
            {"slot": "下午 14:00-17:30", "topic": "命令行 AI 助手主控类与斜杠指令系统", "detail": "实现 LocalSmartMockBackend、斜杠指令路由与容错 REPL 主循环。"},
            {"slot": "晚间 19:00-20:30", "topic": "阶段一综合验收测试与代码走查", "detail": "编写覆盖记忆、持久化、指令、异常回滚的完整 pytest 套件，模拟 GitLab MR 评审。"},
            {"slot": "复盘 20:30-21:00", "topic": "第一阶段知识图谱复盘与进阶作业", "detail": "串联 Day 1~14 工程技能，完成 3 道考核拓展作业。"}
        ],
        "architecture_design": (
            "阶段考核项目一严格践行「关注点分离（Separation of Concerns）」的面向对象架构，拆分为两个高内聚低耦合模块：\n"
            "1. **对话记忆与持久化层（day14_session_memory.py）**：\n"
            "   - `ChatMessage` 封装单条消息的角色（`user`/`assistant`）、正文与 UTC 时间戳。\n"
            "   - `ConversationMemory` 负责维护多轮上下文状态，提供 `build_payload_messages()` 自动将 `system` 置顶并按 `max_history_messages` 执行滑动窗口截断；提供 `rollback_last_user_message()` 保证异常时对话状态原子一致；提供 `save_to_json()` / `load_from_json()` 实现跨进程会话恢复。\n"
            "2. **命令行助手主控与后端适配层（day14_cli_assistant.py）**：\n"
            "   - `BaseChatBackend` 定义极简抽象接口 `complete(messages) -> str`，既可接入内置的 `LocalSmartMockBackend`（能够真实读取历史 `messages` 演示多轮记忆），也可直接包装 Day 12 的 `StarMindHTTPClient` 接入 DeepSeek/通义千问。\n"
            "   - `StarMindCLIAssistant` 将输入行统一分发至 `handle_line()`，清晰隔离斜杠指令处理与普通对话处理，`run_repl(input_lines=...)` 既支持终端真人交互也支持自动化脚本回放。"
        ),
        "diagrams": [
            {
                "title": "命令行多轮对话主循环（REPL）与斜杠指令流程图",
                "kind": "flowchart",
                "caption": "展示用户输入进入助手后如何分流为空输入拦截、斜杠指令路由与多轮对话调用，并在异常时回滚状态。",
                "nodes": [
                    {"id": "n1", "label": "接收用户输入行", "sub": "REPL / 脚本输入", "color": "#3b82f6"},
                    {"id": "n2", "label": "以 / 开头？", "sub": "区分指令与普通提问", "color": "#8b5cf6"},
                    {"id": "n3", "label": "斜杠指令路由器", "sub": "/clear /save /stats /exit", "color": "#06b6d4"},
                    {"id": "n4", "label": "写入 user 消息并调模型", "sub": "携带完整 messages 上下文", "color": "#f59e0b"},
                    {"id": "n5", "label": "成功写入 assistant 回复", "sub": "更新轮数与 Token 统计", "color": "#10b981"},
                    {"id": "n6", "label": "异常捕获与消息回滚", "sub": "rollback_last_user_message", "color": "#ef4444"}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "label": "非空文本"},
                    {"from": "n2", "to": "n3", "label": "是（指令）"},
                    {"from": "n2", "to": "n4", "label": "否（对话）"},
                    {"from": "n4", "to": "n5", "label": "调用成功"},
                    {"from": "n4", "to": "n6", "label": "抛出异常"}
                ]
            },
            {
                "title": "星辰智脑 CLI 助手 v1.0 四层模块化架构图",
                "kind": "architecture",
                "caption": "展示交互外壳、指令路由、记忆持久化与可插拔大模型后端之间的清晰依赖边界。",
                "nodes": [
                    {"id": "a1", "label": "CLI REPL 外壳", "sub": "run_repl() / handle_line()", "color": "#3b82f6"},
                    {"id": "a2", "label": "Command Router", "sub": "/help /clear /save /history", "color": "#8b5cf6"},
                    {"id": "a3", "label": "ConversationMemory", "sub": "滑动窗口 + JSON 持久化", "color": "#f59e0b"},
                    {"id": "a4", "label": "BaseChatBackend", "sub": "Mock 后端 / DeepSeek HTTP", "color": "#10b981"},
                    {"id": "a5", "label": "本地 sessions/*.json", "sub": "UTF-8 对话存档文件", "color": "#06b6d4"}
                ],
                "edges": [
                    {"from": "a1", "to": "a2", "label": "解析斜杠指令"},
                    {"from": "a1", "to": "a3", "label": "读写多轮上下文"},
                    {"from": "a1", "to": "a4", "label": "发送 messages 推理"},
                    {"from": "a3", "to": "a5", "label": "save / load JSON"}
                ]
            },
            {
                "title": "多轮对话上下文组装与异常回滚时序图",
                "kind": "sequence",
                "caption": "展示第 2 轮追问如何自动携带第 1 轮记忆，以及第 3 轮触发异常时如何安全回滚保证历史干净。",
                "nodes": [
                    {"id": "q1", "label": "User 用户", "sub": "输入多轮提问", "color": "#3b82f6"},
                    {"id": "q2", "label": "StarMindCLIAssistant", "sub": "协调记忆与调用", "color": "#8b5cf6"},
                    {"id": "q3", "label": "ConversationMemory", "sub": "维护 messages 列表", "color": "#f59e0b"},
                    {"id": "q4", "label": "LLM Backend", "sub": "无状态推理引擎", "color": "#10b981"}
                ],
                "edges": [
                    {"from": "q1", "to": "q2", "label": "1. 发送新问题"},
                    {"from": "q2", "to": "q3", "label": "2. add_user_message + build_payload"},
                    {"from": "q2", "to": "q4", "label": "3. complete(完整历史 messages)"},
                    {"from": "q4", "to": "q2", "label": "4. 返回回复 或 抛出异常"},
                    {"from": "q2", "to": "q3", "label": "5. 成功追加回复 / 失败则 rollback"}
                ]
            }
        ],
        "knowledge_notes": [
            {
                "heading": "1. 多轮对话本质：大模型是「无状态」的",
                "content": (
                    "很多人误以为大模型服务器替你记住了上一句话，其实 HTTP API 是完全无状态（Stateless）的！"
                    "所谓「多轮记忆」，全靠客户端把 `[system, user_1, assistant_1, user_2, assistant_2, user_3]` 整串历史记录每次重新打包发给模型。\n"
                    "因此客户端必须做好**滑动窗口裁剪**（始终保留 `system` + 最近 N 条消息），否则聊上 50 轮不仅 Token 费暴涨，还会直接触发模型上下文长度超限报错。"
                ),
                "pitfalls": "裁剪历史消息时，千万别一刀把索引 0 的 `system` 人设消息也截掉了！务必把 `system_prompt` 独立保存，每次组装 payload 时再拼在最前面。"
            },
            {
                "heading": "2. 失败回滚：保护 messages 奇偶交替完整性",
                "content": (
                    "主流大模型 API 严格要求 `messages` 中 `user` 和 `assistant` 交替出现。如果在调用模型前先执行了 `add_user_message()`，结果这次网络超时报错了，"
                    "如果不把刚才那条 `user` 消息 `pop` 回滚掉，下一次用户重新提问就会出现连续两条 `user` 消息，导致后续所有请求被 API 拒绝（HTTP 400）！"
                ),
                "pitfalls": "在 `except Exception:` 分支里调用 `memory.rollback_last_user_message()`，是一个极小但极显功力的生产级细节。"
            },
            {
                "heading": "3. CLI 项目的工程化可测试性（依赖注入）",
                "content": (
                    "写命令行程序最容易犯的错，就是把 `while True: input()`、文件读写和网络请求全揉在一个文件顶层，导致完全没法写单元测试。\n"
                    "正确做法是：**将单行处理逻辑抽成纯方法 `handle_line(raw_line) -> (should_continue, reply)`**，并把后端引擎 `backend` 和保存目录 `save_dir` 通过构造函数注入——这样 `pytest` 不用模拟键盘敲击也能 100% 测完每一条斜杠指令！"
                ),
                "pitfalls": "涉及文件名参数的 `/save <filename>` 指令，要注意用 `Path(filename).name` 去掉恶意路径前缀（如 `../../etc/passwd`），防止路径穿越漏洞。"
            }
        ],
        "code_steps": [
            {
                "step_title": "步骤一：实现多轮对话记忆引擎与 JSON 持久化模块",
                "file_path": "src/day14_session_memory.py",
                "narration": "先搭好核心数据结构 `ConversationMemory`：负责 `messages` 增删、滑动窗口截断、失败回滚、Token 估算以及 UTF-8 JSON 持久化存取。",
                "code": r'''"""
STARMIND-014 模块一：多轮对话记忆引擎与 JSON 持久化存储。
负责维护 system 人设、多轮 messages 历史、滑动窗口裁剪、异常回滚与 JSON 读写。
"""

import json
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class ChatMessage:
    """单条对话消息记录。"""

    role: str  # "user" 或 "assistant"
    content: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )


class ConversationMemory:
    """星辰智脑多轮对话上下文记忆管理器。"""

    def __init__(
        self,
        system_prompt: str = "你是杭州星辰数科企业 AI 助手「星辰智脑」，请提供专业简洁的中文解答。",
        max_history_messages: int = 10,
        session_id: str = "default-session",
    ) -> None:
        if max_history_messages < 2:
            raise ValueError("max_history_messages 至少为 2（一问一答）")
        self.system_prompt = system_prompt
        self.max_history_messages = max_history_messages
        self.session_id = session_id
        self.messages: List[ChatMessage] = []

    def add_user_message(self, content: str) -> ChatMessage:
        """追加一条用户消息。"""
        cleaned = content.strip()
        if not cleaned:
            raise ValueError("用户消息不能为空")
        msg = ChatMessage(role="user", content=cleaned)
        self.messages.append(msg)
        return msg

    def add_assistant_message(self, content: str) -> ChatMessage:
        """追加一条助手回复消息。"""
        msg = ChatMessage(role="assistant", content=content.strip())
        self.messages.append(msg)
        return msg

    def rollback_last_user_message(self) -> bool:
        """当模型调用失败时回滚最后一条孤立的 user 消息，防止上下文损坏。"""
        if self.messages and self.messages[-1].role == "user":
            self.messages.pop()
            return True
        return False

    def build_payload_messages(self) -> List[Dict[str, str]]:
        """
        构造发送给大模型的标准 messages 数组：
        始终保留 system_prompt 在首位 + 最近 max_history_messages 条历史消息。
        """
        window = self.messages[-self.max_history_messages :]
        payload: List[Dict[str, str]] = [{"role": "system", "content": self.system_prompt}]
        for item in window:
            payload.append({"role": item.role, "content": item.content})
        return payload

    def clear(self) -> None:
        """清空多轮历史消息（保留 system_prompt 人设）。"""
        self.messages.clear()

    def get_stats(self) -> Dict[str, Any]:
        """统计当前会话轮数、消息总数及粗略 Token 估算。"""
        user_turns = sum(1 for m in self.messages if m.role == "user")
        total_chars = len(self.system_prompt) + sum(len(m.content) for m in self.messages)
        return {
            "session_id": self.session_id,
            "turns": user_turns,
            "message_count": len(self.messages),
            "estimated_tokens": max(1, int(total_chars * 1.2)),
            "window_limit": self.max_history_messages,
        }

    def save_to_json(self, file_path: Path) -> Path:
        """将当前多轮对话完整持久化为 UTF-8 JSON 文件。"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "session_id": self.session_id,
            "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "system_prompt": self.system_prompt,
            "max_history_messages": self.max_history_messages,
            "messages": [asdict(m) for m in self.messages],
        }
        file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return file_path

    @classmethod
    def load_from_json(cls, file_path: Path) -> "ConversationMemory":
        """从 JSON 存档文件恢复历史会话记忆。"""
        if not file_path.exists():
            raise FileNotFoundError(f"会话文件不存在: {file_path}")
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"会话 JSON 文件已损坏: {exc}") from exc

        if not isinstance(raw, dict) or not isinstance(raw.get("messages"), list):
            raise ValueError("会话 JSON 结构无效：缺少 messages 列表")

        mem = cls(
            system_prompt=str(raw.get("system_prompt", "")),
            max_history_messages=int(raw.get("max_history_messages", 10)),
            session_id=str(raw.get("session_id", "restored-session")),
        )
        for item in raw["messages"]:
            mem.messages.append(
                ChatMessage(
                    role=str(item["role"]),
                    content=str(item["content"]),
                    timestamp=str(item.get("timestamp", "")),
                )
            )
        return mem


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        mem = ConversationMemory(session_id="demo-014", max_history_messages=4)
        mem.add_user_message("我叫小王，负责杭州研发部。")
        mem.add_assistant_message("你好小王！很高兴为杭州研发部服务。")
        saved = mem.save_to_json(Path(tmp) / "chat_history.json")
        restored = ConversationMemory.load_from_json(saved)
        print("持久化恢复成功，统计信息:", restored.get_stats())
        print("Payload 消息数:", len(restored.build_payload_messages()))
''',
                "explanation": (
                    "1. `build_payload_messages()` 通过切片 `self.messages[-self.max_history_messages:]` 实现优雅的滑动窗口裁剪，同时确保 `system_prompt` 永远稳居第一位。\n"
                    "2. `load_from_json()` 是 `@classmethod` 工厂方法，负责校验文件存在性、JSON 合法性与字段完整性，读到损坏文件时抛出清晰的 `ValueError`。"
                ),
                "expected_output": (
                    "持久化恢复成功，统计信息: {'session_id': 'demo-014', 'turns': 1, 'message_count': 2, 'estimated_tokens': 81, 'window_limit': 4}\n"
                    "Payload 消息数: 3"
                )
            },
            {
                "step_title": "步骤二：实现支持斜杠指令与异常回滚的命令行多轮 AI 助手 v1.0",
                "file_path": "src/day14_cli_assistant.py",
                "narration": "现在把记忆引擎、可插拔后端和斜杠指令系统拼装成完整的 `StarMindCLIAssistant`！注意看 `LocalSmartMockBackend` 会真正读取前几轮 `messages` 里的上下文（比如记住用户的名字），离线就能体验真实多轮记忆！",
                "code": r'''"""
STARMIND-014 模块二：星辰智脑命令行多轮对话 AI 助手 v1.0。
支持多轮上下文记忆、/help /history /stats /clear /save /exit 斜杠指令、
JSON 持久化存档与模型异常自动回滚。
"""

import re
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from day14_session_memory import ConversationMemory


class BaseChatBackend(ABC):
    """大模型对话后端抽象基类，便于无缝切换本地 Mock 或 DeepSeek/通义千问 HTTP 客户端。"""

    @abstractmethod
    def complete(self, messages: List[Dict[str, str]]) -> str:
        """接收标准 OpenAI 格式 messages 列表并返回助手回复正文。"""


class LocalSmartMockBackend(BaseChatBackend):
    """具备基础多轮上下文记忆能力的离线模拟后端（零外网依赖）。"""

    NAME_PATTERN = re.compile(r"(?:我叫|我是)([\u4e00-\u9fa5a-zA-Z0-9_]{1,12})")

    def complete(self, messages: List[Dict[str, str]]) -> str:
        user_msgs = [m["content"] for m in messages if m.get("role") == "user"]
        if not user_msgs:
            return "你好！我是星辰智脑，请问有什么可以帮您？"

        latest = user_msgs[-1]
        if "__TRIGGER_ERROR__" in latest:
            raise RuntimeError("模拟上游大模型网关 503 临时故障")

        # 扫描全部历史 user 消息，提取用户此前介绍过的名字（演示多轮记忆）
        remembered_name: Optional[str] = None
        for text in user_msgs:
            match = self.NAME_PATTERN.search(text)
            if match:
                candidate = match.group(1)
                if not any(q in candidate for q in ("什么", "谁", "吗", "呢")):
                    remembered_name = candidate

        if "我是谁" in latest or "我叫什么" in latest or "记得我" in latest:
            if remembered_name:
                return f"当然记得！你之前告诉我，你叫「{remembered_name}」。当前已累计记忆 {len(user_msgs)} 轮提问。"
            return "你还没有告诉我你的名字呢，可以说「我叫XXX」让我记住你！"

        if "报销" in latest:
            prefix = f"{remembered_name}同学，" if remembered_name else ""
            return f"{prefix}星辰数科报销请在钉钉提交费用单，500元以上需主管与财务双审批。"

        prefix = f"收到，{remembered_name}！" if remembered_name else "收到！"
        return f"{prefix}你刚才说：「{latest}」（当前上下文共携带 {len(messages)} 条消息）。"


class StarMindCLIAssistant:
    """星辰智脑命令行多轮对话助手主控类。"""

    HELP_TEXT = (
        "可用指令列表：\n"
        "  /help              查看帮助信息\n"
        "  /history           查看当前对话历史\n"
        "  /stats             查看对话轮数与 Token 估算\n"
        "  /clear             清空当前多轮记忆（保留系统人设）\n"
        "  /save [文件名]     保存对话记录为 JSON 文件（默认 session_history.json）\n"
        "  /exit              退出助手"
    )

    def __init__(
        self,
        backend: Optional[BaseChatBackend] = None,
        memory: Optional[ConversationMemory] = None,
        save_dir: Optional[Path] = None,
    ) -> None:
        self.backend = backend or LocalSmartMockBackend()
        self.memory = memory or ConversationMemory()
        self.save_dir = save_dir or Path("sessions")

    def _handle_command(self, line: str) -> Tuple[bool, str]:
        """解析并执行以 / 开头的斜杠管理指令。"""
        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd in {"/exit", "/quit"}:
            return False, "再见！感谢使用星辰智脑命令行 AI 助手。"

        if cmd == "/help":
            return True, self.HELP_TEXT

        if cmd == "/clear":
            self.memory.clear()
            return True, "已清空当前多轮对话记忆（系统人设已保留）。"

        if cmd == "/stats":
            st = self.memory.get_stats()
            return True, (
                f"会话ID: {st['session_id']} | 对话轮数: {st['turns']} | "
                f"消息条数: {st['message_count']} | 估算Tokens: {st['estimated_tokens']}"
            )

        if cmd == "/history":
            if not self.memory.messages:
                return True, "当前暂无对话历史。"
            lines = [f"[{i}] {m.role}: {m.content}" for i, m in enumerate(self.memory.messages, 1)]
            return True, "\n".join(lines)

        if cmd == "/save":
            # 使用 Path(arg).name 防止路径穿越漏洞
            safe_name = Path(arg).name if arg else "session_history.json"
            if not safe_name.endswith(".json"):
                safe_name += ".json"
            target = self.save_dir / safe_name
            saved_path = self.memory.save_to_json(target)
            return True, f"对话历史已保存至：{saved_path.as_posix()}"

        return True, f"未知指令：{cmd}，输入 /help 查看所有支持的指令。"

    def handle_line(self, raw_line: str) -> Tuple[bool, str]:
        """
        处理单行用户输入，返回 (是否继续运行, 输出文本)。
        """
        text = raw_line.strip()
        if not text:
            return True, "提示：输入不能为空，请输入问题或 /help 查看指令。"

        if text.startswith("/"):
            return self._handle_command(text)

        self.memory.add_user_message(text)
        try:
            payload = self.memory.build_payload_messages()
            reply = self.backend.complete(payload)
        except Exception as exc:
            # 异常时回滚刚才塞进去的 user 消息，确保历史状态不被污染
            self.memory.rollback_last_user_message()
            return True, f"抱歉，模型调用出现异常（已自动回滚本轮输入）：{exc}"

        self.memory.add_assistant_message(reply)
        return True, f"星辰智脑 > {reply}"

    def run_repl(self, input_lines: Optional[List[str]] = None) -> List[str]:
        """
        运行多轮对话主循环。
        - 传入 input_lines 时非阻塞逐行回放（用于演示与自动化测试）；
        - 未传 input_lines 时进入终端交互式 input() 模式。
        """
        transcript: List[str] = []
        script_iter = iter(input_lines) if input_lines is not None else None

        while True:
            if script_iter is not None:
                try:
                    raw = next(script_iter)
                except StopIteration:
                    break
            else:
                try:
                    raw = input("你 > ")
                except (EOFError, KeyboardInterrupt):
                    transcript.append("检测到中断信号，已安全退出。")
                    break

            keep_going, out = self.handle_line(raw)
            transcript.append(out)
            if not keep_going:
                break

        return transcript


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        assistant = StarMindCLIAssistant(save_dir=Path(tmp))
        demo_script = [
            "你好，我叫林产品，在杭州研发中心工作。",
            "你还记得我叫什么吗？",
            "/stats",
            "/save milestone1_demo.json",
            "/clear",
            "你还记得我叫什么吗？",
            "/exit",
        ]
        for user_in, bot_out in zip(demo_script, assistant.run_repl(demo_script)):
            print(f"你 > {user_in}")
            print(bot_out)
            print("-" * 55)
''',
                "explanation": (
                    "1. `LocalSmartMockBackend` 通过正则扫描历史 `user` 消息来记住用户名字，当用户输入 `/clear` 后再追问「还记得我叫什么吗？」，助手会诚实回答不记得，直观验证了多轮记忆与清空指令的真实效果！\n"
                    "2. `/save` 指令使用 `Path(arg).name` 清洗文件名，杜绝用户误输 `../../xx.json` 覆盖系统其他目录文件。\n"
                    "3. `handle_line()` 在 `except Exception` 中执行 `rollback_last_user_message()`，彻底杜绝半截对话污染上下文。"
                ),
                "expected_output": (
                    "你 > 你好，我叫林产品，在杭州研发中心工作。\n"
                    "星辰智脑 > 收到，林产品！你刚才说：「你好，我叫林产品，在杭州研发中心工作。」（当前上下文共携带 2 条消息）。\n"
                    "-------------------------------------------------------\n"
                    "你 > 你还记得我叫什么吗？\n"
                    "星辰智脑 > 当然记得！你之前告诉我，你叫「林产品」。当前已累计记忆 2 轮提问。\n"
                    "-------------------------------------------------------\n"
                    "你 > /stats\n"
                    "会话ID: default-session | 对话轮数: 2 | 消息条数: 4 | 估算Tokens: 210\n"
                    "-------------------------------------------------------\n"
                    "你 > /save milestone1_demo.json\n"
                    "对话历史已保存至：.../milestone1_demo.json\n"
                    "-------------------------------------------------------\n"
                    "你 > /clear\n"
                    "已清空当前多轮对话记忆（系统人设已保留）。\n"
                    "-------------------------------------------------------\n"
                    "你 > 你还记得我叫什么吗？\n"
                    "星辰智脑 > 你还没有告诉我你的名字呢，可以说「我叫XXX」让我记住你！\n"
                    "-------------------------------------------------------\n"
                    "你 > /exit\n"
                    "再见！感谢使用星辰智脑命令行 AI 助手。\n"
                    "-------------------------------------------------------"
                )
            }
        ],
        "unit_test_code": r'''"""STARMIND-014 阶段考核项目一自动化验收测试。"""

import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from day14_session_memory import ConversationMemory
from day14_cli_assistant import StarMindCLIAssistant


def test_memory_sliding_window_and_json_roundtrip(tmp_path: Path):
    mem = ConversationMemory(system_prompt="你是星辰助教", max_history_messages=2, session_id="s-01")
    mem.add_user_message("第1问")
    mem.add_assistant_message("第1答")
    mem.add_user_message("第2问")
    mem.add_assistant_message("第2答")

    payload = mem.build_payload_messages()
    # system 置顶 + 最近 2 条消息 = 共 3 条
    assert len(payload) == 3
    assert payload[0] == {"role": "system", "content": "你是星辰助教"}
    assert payload[1]["content"] == "第2问"
    assert payload[2]["content"] == "第2答"

    saved_file = mem.save_to_json(tmp_path / "history.json")
    restored = ConversationMemory.load_from_json(saved_file)
    assert restored.session_id == "s-01"
    assert restored.system_prompt == "你是星辰助教"
    assert len(restored.messages) == 4

    # 损坏的 JSON 必须抛出 ValueError
    broken = tmp_path / "broken.json"
    broken.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError):
        ConversationMemory.load_from_json(broken)


def test_cli_assistant_multiturn_commands_and_persistence(tmp_path: Path):
    assistant = StarMindCLIAssistant(save_dir=tmp_path)

    # 1. 多轮记忆验证
    ok1, out1 = assistant.handle_line("你好，我叫阿杰")
    assert ok1 is True and "阿杰" in out1

    ok2, out2 = assistant.handle_line("你还记得我叫什么吗？")
    assert ok2 is True and "阿杰" in out2

    # 2. /stats 与 /history 与 /save
    _, stats_out = assistant.handle_line("/stats")
    assert "对话轮数: 2" in stats_out

    _, hist_out = assistant.handle_line("/history")
    assert "阿杰" in hist_out

    _, save_out = assistant.handle_line("/save my_chat")
    saved_path = tmp_path / "my_chat.json"
    assert saved_path.exists()
    assert "my_chat.json" in save_out

    # 3. /clear 清空后忘记上下文，但系统人设仍在
    _, clear_out = assistant.handle_line("/clear")
    assert "已清空" in clear_out
    assert len(assistant.memory.messages) == 0

    _, out3 = assistant.handle_line("你还记得我叫什么吗？")
    assert "还没有告诉我" in out3

    # 4. /exit 正常结束循环
    keep_going, exit_out = assistant.handle_line("/exit")
    assert keep_going is False
    assert "再见" in exit_out


def test_cli_assistant_error_rollback_and_edge_cases(tmp_path: Path):
    assistant = StarMindCLIAssistant(save_dir=tmp_path)
    assistant.handle_line("第一轮正常提问")
    assert len(assistant.memory.messages) == 2

    # 触发模拟后端故障：助手不应崩溃，且失败的 user 消息应被自动回滚
    keep_going, err_out = assistant.handle_line("请执行 __TRIGGER_ERROR__")
    assert keep_going is True
    assert "已自动回滚" in err_out
    assert len(assistant.memory.messages) == 2

    # 空输入与未知指令
    _, empty_out = assistant.handle_line("   ")
    assert "不能为空" in empty_out

    _, unknown_out = assistant.handle_line("/foobar")
    assert "未知指令" in unknown_out


def test_run_repl_end_to_end(tmp_path: Path):
    assistant = StarMindCLIAssistant(save_dir=tmp_path)
    outputs = assistant.run_repl(["/help", "我叫老陈", "报销怎么走？", "/exit"])
    assert len(outputs) == 4
    assert "/clear" in outputs[0]
    assert "老陈同学" in outputs[2]
    assert "再见" in outputs[3]
''',
        "gitlab_review_log": [
            {
                "reviewer": "老陈 (架构师)",
                "role": "Milestone 1 Final Review",
                "comment": "第一阶段毕业考核满分通过！记忆管理、指令路由、后端抽象三层边界清晰，异常回滚和 `/save` 防路径穿越这种生产细节都考虑到了，完全具备进入第二阶段 FastAPI 后端开发的功底！",
                "resolution": "Approved — Milestone 1 Passed!"
            },
            {
                "reviewer": "林产品 (PM)",
                "role": "Product Acceptance",
                "comment": "亲测多轮记忆、`/save` 导出 JSON、`/clear` 重置话题和 `/exit` 退出全部符合 PRD 验收标准，下周咱们就给它套上 Web 页面和数据库！",
                "resolution": "产品验收签字通过。"
            }
        ],
        "homeworks": [
            {
                "title": "基础巩固：为多轮对话增加 Markdown 导出器",
                "difficulty": "基础巩固",
                "requirement": "编写函数 `export_messages_to_markdown(messages: list[dict], title: str = '星辰智脑对话记录') -> str`，将 `messages` 列表渲染为清晰的 Markdown 文本（每条消息以 `### 用户` 或 `### 助手` 标题分段）。",
                "hint": "遍历 `messages`，用字典把 `'user'` 映射为 `'用户'`、`'assistant'` 映射为 `'助手'`，最后用 `'\\n\\n'.join(blocks)` 拼接。",
                "solution_code": r'''"""Day 14 课后题 1：多轮对话记录 Markdown 导出器。"""

from typing import Dict, List


def export_messages_to_markdown(
    messages: List[Dict[str, str]],
    title: str = "星辰智脑对话记录",
) -> str:
    """将标准 messages 列表导出为易读的 Markdown 纪要文本。"""
    role_map = {"user": "用户", "assistant": "星辰智脑", "system": "系统人设"}
    blocks = [f"# {title}"]
    for idx, msg in enumerate(messages, 1):
        role_label = role_map.get(msg.get("role", ""), msg.get("role", "未知"))
        blocks.append(f"### {idx}. {role_label}\n\n{msg.get('content', '').strip()}")
    return "\n\n".join(blocks)


if __name__ == "__main__":
    sample = [
        {"role": "user", "content": "星辰智脑有哪些指令？"},
        {"role": "assistant", "content": "支持 /help、/clear、/save、/stats 和 /exit。"},
    ]
    print(export_messages_to_markdown(sample))
''',
                "solution_analysis": "JSON 适合程序加载恢复，Markdown 适合直接粘贴到飞书/钉钉文档分享给同事，两者结合能极大提升 CLI 工具的实用性。"
            },
            {
                "title": "企业实战：本地多会话存档管理器",
                "difficulty": "企业实战",
                "requirement": "编写 `list_saved_sessions(save_dir: Path) -> list[dict]`，扫描目录下所有 `.json` 会话存档，返回按文件名排序的摘要列表，每项包含 `file_name`、`session_id`、`message_count`；若遇到损坏的 JSON 文件不崩溃，将其 `session_id` 标记为 `'CORRUPTED'`。",
                "hint": "用 `sorted(save_dir.glob('*.json'))` 遍历，配合 `try/except (json.JSONDecodeError, OSError)` 容错解析。",
                "solution_code": r'''"""Day 14 课后题 2：多会话 JSON 存档扫描与容错摘要器。"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List


def list_saved_sessions(save_dir: Path) -> List[Dict[str, Any]]:
    """扫描会话目录，返回所有 JSON 存档的摘要信息（损坏文件安全标记不崩溃）。"""
    if not save_dir.exists():
        return []
    summaries: List[Dict[str, Any]] = []
    for path in sorted(save_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            summaries.append({
                "file_name": path.name,
                "session_id": str(data.get("session_id", "unknown")),
                "message_count": len(data.get("messages", [])),
            })
        except (json.JSONDecodeError, OSError, TypeError):
            summaries.append({
                "file_name": path.name,
                "session_id": "CORRUPTED",
                "message_count": 0,
            })
    return summaries


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "s1.json").write_text(json.dumps({"session_id": "hr-qa", "messages": [{"role": "user", "content": "hi"}]}), encoding="utf-8")
        (root / "bad.json").write_text("{broken", encoding="utf-8")
        print(list_saved_sessions(root))
''',
                "solution_analysis": "目录扫描类功能一定要做单文件异常隔离：绝不能因为目录里混进一个半截损坏文件就导致整个 `/list` 列表功能崩溃。"
            },
            {
                "title": "架构进阶：基于 Token 预算的智能上下文裁剪器",
                "difficulty": "架构进阶",
                "requirement": "按条数裁剪有时不够精准（一条长日志就可能占几千字符）。编写 `trim_messages_by_budget(system_prompt: str, messages: list[dict], max_chars: int) -> list[dict]`，始终保留首条 `system` 消息，然后从最新消息往前倒序装入，直到总字符数即将超过 `max_chars` 为止，最终保持时间正序返回。",
                "hint": "先扣掉 `len(system_prompt)` 得到剩余预算，再用 `reversed(messages)` 倒序累加挑出能放下的最新消息，最后反转回来拼在 `system` 后面。",
                "solution_code": r'''"""Day 14 课后题 3：按字符/Token 预算倒序裁剪多轮上下文。"""

from typing import Dict, List


def trim_messages_by_budget(
    system_prompt: str,
    messages: List[Dict[str, str]],
    max_chars: int,
) -> List[Dict[str, str]]:
    """在严格不超过 max_chars 预算的前提下，保留 system 人设与尽可能多的新近消息。"""
    budget = max_chars - len(system_prompt)
    selected_rev: List[Dict[str, str]] = []

    for msg in reversed(messages):
        cost = len(msg.get("content", ""))
        if cost <= budget:
            selected_rev.append(msg)
            budget -= cost
        else:
            break

    selected_rev.reverse()
    return [{"role": "system", "content": system_prompt}, *selected_rev]


if __name__ == "__main__":
    history = [
        {"role": "user", "content": "这是一条很老很长的历史问题" * 3},
        {"role": "assistant", "content": "旧回复"},
        {"role": "user", "content": "最新问题"},
        {"role": "assistant", "content": "最新回复"},
    ]
    trimmed = trim_messages_by_budget("系统人设", history, max_chars=25)
    print(trimmed)
''',
                "solution_analysis": "倒序装包 + 反转还原是几乎所有主流 AI 框架（LangChain / LlamaIndex / OpenAI Agent）计算 Token 上下文窗口的底层标准算法！"
            }
        ],
        "extra_deep_dive": (
            "【第一阶段收官复盘：从 CLI 助手到生产级企业 AI 平台，还差哪几步？】\n"
            "今天咱们的 CLI 助手已经具备了完整的多轮大脑内核，但真要让全公司 500 名员工同时使用，还面临四个核心挑战：\n"
            "1）**多人并发访问** -> 第二阶段（Day 15~26）用 **FastAPI + SQLite/PostgreSQL** 把本地 JSON 换成并发安全的数据库与 HTTP API；\n"
            "2）**不懂公司私密文档** -> 第三阶段（Day 27~38）接入 **Embedding + 向量数据库 + RAG 检索增强**；\n"
            "3）**只会说不会干活** -> 第四阶段（Day 39~50）升级为 **Function Calling + ReAct + MCP 工具调用 Agent**；\n"
            "4）**上线观测与运维** -> 第五、六阶段接入 **流式 SSE 前端、评测集、Docker 容器化与线上监控**。\n"
            "第一阶段的地基你已经打得无比扎实，下一阶段见！"
        )
    },
])
