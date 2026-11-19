"""
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

