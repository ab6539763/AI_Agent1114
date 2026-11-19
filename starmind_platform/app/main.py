"""
星辰智脑 (StarMind Enterprise Agent Platform) FastAPI 应用主入口。

职责：
1. 应用生命周期管理（`lifespan`）：自动初始化 SQLite 数据库、销售业绩示例数据，并预置企业知识库样例文档。
2. 全局中间件：CORS 跨域放行、全链路 TraceID 注入与响应头 `X-Trace-ID` 回传。
3. 全局异常处理：将 `StarMindError` 子类统一映射为规范 JSON 错误响应并写入审计日志。
4. 前端静态页面挂载：访问 `/` 直接呈现中文企业级控制台界面。
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, List, Optional, Tuple

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from starmind_platform.app.api.routes import PlatformContainer, router
from starmind_platform.app.config import Settings, get_settings
from starmind_platform.app.core.exceptions import StarMindError
from starmind_platform.app.core.logging_utils import generate_trace_id, get_logger, trace_context

logger = get_logger("starmind.main")

WEB_INDEX_PATH = Path(__file__).resolve().parent / "web" / "index.html"

# 平台启动时自动预置的企业知识库样例文档，确保开箱即可体验真实溯源 RAG
SEED_KB_DOCUMENTS: List[Tuple[str, str, dict]] = [
    (
        "星辰数科差旅与费用报销规范.md",
        """# 杭州星辰数科差旅与费用报销规范（2026版）

1. 住宿标准：一线城市（北京、上海、深圳、广州）普通员工每晚不超过 650 元，杭州及其他新一线城市每晚不超过 500 元。
2. 交通标准：高铁优先预订二等座；连续飞行超过 4 小时或总监级以上人员可申请商务舱。
3. 餐补与市内交通：出差期间按每日 180 元包干发放伙食与市内交通补助，无需单独粘贴零星餐饮票据。
4. 审批权限：单笔报销金额小于 5000 元由直属主管在线审批；金额大于等于 5000 元须触发人工复核，依次经由部门总监与财务中心会签后打款。
5. 时效要求：差旅结束后 15 个工作日内须在 OA 报销系统提交电子发票，逾期跨季度原则上不予核销。
""",
        {"department": "财务中心", "category": "行政制度"},
    ),
    (
        "星辰数科考勤与带薪年休假制度.md",
        """# 杭州星辰数科考勤与带薪年休假制度

1. 弹性工作制：研发与产品中心实行核心工时制，上午 9:00-10:00 弹性打卡，满 8 小时工作制（不含午休 1.5 小时）。
2. 带薪年休假：入职满 1 年不满 10 年享有 7 天带薪年假；满 10 年不满 20 年享有 12 天；司龄每增加 1 年额外奖励 1 天星辰福利假，上限 15 天。
3. 请假审批：3 天以内年假或事假由直属主管审批；连续请假超过 3 天需抄送 HRBP 并由部门负责人审批。
4. 加班调休：周末或法定节假日经审批的紧急上线支持，可按 1:1 申请调休假，有效期为 6 个月。
""",
        {"department": "人力资源部", "category": "人事制度"},
    ),
    (
        "星辰智脑AI应用研发上线与安全合规手册.md",
        """# 星辰智脑 AI 应用研发上线与安全合规手册

1. 数据脱敏红线：严禁将客户明文手机号、18位身份证号、银行卡号及邮箱直接发送至公网大模型 API，必须经过平台安全护栏自动脱敏。
2. RAG 幻觉治理：所有面向内部员工与外部客户的知识库问答，必须标注 [文档名#片段ID] 溯源依据；当检索置信度低于阈值时，强制输出“知识库暂无相关依据，我不知道”。
3. Text-to-SQL 安全：Agent 访问业务数据库一律使用只读账号与白名单 SELECT 校验，严禁执行 DROP、DELETE、UPDATE、INSERT 及多语句分号注入。
4. 灰度发布与可观测性：新版本 Prompt 或 LoRA 微调权重上线前，须通过 Ragas 忠实度 >= 0.85 与安全红队测试，上线后持续监控 P95 延迟与单次调用人民币成本。
""",
        {"department": "AI平台工程部", "category": "研发规范"},
    ),
]


def _seed_knowledge_base(container: PlatformContainer) -> None:
    """当向量库为空时，自动灌入杭州星辰数科 3 份核心制度文档。"""
    if container.rag.vector_store.chunks:
        return
    for doc_name, content, meta in SEED_KB_DOCUMENTS:
        container.rag.ingest_document(
            doc_name=doc_name,
            content=content,
            doc_format="md",
            metadata=meta,
        )
    logger.info(
        f"已自动预置企业知识库样例文档 {len(SEED_KB_DOCUMENTS)} 份，"
        f"共生成 {len(container.rag.vector_store.chunks)} 个向量片段。"
    )


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    """FastAPI 应用工厂函数（便于生产部署与 pytest 隔离测试）。"""
    cfg = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        container = PlatformContainer(cfg)
        _seed_knowledge_base(container)
        application.state.container = container
        logger.info(
            f"星辰智脑平台启动完成 | provider={container.llm.provider} | model={container.llm.model}"
        )
        yield
        logger.info("星辰智脑平台正在优雅关闭...")

    application = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        description="杭州星辰数科企业级大模型应用与 Agent 编排平台（RAG / ReAct / StateGraph / Multi-Agent / Text-to-SQL / MCP / Fine-tune）",
        lifespan=lifespan,
    )

    # 1. CORS 跨域配置
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. 全链路 TraceID 中间件
    @application.middleware("http")
    async def trace_id_middleware(request: Request, call_next):
        incoming_tid = request.headers.get("X-Trace-ID") or generate_trace_id()
        with trace_context(incoming_tid) as tid:
            response = await call_next(request)
            response.headers["X-Trace-ID"] = tid
            return response

    # 3. 统一业务异常处理（捕获 StarMindError 并记录安全审计日志）
    @application.exception_handler(StarMindError)
    async def starmind_error_handler(request: Request, exc: StarMindError) -> JSONResponse:
        container: Optional[PlatformContainer] = getattr(request.app.state, "container", None)
        if container is not None:
            try:
                container.db.record_audit(
                    action=f"error.{exc.error_code}",
                    status="blocked" if exc.http_status == 400 else "error",
                    detail=exc.message,
                )
            except Exception:
                pass
        body = exc.to_dict()
        body["trace_id"] = request.headers.get("X-Trace-ID") or generate_trace_id()
        return JSONResponse(status_code=exc.http_status, content=body)

    # 4. 挂载 API 路由
    application.include_router(router)

    # 5. 挂载企业级中文 Web 控制台首页
    @application.get("/", response_class=HTMLResponse, include_in_schema=False)
    def serve_console() -> HTMLResponse:
        if WEB_INDEX_PATH.exists():
            return HTMLResponse(content=WEB_INDEX_PATH.read_text(encoding="utf-8"))
        return HTMLResponse(
            content="<h1>星辰智脑 StarMind Enterprise Agent Platform</h1><p>API 文档请访问 <a href='/docs'>/docs</a></p>"
        )

    return application


# Uvicorn 默认启动对象：uvicorn starmind_platform.app.main:app
app = create_app()
