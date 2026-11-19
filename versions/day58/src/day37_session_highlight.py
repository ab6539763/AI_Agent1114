"""
Day 37 - 步骤一：阶段项目二(下) 多会话管理、多轮查询改写、安全引用高亮与 SSE 流式引擎
"""

from __future__ import annotations

import html
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Sequence, Tuple


@dataclass
class ChatTurn:
    role: str  # "user" | "assistant"
    content: str
    rewritten_query: Optional[str] = None


@dataclass
class HighlightedCitation:
    index: int
    doc_id: str
    source: str
    section: str
    raw_snippet: str
    highlighted_snippet: str
    score: float


class SessionManager:
    """多会话对话历史管理器：支持按 session_id 隔离与滑动窗口自动裁剪。"""

    def __init__(self, max_turns: int = 6) -> None:
        self.max_turns = max_turns
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, title: str = "新对话", department: str = "public") -> str:
        sid = f"sess_{uuid.uuid4().hex[:10]}"
        self._sessions[sid] = {
            "session_id": sid,
            "title": title,
            "department": department,
            "history": [],
        }
        return sid

    def ensure_session(self, session_id: Optional[str], department: str = "public") -> str:
        if session_id and session_id in self._sessions:
            return session_id
        if session_id:
            self._sessions[session_id] = {
                "session_id": session_id,
                "title": "自动创建会话",
                "department": department,
                "history": [],
            }
            return session_id
        return self.create_session(department=department)

    def append_turn(self, session_id: str, role: str, content: str, rewritten_query: Optional[str] = None) -> None:
        sess = self._sessions[session_id]
        sess["history"].append(ChatTurn(role=role, content=content, rewritten_query=rewritten_query))
        max_msgs = self.max_turns * 2
        if len(sess["history"]) > max_msgs:
            sess["history"] = sess["history"][-max_msgs:]

    def get_history(self, session_id: str) -> List[ChatTurn]:
        if session_id not in self._sessions:
            raise KeyError(f"Session {session_id} not found")
        return list(self._sessions[session_id]["history"])

    def list_sessions(self) -> List[Dict[str, Any]]:
        return [
            {
                "session_id": s["session_id"],
                "title": s["title"],
                "department": s["department"],
                "turn_count": len(s["history"]) // 2,
            }
            for s in self._sessions.values()
        ]

    def delete_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None


class MultiTurnQueryRewriter:
    """
    多轮对话指代消解改写器：
    识别「它/这个/该制度/那…」等指代词与短追问，从上一轮用户问题中提取主题实体进行语义补全。
    """

    PRONOUNS = ("它", "这个", "那个", "该制度", "这项", "上面")
    TOPIC_KEYWORDS = ("年假", "病假", "出差", "住宿", "餐饮", "发布窗口", "周五", "ERR-5042", "VPN", "天枢项目")

    def rewrite(self, history: Sequence[ChatTurn], current_query: str) -> str:
        user_turns = [t for t in history if t.role == "user"]
        if not user_turns:
            return current_query

        last_q = user_turns[-1].rewritten_query or user_turns[-1].content
        # 抽取上一轮的核心业务主题
        anchor = next((kw for kw in self.TOPIC_KEYWORDS if kw in last_q), "")
        if not anchor:
            anchor = re.sub(r"[？?！!。，,请问一下呢吧]", "", last_q)[:10]

        has_pronoun = any(p in current_query for p in self.PRONOUNS)
        is_short_followup = (current_query.startswith("那") or len(current_query.strip()) <= 11) and (
            anchor not in current_query
        )

        if not has_pronoun and not is_short_followup:
            return current_query

        rewritten = current_query
        for p in self.PRONOUNS:
            if p in rewritten:
                rewritten = rewritten.replace(p, anchor)
        if anchor not in rewritten:
            rewritten = f"关于{anchor}，{rewritten}"
        return rewritten


