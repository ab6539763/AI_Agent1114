"""
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

