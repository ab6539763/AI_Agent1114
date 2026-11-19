"""
Day 47 课后作业 3（架构进阶）：为 Coding Agent 增加统一补丁应用前的语法预检
工单：STARMIND-047
"""

"""Day 47 作业 3 参考答案：Coding Agent AST 语法预检器。"""

import ast
from typing import Tuple


def verify_python_syntax(code_str: str) -> Tuple[bool, str]:
    try:
        ast.parse(code_str)
        return True, "OK"
    except SyntaxError as exc:
        return False, f"第 {exc.lineno} 行语法错误: {exc.msg}"


if __name__ == "__main__":
    assert verify_python_syntax("x = 1 + 2")[0] is True
    ok, msg = verify_python_syntax("def broken(:\n    pass")
    print("语法拦截:", ok, msg)
    assert ok is False

