# STARMIND-056 · Day 56 需求文档与 GitLab 迭代记录

| 字段 | 内容 |
|------|------|
| **迭代天数** | Day 56 / 70 |
| **所属阶段** | 第 5 阶段：第五阶段：模型微调与部署（第 8 周：模型微调、本地推理部署与安全合规） |
| **需求标题** | AI 应用容器化部署工程化与运维巡检 —— 多阶段 Dockerfile、Docker Compose 编排、Nginx SSE 反向代理与健康检查巡检 |
| **GitLab 分支** | `feat/day56-docker-nginx-ops` |
| **Commit 规范** | `feat(day56): 实现部署配置生成器与容器健康巡检引擎` |
| **配套课件** | `courseware/day56/index.html` |
| **配套 Notebook** | `notebooks/day56/day56_practice.ipynb` |
| **迭代快照** | `versions/day56/` |

## 1. 上下文衔接

- **承上（昨日基线）**：昨天我们打通了 Ollama/vLLM 统一 OpenAI 推理协议，并手写了 TTFT/TPS 异步压测器验证了并发吞吐。
- **启下（明日演进）**：明天（Day 57）是第五阶段周测 + 安全与合规专题：内容审核、敏感信息脱敏、国内大模型网信办备案常识，以及 Token 成本实时监控与熔断。

## 2. 业务需求说明 (PRD)

### 业务背景
星辰智脑即将部署至杭州阿里云 ECS 生产环境，需将 FastAPI 后端、前端控制台、Redis 缓存与上游推理服务统一容器化编排，并通过 Nginx 暴露 HTTPS/SSE 入口，同时配备上线后自动化巡检探针。

### 核心痛点
- 传统单阶段镜像体积大、包含编译工具链且以 root 运行，无法通过企业容器安全扫描。
- Nginx 默认缓冲代理响应，导致大模型 SSE 打字机流式接口卡死甚至 504 超时。
- 缺少标准化 `/healthz`、`/readyz` 探针与一键巡检脚本，出故障时排查耗时。

### 迭代目标
- 实现部署配置生成与安全审计器：自动生成多阶段瘦身 Dockerfile、Docker Compose 编排文件与支持 SSE 流式无缓冲的 Nginx 配置，并校验关键安全与超时配置。
- 实现生产运维健康巡检引擎：并发检测多服务探针状态、响应延迟、磁盘/内存水位并输出红黄绿巡检报告。

### 验收标准
- [x] 生成的 Dockerfile 包含多阶段 `AS builder`、非 root 用户切换 `USER appuser` 与 `HEALTHCHECK` 指令。
- [x] 生成的 Nginx 配置包含 `proxy_buffering off`、`proxy_cache off`、`proxy_read_timeout 300s` 及 HTTP/1.1 长连接配置。
- [x] 运维巡检器准确识别健康、降级、宕机三种状态并返回标准退出码。

### 非功能指标
- 纯 Python 离线可验证全部生成资产的语法与安全合规项。

## 3. 架构设计与交付清单

企业级 AI 应用部署架构的核心是 **分层解耦 + 不可变基础设施 + 流式友好网关**：

1. **Nginx 边缘网关层（SSE 专项优化）**：
   大模型对话普遍耗时 10~60 秒且采用 Server-Sent Events（`text/event-stream`）逐字推送。普通 Web 配置下的 Nginx 会把后端响应攒满 4KB 缓冲再发，导致前端完全失去打字机体验；必须在 `/api/v1/chat/stream` 路由下显式声明 `proxy_buffering off;`、`chunked_transfer_encoding on;`、`proxy_http_version 1.1;`、`proxy_set_header Connection '';` 以及 `proxy_read_timeout 300s;`。

2. **多阶段 Docker 镜像（Multi-Stage Build）**：
   第一阶段（builder）安装 gcc 等编译依赖并把 Python 依赖打进独立虚拟环境 `/opt/venv`；第二阶段基于 `python:3.11-slim` 仅拷贝 `/opt/venv` 与应用源码，创建普通用户 `starmind` 运行 `uvicorn`，镜像体积直降 60% 且杜绝容器提权风险。

3. **双探针与运维巡检（Liveness vs Readiness）**：
   - `/healthz`（存活探针）：仅检查进程是否活着，不查下游数据库，避免数据库抖动引发容器雪崩重启。
   - `/readyz`（就绪探针）：检查 SQLite/PostgreSQL、Redis、推理网关是否全部连通，就绪后 Nginx/K8s 才切入流量。

### 当日交付代码文件
- `src/day56_deploy_generator.py`：步骤一：实现多阶段 Dockerfile / Compose / SSE Nginx 生成与安全审计器
- `src/day56_ops_inspector.py`：步骤二：实现生产级运维健康巡检与分级告警引擎

## 4. GitLab Merge Request Code Review 记录

### Reviewer：老陈（Approved）
用纯 Python `urllib.request` 写 `HEALTHCHECK` 比在 slim 镜像里额外 `apt-get install curl` 干净多了，少装一个包就少一分攻击面和镜像体积。

### Reviewer：阿杰（Approved）
运维巡检器的 0/1/2 退出码规范我直接接进咱们 GitLab CI 部署后的 smoke-test 阶段了，只要返回 2 自动触发回滚！

