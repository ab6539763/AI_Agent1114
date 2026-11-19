"""
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

