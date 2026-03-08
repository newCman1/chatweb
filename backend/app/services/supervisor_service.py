import asyncio
import contextvars
import logging
import re
from dataclasses import asdict
from typing import Optional
from uuid import uuid4

import httpx

from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import log_event
from app.db.session import db
from app.models.chat import utc_now_iso
from app.models.supervisor import SupervisorRunRecord, SupervisorTaskRecord
from app.schemas.supervisor import SupervisorRunRequest
from app.services.ai_client import AIRequestOptions, ai_client
from app.services.chat_service import chat_service


def _run_from_row(row, tasks: list[SupervisorTaskRecord]) -> SupervisorRunRecord:
    return SupervisorRunRecord(
        id=row["id"],
        conversation_id=row["conversation_id"],
        objective=row["objective"],
        plan_text=row["plan_text"],
        primary_name=row["primary_name"],
        worker_name=row["worker_name"],
        status=row["status"],
        summary=row["summary"],
        created_at=row["created_at"],
        tasks=tasks,
    )


def _task_from_row(row) -> SupervisorTaskRecord:
    return SupervisorTaskRecord(
        index=row["task_index"],
        title=row["title"],
        worker_output=row["worker_output"],
        review_verdict=row["review_verdict"],
        review_feedback=row["review_feedback"],
        status=row["status"],
        retries=row["retries"],
    )


