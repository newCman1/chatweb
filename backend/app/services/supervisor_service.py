import logging
import re
from dataclasses import asdict
from typing import Optional
from uuid import uuid4

import httpx

from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import log_event
from app.models.chat import utc_now_iso
from app.models.supervisor import SupervisorRunRecord, SupervisorTaskRecord
from app.schemas.supervisor import SupervisorRunRequest
from app.services.ai_client import AIRequestOptions, ai_client
from app.services.chat_service import chat_service


class SupervisorService:
    def __init__(self) -> None:
        self._runs: dict[str, SupervisorRunRecord] = {}
        self._logger = logging.getLogger("chatweb.backend.services.supervisor")

    async def run(self, payload: SupervisorRunRequest) -> SupervisorRunRecord:
        objective = payload.objective.strip()
        if not objective:
            raise AppError("SUPERVISOR_EMPTY_OBJECTIVE", "objective is required", status_code=400)
        if payload.max_tasks <= 0 or payload.max_tasks > 8:
            raise AppError("SUPERVISOR_INVALID_MAX_TASKS", "maxTasks must be between 1 and 8", status_code=400)
        if payload.max_retries < 0 or payload.max_retries > 3:
            raise AppError("SUPERVISOR_INVALID_MAX_RETRIES", "maxRetries must be between 0 and 3", status_code=400)

        run_id = str(uuid4())
        log_event(
            self._logger,
            logging.INFO,
            "supervisor.run.start",
            {
                "run_id": run_id,
                "conversation_id": payload.conversation_id,
                "max_tasks": payload.max_tasks,
                "max_retries": payload.max_retries,
            },
        )
        history = await chat_service.list_messages(payload.conversation_id)
        shared_history = self._format_history(history)

        plan_text = payload.plan.strip() if payload.plan and payload.plan.strip() else ""
        if not plan_text:
            plan_text = await self._primary_plan(objective, shared_history, payload.max_tasks)
        tasks = self._extract_tasks(plan_text, payload.max_tasks)
        if not tasks:
            tasks = [objective]

        task_rows: list[SupervisorTaskRecord] = []
        for index, title in enumerate(tasks, start=1):
            retries = 0
            worker_output = await self._worker_execute(title, objective, plan_text, shared_history)
            verdict, feedback = await self._primary_review(title, objective, plan_text, worker_output)

            while verdict == "REVISE" and retries < payload.max_retries:
                retries += 1
                worker_output = await self._worker_execute(
                    title,
                    objective,
                    plan_text,
                    shared_history,
                    review_feedback=feedback,
                )
                verdict, feedback = await self._primary_review(title, objective, plan_text, worker_output)

            status = "completed" if verdict == "PASS" else "failed"
            task_rows.append(
                SupervisorTaskRecord(
                    index=index,
                    title=title,
                    worker_output=worker_output,
                    review_verdict=verdict,
                    review_feedback=feedback,
                    status=status,
                    retries=retries,
                )
            )
            log_event(
                self._logger,
                logging.INFO,
                "supervisor.task.done",
                {
                    "run_id": run_id,
                    "task_index": index,
                    "status": status,
                    "retries": retries,
                },
            )

        summary = await self._primary_summary(objective, plan_text, task_rows)
        run_status = "completed" if all(item.status == "completed" for item in task_rows) else "failed"
        record = SupervisorRunRecord(
            id=run_id,
            conversation_id=payload.conversation_id,
            objective=objective,
            plan_text=plan_text,
            primary_name=settings.supervisor_primary_name,
            worker_name=settings.supervisor_worker_name,
            status=run_status,
            summary=summary,
            created_at=utc_now_iso(),
            tasks=task_rows,
        )
        self._runs[run_id] = record
        log_event(
            self._logger,
            logging.INFO,
            "supervisor.run.done",
            {"run_id": run_id, "status": run_status, "task_count": len(task_rows)},
        )
        return record

    def get_run(self, run_id: str) -> SupervisorRunRecord:
        row = self._runs.get(run_id)
        if not row:
            raise AppError("SUPERVISOR_RUN_NOT_FOUND", f"Run not found: {run_id}", status_code=404)
        return row

    async def _primary_plan(self, objective: str, shared_history: str, max_tasks: int) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a supervisor AI. Output a concise numbered task list only. "
                    "Each line must start with `1.` style numbering."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Objective:\n{objective}\n\n"
                    f"Conversation history:\n{shared_history}\n\n"
                    f"Generate at most {max_tasks} tasks."
                ),
            },
        ]
        return await self._run_model(messages, self._primary_options(), fallback=f"1. {objective}")

    async def _worker_execute(
        self,
        task_title: str,
        objective: str,
        plan_text: str,
        shared_history: str,
        review_feedback: Optional[str] = None,
    ) -> str:
        revise_note = f"\nReviewer feedback:\n{review_feedback}" if review_feedback else ""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a worker AI. Complete only the assigned task and return practical output. "
                    "Be concise and explicit."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Objective:\n{objective}\n\n"
                    f"Plan:\n{plan_text}\n\n"
                    f"Task:\n{task_title}\n\n"
                    f"Shared conversation history:\n{shared_history}{revise_note}"
                ),
            },
        ]
        return await self._run_model(messages, self._worker_options(), fallback=f"Task result draft for: {task_title}")

    async def _primary_review(
        self,
        task_title: str,
        objective: str,
        plan_text: str,
        worker_output: str,
    ) -> tuple[str, str]:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict supervisor reviewer. Reply with:\n"
                    "VERDICT: PASS or REVISE\n"
                    "FEEDBACK: one concise sentence."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Objective:\n{objective}\n\n"
                    f"Plan:\n{plan_text}\n\n"
                    f"Task:\n{task_title}\n\n"
                    f"Worker output:\n{worker_output}"
                ),
            },
        ]
        raw = await self._run_model(messages, self._primary_options(), fallback="VERDICT: PASS\nFEEDBACK: Accepted.")
        verdict = "PASS" if "VERDICT: PASS" in raw.upper() else "REVISE"
        feedback_match = re.search(r"FEEDBACK:\s*(.+)", raw, re.IGNORECASE)
        feedback = feedback_match.group(1).strip() if feedback_match else "No feedback."
        return verdict, feedback

    async def _primary_summary(
        self, objective: str, plan_text: str, tasks: list[SupervisorTaskRecord]
    ) -> str:
        compact_tasks = "\n".join(
            f"{item.index}. {item.title} => {item.status} ({item.review_feedback})" for item in tasks
        )
        messages = [
            {
                "role": "system",
                "content": "You are a supervisor AI. Summarize final execution status in 4 lines max.",
            },
            {
                "role": "user",
                "content": f"Objective:\n{objective}\n\nPlan:\n{plan_text}\n\nTask results:\n{compact_tasks}",
            },
        ]
        return await self._run_model(messages, self._primary_options(), fallback=compact_tasks)

    async def _run_model(
        self, messages: list[dict[str, str]], options: AIRequestOptions, fallback: str
    ) -> str:
        if not ai_client.is_enabled(options):
            return fallback
        out: list[str] = []
        try:
            async for event_type, delta in ai_client.stream_chat(messages, enable_thinking=False, options=options):
                if event_type == "answer" and delta:
                    out.append(delta)
        except httpx.HTTPError as error:
            log_event(
                self._logger,
                logging.WARNING,
                "supervisor.model.error",
                {"error": str(error), "fallback_used": True},
            )
            return fallback
        text = "".join(out).strip()
        return text if text else fallback

    def _primary_options(self) -> AIRequestOptions:
        return AIRequestOptions(
            api_key=settings.supervisor_primary_api_key or None,
            base_url=settings.supervisor_primary_base_url or None,
            model=settings.supervisor_primary_model or None,
            reasoning_model=settings.supervisor_primary_reasoning_model or None,
        )

    def _worker_options(self) -> AIRequestOptions:
        return AIRequestOptions(
            api_key=settings.supervisor_worker_api_key or None,
            base_url=settings.supervisor_worker_base_url or None,
            model=settings.supervisor_worker_model or None,
            reasoning_model=settings.supervisor_worker_reasoning_model or None,
        )

    def _extract_tasks(self, plan_text: str, max_tasks: int) -> list[str]:
        out: list[str] = []
        for raw in plan_text.splitlines():
            line = raw.strip()
            if not line:
                continue
            matched = re.match(r"^\d+\.\s*(.+)$", line)
            if matched:
                out.append(matched.group(1).strip())
            elif line.startswith("- "):
                out.append(line[2:].strip())
            if len(out) >= max_tasks:
                break
        return [item for item in out if item]

    def _format_history(self, history: list) -> str:
        if not history:
            return "(empty)"
        lines: list[str] = []
        for item in history[-12:]:
            snippet = item.content.strip().replace("\n", " ")
            lines.append(f"[{item.role}] {snippet[:240]}")
        return "\n".join(lines)


supervisor_service = SupervisorService()


def supervisor_to_dict(row: SupervisorRunRecord) -> dict:
    payload = asdict(row)
    return {
        "id": payload["id"],
        "conversationId": payload["conversation_id"],
        "objective": payload["objective"],
        "planText": payload["plan_text"],
        "primaryName": payload["primary_name"],
        "workerName": payload["worker_name"],
        "status": payload["status"],
        "summary": payload["summary"],
        "createdAt": payload["created_at"],
        "tasks": [
            {
                "index": item["index"],
                "title": item["title"],
                "workerOutput": item["worker_output"],
                "reviewVerdict": item["review_verdict"],
                "reviewFeedback": item["review_feedback"],
                "status": item["status"],
                "retries": item["retries"],
            }
            for item in payload["tasks"]
        ],
    }
