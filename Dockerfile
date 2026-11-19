# 星辰智脑 (StarMind) 企业级 Agent 平台生产级多阶段 Dockerfile
# 构建命令: docker build -t starmind-agent-platform:v1.0.0 .

FROM python:3.11-slim AS builder

WORKDIR /build

# 配置国内清华源加速构建
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

FROM python:3.11-slim AS runtime

LABEL maintainer="AI Platform Engineering Team <ai-eng@xingchen-tech.cn>"
LABEL version="1.0.0"
LABEL description="StarMind Enterprise Agent Platform"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STARMIND_ENV=production \
    STARMIND_HOST=0.0.0.0 \
    STARMIND_PORT=8000 \
    STARMIND_DB_PATH=/app/data/starmind.db

# 创建非 root 安全运行用户
RUN groupadd -r starmind && useradd -r -g starmind starmind \
    && mkdir -p /app/data /app/logs \
    && chown -R starmind:starmind /app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY starmind_platform/ /app/starmind_platform/

USER starmind

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')" || exit 1

CMD ["uvicorn", "starmind_platform.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