class SupervisorService:
    def __init__(self) -> None:
        self._runs: dict[str, SupervisorRunRecord] = {}
        self._run_tasks: dict[str, asyncio.Task[None]] = {}
        self._abort_flags: dict[str, asyncio.Event] = {}
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger("chatweb.backend.services.supervisor")
        self._primary_runtime_options_var: contextvars.ContextVar[Optional[AIRequestOptions]] = contextvars.ContextVar(
            "supervisor_primary_runtime_options", default=None
        )
        self._worker_runtime_options_var: contextvars.ContextVar[Optional[AIRequestOptions]] = contextvars.ContextVar(
            "supervisor_worker_runtime_options", default=None
        )

    async def run(self, payload: SupervisorRunRequest) -> SupervisorRunRecord:
        objective = self._validate_payload(payload)
        run_id = str(uuid4())
        record = self._new_run_record(run_id, payload, objective)
        async with self._lock:
            self._runs[run_id] = record
        await self._persist_run(record)

        abort_flag = asyncio.Event()
        log_event(
            self._logger,
            logging.INFO,
            "supervisor.run.sync.start",
            {
                "run_id": run_id,
                "conversation_id": payload.conversation_id,
                "max_tasks": payload.max_tasks,
                "max_retries": payload.max_retries,
            },
        )
        await self._execute_pipeline(record, payload, abort_flag)
        await self._persist_run(record)
        log_event(
            self._logger,
            logging.INFO,
            "supervisor.run.sync.done",
            {"run_id": run_id, "status": record.status, "task_count": len(record.tasks)},
        )
        return record

    async def start(self, payload: SupervisorRunRequest) -> SupervisorRunRecord:
        objective = self._validate_payload(payload)
        run_id = str(uuid4())
        record = self._new_run_record(run_id, payload, objective)
        abort_flag = asyncio.Event()

        async with self._lock:
            self._runs[run_id] = record
            self._abort_flags[run_id] = abort_flag
            self._run_tasks[run_id] = asyncio.create_task(self._execute_in_background(run_id, payload, abort_flag))
        await self._persist_run(record)

        log_event(
            self._logger,
            logging.INFO,
            "supervisor.run.async.started",
            {"run_id": run_id, "conversation_id": payload.conversation_id},
        )
        return record

    async def abort(self, run_id: str) -> SupervisorRunRecord:
        row = await self.get_run(run_id)
        if row.status in {"completed", "failed", "aborted"}:
            return row

        row.status = "aborted"
        if not row.summary:
            row.summary = "Run aborted by user."
        for item in row.tasks:
            if item.status == "running":
                item.status = "aborted"
                if not item.review_feedback:
                    item.review_feedback = "Aborted by user."

        async with self._lock:
            flag = self._abort_flags.get(run_id)
            task = self._run_tasks.get(run_id)
            self._runs[run_id] = row

        if flag:
            flag.set()
        if task and not task.done():
            task.cancel()
        await self._persist_run(row)
        log_event(self._logger, logging.WARNING, "supervisor.run.abort", {"run_id": run_id})
        return row

    async def get_run(self, run_id: str) -> SupervisorRunRecord:
        cached = self._runs.get(run_id)
        if cached:
            return cached
        row = await self._load_run(run_id)
        if not row:
            raise AppError("SUPERVISOR_RUN_NOT_FOUND", f"Run not found: {run_id}", status_code=404)
        return row

    async def list_runs(self, conversation_id: str, limit: int = 20) -> list[SupervisorRunRecord]:
        rows = await db.fetchall(
            """
            SELECT id, conversation_id, objective, plan_text, primary_name, worker_name,
                   status, summary, created_at
            FROM supervisor_runs
            WHERE conversation_id = ?
            ORDER BY created_at DESC
            LIMIT ?;
            """,
            (conversation_id, max(1, min(100, limit))),
        )
        values: list[SupervisorRunRecord] = []
        for row in rows:
            tasks = await self._load_tasks(row["id"])
            values.append(_run_from_row(row, tasks))
        return values

    async def _execute_in_background(
        self,
        run_id: str,
        payload: SupervisorRunRequest,
        abort_flag: asyncio.Event,
    ) -> None:
        row = await self.get_run(run_id)
        try:
            await self._execute_pipeline(row, payload, abort_flag)
        except asyncio.CancelledError:
            row.status = "aborted"
            if not row.summary:
                row.summary = "Run aborted by user."
            for item in row.tasks:
                if item.status == "running":
                    item.status = "aborted"
                    if not item.review_feedback:
                        item.review_feedback = "Aborted by user."
            log_event(self._logger, logging.WARNING, "supervisor.run.cancelled", {"run_id": run_id})
        except AppError as error:
            row.status = "failed"
            row.summary = f"{error.code}: {error.message}"
            log_event(
                self._logger,
                logging.ERROR,
                "supervisor.run.app_error",
                {"run_id": run_id, "code": error.code, "message": error.message},
            )
        except Exception as error:
            row.status = "failed"
            row.summary = "Unexpected supervisor failure."
            log_event(
                self._logger,
                logging.ERROR,
                "supervisor.run.error",
                {"run_id": run_id, "error": str(error)},
            )
        finally:
            await self._persist_run(row)
            async with self._lock:
                self._runs[run_id] = row
                self._run_tasks.pop(run_id, None)
                self._abort_flags.pop(run_id, None)

    async def _execute_pipeline(
        self,
        row: SupervisorRunRecord,
        payload: SupervisorRunRequest,
        abort_flag: asyncio.Event,
    ) -> None:
        primary_option_token = self._primary_runtime_options_var.set(self._runtime_primary_options(payload))
        worker_option_token = self._worker_runtime_options_var.set(self._runtime_worker_options(payload))
        try:
            history = await chat_service.list_messages(payload.conversation_id)
            shared_context = self._format_history(history)

            plan_text = payload.plan.strip() if payload.plan and payload.plan.strip() else ""
            if not plan_text:
                self._raise_if_aborted(abort_flag)
                plan_text = await self._primary_plan(row.objective, shared_context, payload.max_tasks)
            row.plan_text = plan_text
            await self._persist_run(row)

            task_titles = self._extract_tasks(plan_text, payload.max_tasks)
            if not task_titles:
                task_titles = [row.objective]

            row.tasks.clear()
            for index, title in enumerate(task_titles, start=1):
                self._raise_if_aborted(abort_flag)
                item = SupervisorTaskRecord(
                    index=index,
                    title=title,
                    worker_output="",
                    review_verdict="PENDING",
                    review_feedback="",
                    status="running",
                    retries=0,
                )
                row.tasks.append(item)
                await self._persist_run(row)

                worker_output = await self._worker_execute(title, row.objective, row.plan_text, shared_context)
                self._raise_if_aborted(abort_flag)
                verdict, feedback = await self._primary_review(title, row.objective, row.plan_text, worker_output)

                while verdict == "REVISE" and item.retries < payload.max_retries:
                    self._raise_if_aborted(abort_flag)
                    item.retries += 1
                    worker_output = await self._worker_execute(
                        title,
                        row.objective,
                        row.plan_text,
                        shared_context,
                        review_feedback=feedback,
                    )
                    verdict, feedback = await self._primary_review(title, row.objective, row.plan_text, worker_output)

                item.worker_output = worker_output
                item.review_verdict = verdict
                item.review_feedback = feedback
                item.status = "completed" if verdict == "PASS" else "failed"
                shared_context = self._append_task_exchange_to_context(
                    shared_context=shared_context,
                    primary_name=row.primary_name,
                    worker_name=row.worker_name,
                    task=item,
                )
                await self._persist_run(row)
                log_event(
                    self._logger,
                    logging.INFO,
                    "supervisor.task.done",
                    {
                        "run_id": row.id,
                        "task_index": item.index,
                        "status": item.status,
                        "retries": item.retries,
                    },
                )

            self._raise_if_aborted(abort_flag)
            row.summary = await self._primary_summary(row.objective, row.plan_text, row.tasks)
            row.status = "completed" if all(item.status == "completed" for item in row.tasks) else "failed"
            await self._persist_run(row)
        finally:
            self._primary_runtime_options_var.reset(primary_option_token)
            self._worker_runtime_options_var.reset(worker_option_token)

    def _append_task_exchange_to_context(
        self,
        shared_context: str,
        primary_name: str,
        worker_name: str,
        task: SupervisorTaskRecord,
    ) -> str:
        worker_output = task.worker_output.strip() or "(empty)"
        review_feedback = task.review_feedback.strip() or "No feedback."
        exchange = (
            f"[{worker_name}] Task {task.index}: {task.title}\n{worker_output}\n"
            f"[{primary_name}] Review Task {task.index}: {task.review_verdict}\n{review_feedback}"
        )
        if not shared_context or shared_context == "(empty)":
            return exchange
        return f"{shared_context}\n{exchange}"

    def _validate_payload(self, payload: SupervisorRunRequest) -> str:
        objective = payload.objective.strip()
        if not objective:
            raise AppError("SUPERVISOR_EMPTY_OBJECTIVE", "objective is required", status_code=400)
        if payload.max_tasks <= 0 or payload.max_tasks > 8:
            raise AppError("SUPERVISOR_INVALID_MAX_TASKS", "maxTasks must be between 1 and 8", status_code=400)
        if payload.max_retries < 0 or payload.max_retries > 3:
            raise AppError("SUPERVISOR_INVALID_MAX_RETRIES", "maxRetries must be between 0 and 3", status_code=400)
        return objective

    def _new_run_record(self, run_id: str, payload: SupervisorRunRequest, objective: str) -> SupervisorRunRecord:
        return SupervisorRunRecord(
            id=run_id,
            conversation_id=payload.conversation_id,
            objective=objective,
            plan_text=payload.plan.strip() if payload.plan and payload.plan.strip() else "",
            primary_name=settings.supervisor_primary_name,
            worker_name=settings.supervisor_worker_name,
            status="running",
            summary="",
            created_at=utc_now_iso(),
            tasks=[],
        )

    def _raise_if_aborted(self, abort_flag: asyncio.Event) -> None:
        if abort_flag.is_set():
            raise asyncio.CancelledError()

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
        runtime = self._primary_runtime_options_var.get()
        return AIRequestOptions(
            api_key=(runtime.api_key if runtime and runtime.api_key else settings.supervisor_primary_api_key or None),
            base_url=(
                runtime.base_url if runtime and runtime.base_url else settings.supervisor_primary_base_url or None
            ),
            model=(runtime.model if runtime and runtime.model else settings.supervisor_primary_model or None),
            reasoning_model=(
                runtime.reasoning_model
                if runtime and runtime.reasoning_model
                else settings.supervisor_primary_reasoning_model or None
            ),
        )

    def _worker_options(self) -> AIRequestOptions:
        runtime = self._worker_runtime_options_var.get()
        return AIRequestOptions(
            api_key=(runtime.api_key if runtime and runtime.api_key else settings.supervisor_worker_api_key or None),
            base_url=(runtime.base_url if runtime and runtime.base_url else settings.supervisor_worker_base_url or None),
            model=(runtime.model if runtime and runtime.model else settings.supervisor_worker_model or None),
            reasoning_model=(
                runtime.reasoning_model
                if runtime and runtime.reasoning_model
                else settings.supervisor_worker_reasoning_model or None
            ),
        )

    def _runtime_primary_options(self, payload: SupervisorRunRequest) -> AIRequestOptions:
        return AIRequestOptions(
            api_key=self._clean_optional(payload.primary_api_key),
            base_url=self._clean_optional(payload.primary_api_base_url),
            model=self._clean_optional(payload.primary_api_model),
            reasoning_model=self._clean_optional(payload.primary_api_reasoning_model),
        )

    def _runtime_worker_options(self, payload: SupervisorRunRequest) -> AIRequestOptions:
        return AIRequestOptions(
            api_key=self._clean_optional(payload.worker_api_key),
            base_url=self._clean_optional(payload.worker_api_base_url),
            model=self._clean_optional(payload.worker_api_model),
            reasoning_model=self._clean_optional(payload.worker_api_reasoning_model),
        )

    def _clean_optional(self, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

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

    async def _persist_run(self, row: SupervisorRunRecord) -> None:
        now = utc_now_iso()
        statements = [
            (
                """
                INSERT INTO supervisor_runs
                (id, conversation_id, objective, plan_text, primary_name, worker_name,
                 status, summary, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    conversation_id=excluded.conversation_id,
                    objective=excluded.objective,
                    plan_text=excluded.plan_text,
                    primary_name=excluded.primary_name,
                    worker_name=excluded.worker_name,
                    status=excluded.status,
                    summary=excluded.summary,
                    updated_at=excluded.updated_at;
                """,
                (
                    row.id,
                    row.conversation_id,
                    row.objective,
                    row.plan_text,
                    row.primary_name,
                    row.worker_name,
                    row.status,
                    row.summary,
                    row.created_at,
                    now,
                ),
            ),
            ("DELETE FROM supervisor_tasks WHERE run_id = ?;", (row.id,)),
        ]
        tasks_payload = [
            (
                row.id,
                item.index,
                item.title,
                item.worker_output,
                item.review_verdict,
                item.review_feedback,
                item.status,
                item.retries,
                row.created_at,
                now,
            )
            for item in row.tasks
        ]
        many = [
            (
                """
                INSERT INTO supervisor_tasks
                (run_id, task_index, title, worker_output, review_verdict, review_feedback,
                 status, retries, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                tasks_payload,
            )
        ]
        await db.transaction(statements, many)

    async def _load_run(self, run_id: str) -> Optional[SupervisorRunRecord]:
        row = await db.fetchone(
            """
            SELECT id, conversation_id, objective, plan_text, primary_name, worker_name,
                   status, summary, created_at
            FROM supervisor_runs
            WHERE id = ?;
            """,
            (run_id,),
        )
        if not row:
            return None
        tasks = await self._load_tasks(run_id)
        return _run_from_row(row, tasks)

    async def _load_tasks(self, run_id: str) -> list[SupervisorTaskRecord]:
        rows = await db.fetchall(
            """
            SELECT task_index, title, worker_output, review_verdict, review_feedback, status, retries
            FROM supervisor_tasks
            WHERE run_id = ?
            ORDER BY task_index ASC;
            """,
            (run_id,),
        )
        return [_task_from_row(row) for row in rows]


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
