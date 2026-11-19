"""
Day 64 - 模块一：星辰智脑容器化部署清单生成器、合规审计器与 Runbook 交付文档
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ReleaseBundle:
    version: str
    dockerfile: str
    compose_yml: str
    nginx_conf: str
    runbook_md: str


def generate_release_bundle(version: str = "1.0.0") -> ReleaseBundle:
    dockerfile = (
        "FROM python:3.11-slim AS builder\n"
        "WORKDIR /build\n"
        "RUN python -m venv /opt/venv\n"
        "ENV PATH=\"/opt/venv/bin:$PATH\"\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n\n"
        "FROM python:3.11-slim AS runtime\n"
        "RUN useradd -m -u 1000 starmind\n"
        "WORKDIR /app\n"
        "COPY --from=builder /opt/venv /opt/venv\n"
        "COPY src/ ./src/\n"
        "ENV PATH=\"/opt/venv/bin:$PATH\"\n"
        "USER starmind\n"
        "EXPOSE 8000\n"
        "HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')\"\n"
        "CMD [\"uvicorn\", \"src.day62_api_server:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
    )

    compose_yml = (
        "services:\n"
        "  starmind-api:\n"
        f"    image: starmind-api:{version}\n"
        "    restart: unless-stopped\n"
        "    env_file: .env\n"
        "    ports:\n"
        "      - \"127.0.0.1:8000:8000\"\n"
        "    logging:\n"
        "      driver: json-file\n"
        "      options:\n"
        "        max-size: \"50m\"\n"
        "        max-file: \"5\"\n"
        "  nginx:\n"
        "    image: nginx:1.25-alpine\n"
        "    depends_on:\n"
        "      starmind-api:\n"
        "        condition: service_healthy\n"
        "    ports:\n"
        "      - \"443:443\"\n"
    )

    nginx_conf = (
        "location /api/v1/chat/stream {\n"
        "    proxy_pass http://starmind-api:8000;\n"
        "    proxy_http_version 1.1;\n"
        "    proxy_set_header Connection '';\n"
        "    proxy_buffering off;\n"
        "    proxy_cache off;\n"
        "    proxy_read_timeout 300s;\n"
        "}\n"
    )

    runbook_md = (
        f"# 星辰智脑 (StarMind) v{version} 生产交付运维手册 (Runbook)\n\n"
        "## 1. 一键部署命令\n"
        "```bash\n"
        f"docker compose up -d --build\n"
        "```\n\n"
        "## 2. 健康检查探针\n"
        "- 存活探针: `GET /healthz`\n"
        "- 就绪探针: `GET /readyz`\n\n"
        "## 3. 应急回滚命令\n"
        "```bash\n"
        "STARMIND_VERSION=0.9.9 docker compose up -d --no-build starmind-api\n"
        "```\n"
    )
    return ReleaseBundle(version, dockerfile, compose_yml, nginx_conf, runbook_md)


def audit_release_bundle(bundle: ReleaseBundle) -> Dict[str, List[str]]:
    """对部署交付物执行自动化安全与流式合规审计"""
    issues: List[str] = []
    if "AS builder" not in bundle.dockerfile or "USER starmind" not in bundle.dockerfile:
        issues.append("Dockerfile 必须采用多阶段构建并切换非 root 用户")
    if "HEALTHCHECK" not in bundle.dockerfile:
        issues.append("Dockerfile 缺少 HEALTHCHECK 指令")
    if ":latest" in bundle.compose_yml:
        issues.append("Docker Compose 严禁使用 :latest 镜像标签")
    if "max-size" not in bundle.compose_yml:
        issues.append("Docker Compose 缺少日志大小轮转限制")
    if "proxy_buffering off;" not in bundle.nginx_conf or "proxy_read_timeout 300s;" not in bundle.nginx_conf:
        issues.append("Nginx SSE 路由必须关闭 proxy_buffering 并配置长超时")
    if "应急回滚" not in bundle.runbook_md:
        issues.append("Runbook 交付文档缺少应急回滚预案")
    return {"passed": len(issues) == 0, "issues": issues}


if __name__ == "__main__":
    bundle = generate_release_bundle("1.0.0")
    print("部署合规审计:", audit_release_bundle(bundle))
    print("Runbook 预览:\n", bundle.runbook_md)

