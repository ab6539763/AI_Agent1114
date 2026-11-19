"""
Day 64 课后作业 2（企业实战）：企业实战：生成带 SHA-256 校验和的发布产物清单
工单：STARMIND-064
"""

import hashlib


def build_checksum_manifest(files: dict[str, str]) -> dict[str, str]:
    return {name: hashlib.sha256(body.encode("utf-8")).hexdigest() for name, body in files.items()}


m = build_checksum_manifest({"Dockerfile": "FROM python:3.11-slim"})
assert len(m["Dockerfile"]) == 64
print("发布产物 SHA-256 清单生成通过:", m)

