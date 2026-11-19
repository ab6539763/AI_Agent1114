"""
Day 56 - 模块一：容器化部署资产生成器（Dockerfile / Compose / Nginx SSE）与安全审计器
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class DeploySpec:
    """部署环境规格"""
    app_name: str = "starmind-api"
    app_port: int = 8000
    nginx_port: int = 80
    workers: int = 2
    pip_mirror: str = "https://pypi.tuna.tsinghua.edu.cn/simple"


def render_multistage_dockerfile(spec: DeploySpec) -> str:
    """生成多阶段瘦身、非 root、带健康检查的生产级 Dockerfile"""
    return f"""# Stage 1: 构建依赖虚拟环境
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv \\
    && /opt/venv/bin/pip install --no-cache-dir -i {spec.pip_mirror} -r requirements.txt

# Stage 2: 极简安全运行时
FROM python:3.11-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd -m -u 10001 starmind
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=starmind:starmind . /app
USER starmind
EXPOSE {spec.app_port}
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \\
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:{spec.app_port}/healthz', timeout=3)" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{spec.app_port}", "--workers", "{spec.workers}"]
"""


def render_sse_nginx_conf(spec: DeploySpec) -> str:
    """生成针对大模型 SSE 流式输出优化的 Nginx 反向代理配置"""
    return f"""server {{
    listen {spec.nginx_port};
    server_name _;

    client_max_body_size 50M;

    location /api/ {{
        proxy_pass http://{spec.app_name}:{spec.app_port};
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Connection '';
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding on;
        proxy_read_timeout 300s;
    }}

    location /healthz {{
        proxy_pass http://{spec.app_name}:{spec.app_port}/healthz;
    }}
}}
"""


def audit_deploy_assets(dockerfile: str, nginx_conf: str) -> List[str]:
    """审计 Dockerfile 与 Nginx 配置，返回缺失的安全/性能红线项列表"""
    issues: List[str] = []
    if "AS builder" not in dockerfile:
        issues.append("Dockerfile 未使用多阶段构建(AS builder)，镜像体积将偏大")
    if "USER " not in dockerfile or "USER root" in dockerfile:
        issues.append("Dockerfile 未切换非 root 运行用户，存在容器提权风险")
    if "HEALTHCHECK" not in dockerfile:
        issues.append("Dockerfile 缺少 HEALTHCHECK 探针配置")
    if "proxy_buffering off;" not in nginx_conf:
        issues.append("Nginx 未关闭 proxy_buffering，将导致大模型 SSE 流式输出卡顿")
    if "proxy_read_timeout" not in nginx_conf:
        issues.append("Nginx 未设置长读超时，长文本生成易触发 504 Gateway Timeout")
    return issues


if __name__ == "__main__":
    spec = DeploySpec()
    df = render_multistage_dockerfile(spec)
    ngx = render_sse_nginx_conf(spec)
    problems = audit_deploy_assets(df, ngx)
    print(f"部署配置安全审计完成，发现问题数: {len(problems)}")

