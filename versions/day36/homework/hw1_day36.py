"""
Day 36 课后作业 1（基础巩固）：作业一：为多格式解析器增加「YAML 配置文件」格式支持
工单：STARMIND-036
"""

"""Day 36 作业一参考答案：YAML 键值配置文档解析器"""
from typing import List


def parse_simple_yaml_kv(text: str) -> List[str]:
    chunks: List[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        chunks.append(f"配置项 {k.strip()} 的标准值为 {v.strip()}")
    return chunks


if __name__ == "__main__":
    yml = "# 网关配置\nproxy_read_timeout: 30s\nmax_retries: 3\n"
    out = parse_simple_yaml_kv(yml)
    print(out)
    assert len(out) == 2 and "30s" in out[0]

