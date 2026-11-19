"""
Day 30 - 步骤二：星辰数科企业知识库命令行问答工具（CLI）
支持加载企业全量示范制度语料、按部门过滤检索、格式化输出答案与引用溯源卡片。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.day28_loaders import Document, MarkdownLoader
from src.day30_rag_pipeline import EnterpriseRAGPipeline, RAGResponse


STARMIND_CORPUS = [
    (
        "财务报销制度_2026.md",
        "财务部",
        """# 差旅住宿标准
员工因公出差须提前在OA审批。一线城市（北京、上海、深圳、广州）酒店住宿上限每晚600元；新一线城市（杭州、南京、成都）上限每晚480元。
# 餐饮与交通补助
出差期间餐饮补助按每天100元定额随工资发放，无需提供餐饮发票。市内交通实报实销，单次打车超过150元需备注事由。""",
    ),
    (
        "HR员工休假手册_2026.md",
        "HR",
        """# 年假规定
员工在星辰数科连续工作满1年不满10年的，每年享受5天带薪年假；满10年享受10天带薪年假。年假须提前3个工作日提交OA申请。
# 病假与证明
员工申请病假超过1天的，须提供二级及以上公立医院出具的诊断证明与病假条，病假期间按基本工资的80%发放。""",
    ),
    (
        "研发工程规范_v3.md",
        "研发部",
        """# 代码评审与合并
所有业务代码合并至 main 分支前，必须在 GitLab 发起 Merge Request，至少经过1位架构师或高级工程师 Review 通过，且 CI 单元测试通过率须为100%。
# 生产发布窗口
日常生产发布窗口为每周一至周四 10:00-16:00，严禁在周五17:00之后及法定节假日前夕执行非紧急变更发布。""",
    ),
    (
        "IT信息安全指南.md",
        "IT运维",
        """# VPN与内网接入
远程办公访问内网 GitLab 与测试环境必须开启星辰零信任 VPN 客户端，证书每90天自动轮换一次；如遇无法连接，请先在企业微信重置动态令牌。
# 数据脱敏红线
严禁将客户明文手机号、身份证号、银行卡号直接发送给外部公有云大模型 API，所有测试日志须先经脱敏网关处理。""",
    ),
]


def build_starmind_kb(persist_dir: Optional[str | Path] = None) -> EnterpriseRAGPipeline:
    """加载星辰数科内置四部门语料，返回可直接提问的 RAG 引擎。"""
    from src.day29_vector_store import StarMindVectorStore

    store = StarMindVectorStore(collection_name="starmind_enterprise_kb", persist_directory=persist_dir)
    pipeline = EnterpriseRAGPipeline(vector_store=store, chunk_size=180, chunk_overlap=25, score_threshold=0.22)
    if store.count() == 0:
        loader = MarkdownLoader()
        all_docs: List[Document] = []
        for filename, dept, md_text in STARMIND_CORPUS:
            parsed = loader.load_text(md_text, source=filename)
            for d in parsed:
                d.metadata["dept"] = dept
            all_docs.extend(parsed)
        pipeline.ingest_documents(all_docs)
    return pipeline


def format_cli_response(resp: RAGResponse) -> str:
    """将 RAGResponse 格式化为清晰的终端问答卡片。"""
    lines = [
        "=" * 64,
        f"【员工提问】{resp.question}",
        f"【状态】{'兜底拒答 (Fallback)' if resp.is_fallback else '知识库命中'} | 耗时: {resp.latency_ms} ms",
        "-" * 64,
        resp.answer,
    ]
    if resp.citations:
        lines.append("-" * 64)
        lines.append("【引用溯源】")
        for c in resp.citations:
            lines.append(f"  [{c.ref_id}] {c.source} > {c.section} (相似度: {c.score:.3f})")
    lines.append("=" * 64)
    return "\n".join(lines)


def run_demo_queries() -> List[RAGResponse]:
    """运行一组涵盖命中、部门过滤与库外拒答的演示提问。"""
    kb = build_starmind_kb()
    test_cases = [
        ("入职满1年有几天年假？需要提前多久申请？", None),
        ("周五晚上6点可以发版上线吗？", {"dept": "研发部"}),
        ("远程办公连不上内网GitLab怎么办？", None),
        ("请问公司食堂明天中午红烧肉多少钱一份？", None),
    ]
    results: List[RAGResponse] = []
    for q, where in test_cases:
        resp = kb.ask(q, where=where)
        print(format_cli_response(resp))
        results.append(resp)
    return results


if __name__ == "__main__":
    run_demo_queries()

