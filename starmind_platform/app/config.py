"""
配置中心模块 (基于 pydantic-settings)。

设计说明：
1. 遵循 12-Factor App 规范，支持通过环境变量或 `.env` 文件覆盖所有运行参数。
2. 支持多种大模型后端无缝切换：
   - `local_mock`（默认）：内置智能本地推理引擎，无需外网 API Key 即可 100% 流畅体验全部企业级能力。
   - `deepseek`：深度求索 DeepSeek-V3 / DeepSeek-R1 官方 OpenAI 兼容接口。
   - `qwen`：阿里云百炼 / 通义千问 Qwen-Max / Qwen-Plus OpenAI 兼容接口。
   - `openai`：OpenAI GPT-4o / GPT-4o-mini 接口。
   - `ollama`：本地私有化部署 Ollama 服务。
   - `vllm`：企业内网 GPU 集群 vLLM 高并发推理服务。
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 支持的模型供应商枚举类型
LLMProviderType = Literal["local_mock", "deepseek", "qwen", "openai", "ollama", "vllm"]

# 项目根目录与数据目录默认路径
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    """星辰智脑企业级 Agent 平台全局配置项。"""

    model_config = SettingsConfigDict(
        env_prefix="STARMIND_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---------------- 应用基础配置 ----------------
    app_name: str = Field(default="星辰智脑 StarMind Enterprise Agent Platform", description="平台中文全称")
    app_version: str = Field(default="1.0.0", description="平台语义化版本号")
    env: Literal["dev", "staging", "prod", "test"] = Field(default="dev", description="当前运行环境")
    debug: bool = Field(default=False, description="是否开启调试模式")
    log_level: str = Field(default="INFO", description="全局日志级别")

    # ---------------- 大模型后端配置 ----------------
    llm_provider: LLMProviderType = Field(
        default="local_mock",
        description="默认模型供应商（默认 local_mock，无外网 Key 亦可完整运行）",
    )
    llm_model: str = Field(
        default="deepseek-chat",
        description="默认调用的模型标识，例如 deepseek-chat / qwen-max / gpt-4o",
    )
    llm_api_key: str = Field(default="", description="外部大模型 API Key（local_mock 模式可留空）")
    llm_base_url: str = Field(
        default="",
        description="自定义 OpenAI 兼容接口 Base URL（为空时自动按 provider 补全默认地址）",
    )
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0, description="生成温度，企业场景默认偏严谨")
    llm_max_tokens: int = Field(default=2048, ge=64, le=32768, description="单次响应最大输出 Token 数")
    llm_timeout_seconds: float = Field(default=30.0, gt=0.0, description="大模型 HTTP 请求超时时间（秒）")
    llm_max_retries: int = Field(default=3, ge=0, le=10, description="大模型瞬时故障自动重试次数")

    # ---------------- 数据库与持久化配置 ----------------
    data_dir: str = Field(default=str(DEFAULT_DATA_DIR), description="平台本地数据与索引持久化目录")
    database_url: str = Field(
        default=f"sqlite:///{DEFAULT_DATA_DIR / 'starmind.db'}",
        description="SQLAlchemy 数据库连接串（默认使用 SQLite 零配置部署）",
    )
    vector_store_path: str = Field(
        default=str(DEFAULT_DATA_DIR / "vector_store.json"),
        description="轻量本地向量库持久化 JSON 文件路径",
    )

    # ---------------- RAG 检索增强配置 ----------------
    rag_chunk_size: int = Field(default=320, ge=64, le=4096, description="文档切片目标字符长度")
    rag_chunk_overlap: int = Field(default=60, ge=0, le=512, description="相邻文档切片重叠字符数")
    rag_top_k: int = Field(default=4, ge=1, le=20, description="最终送入大模型的参考片段数")
    rag_min_confidence: float = Field(
        default=0.12,
        ge=0.0,
        le=1.0,
        description="RAG 相关性最低置信度阈值，低于该值触发“知识库暂无相关依据”兜底拒答",
    )

    # ---------------- Agent 编排与安全配置 ----------------
    agent_max_steps: int = Field(default=6, ge=1, le=20, description="ReAct Agent 最大推理步数，防止死循环")
    enable_guardrails: bool = Field(default=True, description="是否全局启用企业级安全护栏与敏感信息脱敏")
    enable_pii_masking: bool = Field(default=True, description="是否启用手机号/身份证/银行卡/邮箱脱敏")

    def resolve_base_url(self) -> str:
        """
        根据当前 `llm_provider` 解析最终生效的 OpenAI 兼容 API Base URL。
        若用户显式设置了 `llm_base_url`，则以用户配置为准。
        """
        if self.llm_base_url.strip():
            return self.llm_base_url.rstrip("/")

        default_urls = {
            "deepseek": "https://api.deepseek.com/v1",
            "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "openai": "https://api.openai.com/v1",
            "ollama": "http://127.0.0.1:11434/v1",
            "vllm": "http://127.0.0.1:8001/v1",
            "local_mock": "local://mock",
        }
        return default_urls.get(self.llm_provider, "local://mock")

    def ensure_data_dir(self) -> Path:
        """确保数据持久化目录存在，不存在时自动创建。"""
        path = Path(self.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取全局单例配置对象（支持测试时通过 cache_clear 刷新）。"""
    settings = Settings()
    settings.ensure_data_dir()
    return settings
