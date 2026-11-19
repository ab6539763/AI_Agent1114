"""Day 49 - 步骤一：带 SQLite Checkpointer 与 HITL 中断恢复的多 Agent 办公编排器。"""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)")
INJECTION_RE = re.compile(
    r"(忽略(以上|之前).{0,8}(指令|规则)|ignore\s+(all\s+)?previous\s+instructions|输出.{0,6}system\s*prompt)",
    re.IGNORECASE,
)


class TaskNotFoundError(KeyError):
    pass


class TaskConflictError(RuntimeError):
    pass


class OfficeAssistantOrchestrator:
    """
    星辰多 Agent 智能办公助手核心编排器：
    Guardrail(输入) -> Supervisor(意图路由) -> Specialist(专家执行) -> HITL Checkpointer -> Guardrail(PII脱敏)
    """

    def __init__(self, db_path: Union[str, Path] = ":memory:") -> None:
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS office_tasks (
                thread_id TEXT PRIMARY KEY,
                trace_id TEXT NOT NULL,
                status TEXT NOT NULL,
                routed_agent TEXT NOT NULL,
                state_json TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()
        self._docs = {
            "差旅": "一线城市住宿上限 600 元/晚，餐补 120 元/天；单笔报销超过 5000 元须人工复核。",
            "年假": "年假 3 天及以内由直属主管审批，超过 3 天须部门负责人审批。",
        }
        self._meetings: List[Dict[str, Any]] = [
            {"date": "2026-11-20", "start_hour": 10, "end_hour": 11, "title": "架构周会"}
        ]

    def _save_task(self, thread_id: str, trace_id: str, status: str, routed_agent: str, state: Dict[str, Any]) -> None:
        self._conn.execute(
            """
            INSERT INTO office_tasks (thread_id, trace_id, status, routed_agent, state_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(thread_id) DO UPDATE SET
                status = excluded.status,
                state_json = excluded.state_json,
                updated_at = excluded.updated_at
            """,
            (thread_id, trace_id, status, routed_agent, json.dumps(state, ensure_ascii=False), time.time()),
        )
        self._conn.commit()

    def get_task(self, thread_id: str) -> Dict[str, Any]:
        row = self._conn.execute(
            "SELECT thread_id, trace_id, status, routed_agent, state_json FROM office_tasks WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()
        if not row:
            raise TaskNotFoundError(f"未找到任务线程: {thread_id}")
        return {
            "thread_id": row[0],
            "trace_id": row[1],
            "status": row[2],
            "routed_agent": row[3],
            "state": json.loads(row[4]),
        }

    @staticmethod
    def _redact_pii(text: str) -> str:
        return PHONE_RE.sub(r"\1****\2", text)

    @staticmethod
    def _route_intent(query: str) -> str:
        if any(k in query for k in ("制度", "标准", "规范", "是什么", "查询")):
            return "knowledge_agent"
        if any(k in query for k in ("报销", "请假", "审批")):
            return "approval_agent"
        if any(k in query for k in ("邮件", "会议", "日程", "预定")):
            return "scheduler_agent"
        return "knowledge_agent"

    def chat(
        self,
        query: str,
        user_id: str = "emp_01",
        params: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()
        tid = thread_id or f"th_{uuid.uuid4().hex[:10]}"
        trace_id = f"tr_{uuid.uuid4().hex[:8]}"
        p = params or {}

        # 1. Input Guardrail：拦截 Prompt 注入
        if INJECTION_RE.search(query):
            state = {"query": query, "user_id": user_id, "reply": "触发安全护栏：检测到疑似 Prompt 注入，请求已阻断。"}
            self._save_task(tid, trace_id, "BLOCKED", "guardrail", state)
            return self._build_response(tid, trace_id, "BLOCKED", "guardrail", state, t0)

        # 2. Supervisor 意图路由
        agent = self._route_intent(query)

        # 3. 专家 Agent 分发执行
        if agent == "knowledge_agent":
            matched = [v for k, v in self._docs.items() if k in query]
            raw_reply = "；".join(matched) if matched else "未命中专项制度，建议联系行政部值班电话 13812345678。"
            reply = self._redact_pii(raw_reply)
            state = {"query": query, "user_id": user_id, "reply": reply, "pending_action": None}
            self._save_task(tid, trace_id, "COMPLETED", agent, state)
            return self._build_response(tid, trace_id, "COMPLETED", agent, state, t0)

        if agent == "scheduler_agent":
            if "邮件" in query:
                pending = {
                    "action_type": "SEND_EMAIL",
                    "to": p.get("to_email", "client@partner.com"),
                    "subject": p.get("subject", "星辰智脑合作同步"),
                    "body": self._redact_pii(p.get("body", query)),
                }
                state = {
                    "query": query,
                    "user_id": user_id,
                    "reply": f"已生成发往 {pending['to']} 的邮件草稿，属于高危外发操作，请人工确认后发送。",
                    "pending_action": pending,
                }
                self._save_task(tid, trace_id, "WAITING_CONFIRMATION", agent, state)
                return self._build_response(tid, trace_id, "WAITING_CONFIRMATION", agent, state, t0)

            # 预定日程（低风险直出，含冲突校验）
            date = p.get("date", "2026-11-20")
            s_hr, e_hr = int(p.get("start_hour", 14)), int(p.get("end_hour", 15))
            conflict = any(m["date"] == date and s_hr < m["end_hour"] and m["start_hour"] < e_hr for m in self._meetings)
            if conflict:
                reply = f"会议时段冲突：{date} {s_hr}:00-{e_hr}:00 已有安排，请更换时段。"
            else:
                self._meetings.append({"date": date, "start_hour": s_hr, "end_hour": e_hr, "title": p.get("title", "项目会")})
                reply = f"会议预定成功：{date} {s_hr}:00-{e_hr}:00。"
            state = {"query": query, "user_id": user_id, "reply": reply, "pending_action": None}
            self._save_task(tid, trace_id, "COMPLETED", agent, state)
            return self._build_response(tid, trace_id, "COMPLETED", agent, state, t0)

        # approval_agent
        amount = float(p.get("amount", 1000.0))
        if amount > 5000.0:
            pending = {"action_type": "SUBMIT_EXPENSE", "applicant": user_id, "amount": amount, "reason": query}
            state = {
                "query": query,
                "user_id": user_id,
                "reply": f"报销金额 ¥{amount:.2f} 超过 5000 元红线，已挂起等待部门总监人工确认。",
                "pending_action": pending,
            }
            self._save_task(tid, trace_id, "WAITING_CONFIRMATION", agent, state)
            return self._build_response(tid, trace_id, "WAITING_CONFIRMATION", agent, state, t0)

        state = {
            "query": query,
            "user_id": user_id,
            "reply": f"小额审批单（¥{amount:.2f}）已自动提交至 OA 系统。",
            "pending_action": None,
        }
        self._save_task(tid, trace_id, "COMPLETED", agent, state)
        return self._build_response(tid, trace_id, "COMPLETED", agent, state, t0)

    def confirm(self, thread_id: str, approved: bool, reviewer: str = "总监", comment: str = "") -> Dict[str, Any]:
        """人工确认恢复端点：对 WAITING_CONFIRMATION 任务执行放行或安全撤销。"""
        t0 = time.perf_counter()
        task = self.get_task(thread_id)
        if task["status"] != "WAITING_CONFIRMATION":
            raise TaskConflictError(f"任务当前状态为 {task['status']}，不可重复确认")

        state = task["state"]
        action = state.get("pending_action") or {}
        if approved:
            new_status = "COMPLETED"
            state["execution_result"] = {"executed": True, "reviewer": reviewer, "comment": comment, "action": action}
            state["reply"] = f"人工已确认通过（审批人：{reviewer}），动作 {action.get('action_type')} 执行成功。"
        else:
            new_status = "REJECTED"
            state["execution_result"] = {"executed": False, "reviewer": reviewer, "comment": comment, "action": action}
            state["reply"] = f"人工已拒绝（审批人：{reviewer}），动作 {action.get('action_type')} 已安全撤销。"

        state["pending_action"] = None
        self._save_task(thread_id, task["trace_id"], new_status, task["routed_agent"], state)
        return self._build_response(thread_id, task["trace_id"], new_status, task["routed_agent"], state, t0)

    @staticmethod
    def _build_response(
        thread_id: str,
        trace_id: str,
        status: str,
        routed_agent: str,
        state: Dict[str, Any],
        t0: float,
    ) -> Dict[str, Any]:
        return {
            "thread_id": thread_id,
            "trace_id": trace_id,
            "status": status,
            "routed_agent": routed_agent,
            "reply": state["reply"],
            "pending_action": state.get("pending_action"),
            "latency_ms": round((time.perf_counter() - t0) * 1000.0, 2),
        }

    def close(self) -> None:
        self._conn.close()


if __name__ == "__main__":
    orch = OfficeAssistantOrchestrator(":memory:")
    r1 = orch.chat("帮我发邮件通知客户项目里程碑", params={"to_email": "vp@client.cn", "subject": "周报同步"})
    print("发起高危任务:", r1["status"], "|", r1["reply"])
    r2 = orch.confirm(r1["thread_id"], approved=True, reviewer="老陈")
    print("人工放行结果:", r2["status"], "|", r2["reply"])
    orch.close()