class CitationHighlighter:
    """安全引用溯源高亮器：先 HTML 转义防 XSS，再对命中关键词插入 <mark>...</mark> 高亮标签。"""

    STOP_WORDS = {"怎么", "多少", "什么", "需要", "可以", "请问", "关于", "一下", "是否", "如何", "我们"}

    @classmethod
    def highlight(cls, query: str, snippet: str) -> str:
        safe_text = html.escape(snippet)
        # 提取英文/错误码/数字与长度>=2的中文关键片段
        raw_terms = re.findall(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*|[\u4e00-\u9fff]{2,4}", query)
        candidates: List[str] = []
        for term in raw_terms:
            if term in cls.STOP_WORDS:
                continue
            if len(term) > 2 and re.fullmatch(r"[\u4e00-\u9fff]+", term):
                # 同时加入完整短语和二元词组以提高命中率
                candidates.append(term)
                for i in range(len(term) - 1):
                    bg = term[i : i + 2]
                    if bg not in cls.STOP_WORDS:
                        candidates.append(bg)
            else:
                candidates.append(term)

        # 去重并按长度降序，优先匹配长词避免碎片化高亮
        unique_terms = sorted(set(candidates), key=len, reverse=True)
        matched_terms = [t for t in unique_terms if t.lower() in safe_text.lower()][:6]
        if not matched_terms:
            return safe_text

        pattern = re.compile("|".join(re.escape(t) for t in matched_terms), flags=re.IGNORECASE)
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", safe_text)


class StreamingKBService:
    """集多会话、多轮改写、混合检索、引用高亮与 SSE 流式生成于一体的项目二完整服务。"""

    def __init__(self) -> None:
        self.sessions = SessionManager(max_turns=6)
        self.rewriter = MultiTurnQueryRewriter()
        self.docs: List[Dict[str, str]] = [
            {
                "doc_id": "hr-leave",
                "source": "HR员工休假手册.md",
                "section": "年假与审批流程",
                "department": "public",
                "content": "入职满1年员工享有5天带薪年假，年假需提前3个工作日在OA系统提交审批；病假超过2天须提供公立医院诊断证明。",
            },
            {
                "doc_id": "fin-travel",
                "source": "财务差旅制度.md",
                "section": "差旅住宿与餐补标准",
                "department": "public",
                "content": "一线城市（北京、上海、深圳、广州）出差酒店住宿上限每晚600元，餐饮补助按每天100元定额随工资发放，出差需提前3天在OA发起申请。",
            },
            {
                "doc_id": "ops-5042",
                "source": "运维排障手册.md",
                "section": "ERR-5042网关超时",
                "department": "rd",
                "content": "错误码ERR-5042表示星辰统一网关调用上游推理服务超时（默认15秒），排查步骤：检查上游显存水位并调大proxy_read_timeout。",
            },
        ]

    def _retrieve(self, query: str, department: str = "public", top_k: int = 2) -> List[Tuple[Dict[str, str], float]]:
        allowed = {"public", department}
        q_lower = query.lower()
        q_terms = set(re.findall(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", q_lower))
        for chunk in re.findall(r"[\u4e00-\u9fff]+", q_lower):
            for i in range(len(chunk) - 1):
                q_terms.add(chunk[i : i + 2])

        q_codes = set(re.findall(r"[a-z0-9]+[-_][a-z0-9]+", q_lower))
        scored: List[Tuple[Dict[str, str], float]] = []
        for d in self.docs:
            if d["department"] not in allowed:
                continue
            text = (d["section"] + " " + d["content"]).lower()
            hits = sum(1 for t in q_terms if t in text)
            code_bonus = 0.5 if (q_codes and any(c in text for c in q_codes)) else 0.0
            score = round(min(1.0, hits / max(1, len(q_terms)) + code_bonus), 4)
            if score >= 0.18:
                scored.append((d, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def prepare_answer(
        self,
        session_id: Optional[str],
        question: str,
        department: str = "public",
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        sid = self.sessions.ensure_session(session_id, department=department)
        history = self.sessions.get_history(sid)
        rewritten = self.rewriter.rewrite(history, question)
        hits = self._retrieve(rewritten, department=department, top_k=2)

        if not hits:
            answer = "抱歉，星辰知识库中未检索到足够依据回答当前问题。"
            citations: List[HighlightedCitation] = []
        else:
            citations = [
                HighlightedCitation(
                    index=i,
                    doc_id=d["doc_id"],
                    source=d["source"],
                    section=d["section"],
                    raw_snippet=d["content"],
                    highlighted_snippet=CitationHighlighter.highlight(rewritten, d["content"]),
                    score=sc,
                )
                for i, (d, sc) in enumerate(hits, start=1)
            ]
            top_c = citations[0]
            answer = f"根据《{top_c.source}》（{top_c.section}）：{top_c.raw_snippet} [1]"

        # 将本轮用户原问题与回答写入会话记忆
        self.sessions.append_turn(sid, "user", question, rewritten_query=rewritten)
        self.sessions.append_turn(sid, "assistant", answer)

        return {
            "session_id": sid,
            "original_question": question,
            "rewritten_query": rewritten,
            "answer": answer,
            "citations": citations,
            "latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
        }

    def stream_sse_events(
        self,
        session_id: Optional[str],
        question: str,
        department: str = "public",
        chunk_chars: int = 12,
    ) -> Generator[str, None, None]:
        """按标准 SSE 帧协议依次流式推送：meta -> citation -> token -> done。"""
        result = self.prepare_answer(session_id=session_id, question=question, department=department)

        # 1. 元数据帧（前端可展示“已理解上下文：xxx”）
        meta_payload = {
            "session_id": result["session_id"],
            "rewritten_query": result["rewritten_query"],
        }
        yield f"event: meta\ndata: {json.dumps(meta_payload, ensure_ascii=False)}\n\n"

        # 2. 高亮引用帧（Citations-First，右侧溯源栏瞬间点亮）
        for c in result["citations"]:
            cit_payload = {
                "index": c.index,
                "doc_id": c.doc_id,
                "source": c.source,
                "section": c.section,
                "highlighted_snippet": c.highlighted_snippet,
                "score": c.score,
            }
            yield f"event: citation\ndata: {json.dumps(cit_payload, ensure_ascii=False)}\n\n"

        # 3. 正文打字机分片帧
        answer = result["answer"]
        for i in range(0, len(answer), chunk_chars):
            piece = answer[i : i + chunk_chars]
            yield f"event: token\ndata: {json.dumps({'delta': piece}, ensure_ascii=False)}\n\n"

        # 4. 完成结束帧
        done_payload = {
            "session_id": result["session_id"],
            "total_chars": len(answer),
            "latency_ms": result["latency_ms"],
        }
        yield f"event: done\ndata: {json.dumps(done_payload, ensure_ascii=False)}\n\n"


if __name__ == "__main__":
    svc = StreamingKBService()
    sid = svc.sessions.create_session("年假咨询")
    r1 = svc.prepare_answer(sid, "入职满一年年假有几天？")
    r2 = svc.prepare_answer(sid, "它需要提前几天OA申请？")
    print("第2轮改写:", r2["rewritten_query"])
    print("高亮引用:", r2["citations"][0].highlighted_snippet)

