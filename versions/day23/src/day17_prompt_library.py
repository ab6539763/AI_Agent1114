"""
StarMind Day 17 - 步骤一：星辰智脑 10 大企业场景 Prompt 模板库
支持四要素装配、XML 安全分隔符转义、Zero/One/Few-shot 模式切换与 JSON 契约声明。
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class PromptTemplateSpec:
    """企业级结构化 Prompt 模板规范。"""
    scene_id: str
    scene_name: str
    role: str
    task: str
    required_json_keys: Tuple[str, ...]
    examples: Tuple[Tuple[str, Dict[str, object]], ...]
    max_reply_chars: int = 400


def sanitize_xml_payload(text: str, tag: str = "user_input") -> str:
    """对用户输入中可能出现的同名 XML 闭合标签进行转义，防止边界逃逸。"""
    return (
        text.replace(f"<{tag}>", f"&lt;{tag}&gt;")
        .replace(f"</{tag}>", f"&lt;/{tag}&gt;")
    )


class StarMindPromptLibrary:
    """星辰智脑 10 场景企业级 Prompt 资产库。"""

    def __init__(self) -> None:
        self._templates: Dict[str, PromptTemplateSpec] = {
            spec.scene_id: spec for spec in self._build_builtin_specs()
        }

    @staticmethod
    def _build_builtin_specs() -> List[PromptTemplateSpec]:
        return [
            PromptTemplateSpec(
                scene_id="customer_qa",
                scene_name="智能客服问答",
                role="杭州星辰数科资深客户服务专家",
                task="根据客户问题给出准确、礼貌的答复，并标注是否需要转人工。",
                required_json_keys=("answer", "need_human", "category"),
                examples=(
                    ("怎么开增值税专票？", {"answer": "请进入控制台-费用中心-发票管理提交专票抬头。", "need_human": False, "category": "billing"}),
                    ("你们系统崩了导致我损失十万！", {"answer": "非常抱歉带来不便，已为您紧急升级至专属客户经理跟进。", "need_human": True, "category": "complaint"}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="ticket_triage",
                scene_name="IT 工单分级分类",
                role="企业 IT 运维值班主管",
                task="判断故障工单的所属模块、优先级（P0/P1/P2）与首步排查建议。",
                required_json_keys=("module", "priority", "first_action"),
                examples=(
                    ("核心支付网关全部 502 超时", {"module": "payment_gateway", "priority": "P0", "first_action": "立即检查网关集群健康检查与熔断日志"}),
                    ("申请开通测试环境只读账号", {"module": "iam", "priority": "P2", "first_action": "核对直属主管审批单后在 IAM 平台开通"}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="weekly_report",
                scene_name="研发周报提炼",
                role="互联网研发效能 PMO",
                task="将零散流水账提炼为本周核心产出、风险项与下周计划。",
                required_json_keys=("highlights", "risks", "next_week"),
                examples=(
                    ("修完3个登录Bug，联调支付接口卡在第三方沙箱", {"highlights": ["修复登录模块3个缺陷"], "risks": ["第三方支付沙箱联调阻塞"], "next_week": ["推动联调并提测"]}),
                    ("完成RAG检索压测，QPS提升40%", {"highlights": ["RAG检索吞吐提升40%"], "risks": [], "next_week": ["灰度发布至生产环境"]}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="text_to_sql",
                scene_name="自然语言转 SQL",
                role="资深数据分析师与 PostgreSQL 专家",
                task="仅生成只读 SELECT 查询语句，严禁包含 DELETE/UPDATE/DROP，并说明查询逻辑。",
                required_json_keys=("sql", "read_only", "explanation"),
                examples=(
                    ("统计本月各部门有效订单总额", {"sql": "SELECT dept, SUM(amount) AS total FROM orders WHERE status='paid' GROUP BY dept;", "read_only": True, "explanation": "按部门汇总已支付订单金额"}),
                    ("查询最近7天新增注册用户数", {"sql": "SELECT COUNT(*) AS cnt FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';", "read_only": True, "explanation": "统计近7日新注册用户"}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="contract_review",
                scene_name="商业合同条款审查",
                role="国内企业 SaaS 法务合规顾问",
                task="识别合同片段中的法律与财务风险点，给出风险等级（low/medium/high）及修改建议。",
                required_json_keys=("risk_level", "risk_points", "suggestion"),
                examples=(
                    ("乙方需对任何间接损失承担无限连带赔偿责任。", {"risk_level": "high", "risk_points": ["无限连带赔偿条款风险极高"], "suggestion": "将赔偿上限约定为本合同总金额的100%"}),
                    ("双方应在验收通过后15个工作日内结算尾款。", {"risk_level": "low", "risk_points": [], "suggestion": "条款清晰合理，可保留"}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="email_polish",
                scene_name="商务邮件润色",
                role="企业高管商务沟通顾问",
                task="将口语化草稿改写为得体、简洁的商务邮件，包含标题与正文。",
                required_json_keys=("subject", "body", "tone"),
                examples=(
                    ("王总，明天的会改到下午三点，别忘了。", {"subject": "会议时间调整通知：明日项目评审改至 15:00", "body": "王总您好，原定明日的项目评审会议调整至下午 15:00，烦请知悉并预留时间。", "tone": "formal"}),
                    ("资料发你了，快点看。", {"subject": "项目参考资料发送，请查收", "body": "您好，相关项目资料已随附件发送，期待您的宝贵反馈。", "tone": "polite"}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="meeting_minutes",
                scene_name="会议纪要行动项抽取",
                role="敏捷项目经理",
                task="从会议记录中抽取决策结论和带责任人的待办事项列表。",
                required_json_keys=("decisions", "action_items"),
                examples=(
                    ("大家一致同意周五发版，阿杰负责压测，林产品整理上线清单。", {"decisions": ["确定本周五执行版本发布"], "action_items": [{"owner": "阿杰", "task": "完成发版前压测"}, {"owner": "林产品", "task": "整理上线清单"}]}),
                    ("决定先用DeepSeek-V3做客服试点，老陈周三前给出成本评估。", {"decisions": ["客服场景试点接入DeepSeek-V3"], "action_items": [{"owner": "老陈", "task": "周三前提交成本评估"}]}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="code_review",
                scene_name="Python 代码安全评审",
                role="Python 首席架构师",
                task="检查代码片段中的安全漏洞或性能问题，输出严重程度与修复方案。",
                required_json_keys=("severity", "issue", "fix"),
                examples=(
                    ("cursor.execute(f'SELECT * FROM users WHERE name={u}')", {"severity": "critical", "issue": "存在 SQL 注入漏洞", "fix": "改用参数化查询 cursor.execute('... WHERE name=%s', (u,))"}),
                    ("data = eval(user_input)", {"severity": "critical", "issue": "使用 eval 执行不可信输入存在任意代码执行风险", "fix": "改用 ast.literal_eval 或 json.loads"}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="sentiment_analysis",
                scene_name="品牌舆情情感分析",
                role="舆情洞察分析师",
                task="判断用户评论的情感极性（positive/neutral/negative）并提取核心关键词。",
                required_json_keys=("sentiment", "keywords", "confidence"),
                examples=(
                    ("星辰智脑响应速度真快，帮我省了半天写周报的时间！", {"sentiment": "positive", "keywords": ["响应速度快", "省时间"], "confidence": 0.96}),
                    ("导出 PDF 偶尔会乱码，希望尽快修一下。", {"sentiment": "negative", "keywords": ["导出PDF", "乱码"], "confidence": 0.91}),
                ),
            ),
            PromptTemplateSpec(
                scene_id="interview_eval",
                scene_name="技术面试记录评估",
                role="资深研发面试官",
                task="根据面试官笔记总结候选人优势、待提升点及录用建议（hire/hold/no_hire）。",
                required_json_keys=("strengths", "gaps", "recommendation"),
                examples=(
                    ("Python底层扎实，项目架构清晰，但对K8s排障经验较少。", {"strengths": ["Python基础扎实", "架构思维清晰"], "gaps": ["K8s生产排障经验偏少"], "recommendation": "hire"}),
                    ("连HTTP状态码和基本SQL联表都答不上来。", {"strengths": [], "gaps": ["计算机与数据库基础薄弱"], "recommendation": "no_hire"}),
                ),
            ),
        ]

    def list_scenes(self) -> List[str]:
        """返回全部已注册的场景 ID 列表。"""
        return list(self._templates.keys())

    def get_spec(self, scene_id: str) -> PromptTemplateSpec:
        if scene_id not in self._templates:
            raise KeyError(f"未知场景 ID: {scene_id}")
        return self._templates[scene_id]

    def render(self, scene_id: str, user_text: str, shot_mode: str = "few") -> str:
        """
        渲染完整结构化 Prompt：
        - shot_mode 支持 "zero" (0例) / "one" (1例) / "few" (全部示例)
        """
        spec = self.get_spec(scene_id)
        if shot_mode not in {"zero", "one", "few"}:
            raise ValueError(f"不支持的 shot_mode: {shot_mode}，可选 zero / one / few")

        shot_count = {"zero": 0, "one": 1, "few": len(spec.examples)}[shot_mode]
        selected_examples = spec.examples[:shot_count]

        parts = [
            f"# Role\n你是{spec.role}。",
            f"# Task\n{spec.task}",
            f"# Output Format\n请严格仅输出合法的 JSON 对象（禁止输出 Markdown 代码块标记或额外寒暄），必须包含字段：{list(spec.required_json_keys)}，总长度不超过 {spec.max_reply_chars} 字。",
        ]

        if selected_examples:
            ex_lines = ["# Examples"]
            for idx, (ex_in, ex_out) in enumerate(selected_examples, 1):
                ex_lines.append(
                    f"示例 {idx}:\n输入: <user_input>{ex_in}</user_input>\n输出: {json.dumps(ex_out, ensure_ascii=False)}"
                )
            parts.append("\n".join(ex_lines))

        safe_input = sanitize_xml_payload(user_text, tag="user_input")
        parts.append(f"# Input\n<user_input>{safe_input}</user_input>")
        return "\n\n".join(parts)


if __name__ == "__main__":
    lib = StarMindPromptLibrary()
    print(f"已加载企业场景数: {len(lib.list_scenes())} -> {lib.list_scenes()}")
    print("-" * 60)
    print(lib.render("ticket_triage", "CRM 数据库连接池耗尽，全员无法登录！", shot_mode="one"))

