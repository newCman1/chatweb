import asyncio
import json
import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Optional
from uuid import uuid4

import httpx

from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import log_event
from app.db.session import db
from app.models.chat import ConversationRecord, MessageRecord, utc_now_iso
from app.services.ai_client import AIRequestOptions, ai_client
from app.services.web_search import search_web_context


def build_assistant_reply(user_text: str) -> str:
    return (
        f"You said: {user_text}\n\n"
        "This is a Python backend streaming demo response. Replace this with real model inference."
    )


def build_thinking_summary(user_text: str) -> str:
    brief = user_text.strip().replace("\n", " ")[:80]
    return (
        f"Understanding request: {brief}\n"
        "Planning the response structure.\n"
        "Generating final answer."
    )


def _conversation_from_row(row) -> ConversationRecord:
    return ConversationRecord(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _message_from_row(row) -> MessageRecord:
    return MessageRecord(
        id=row["id"],
        conversation_id=row["conversation_id"],
        role=row["role"],
        content=row["content"],
        thinking=row["thinking"] or "",
        status=row["status"],
        created_at=row["created_at"],
    )


class ChatService:
    def __init__(self) -> None:
        self._active_abort_flags: dict[str, asyncio.Event] = {}
        self._logger = logging.getLogger("chatweb.backend.services.chat")

    async def list_conversations(self) -> list[ConversationRecord]:
        log_event(self._logger, logging.INFO, "service.list_conversations.start")
        rows = await db.fetchall(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC;
            """
        )
        values = [_conversation_from_row(row) for row in rows]
        log_event(self._logger, logging.INFO, "service.list_conversations.done", {"count": len(values)})
        return values

    async def create_conversation(self) -> ConversationRecord:
        conversation_id = str(uuid4())
        now = utc_now_iso()
        await db.execute(
            """
            INSERT INTO conversations (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?);
            """,
            (conversation_id, "New Chat", now, now),
        )
        log_event(self._logger, logging.INFO, "conversation.created", {"conversation_id": conversation_id})
        return ConversationRecord(
            id=conversation_id,
            title="New Chat",
            created_at=now,
            updated_at=now,
        )

    async def list_messages(self, conversation_id: str) -> list[MessageRecord]:
        log_event(self._logger, logging.INFO, "service.list_messages.start", {"conversation_id": conversation_id})
        if not await self._conversation_exists(conversation_id):
            raise AppError(
                "CONVERSATION_NOT_FOUND",
                f"Conversation not found: {conversation_id}",
                status_code=404,
                context={"conversation_id": conversation_id},
            )
        rows = await db.fetchall(
            """
            SELECT id, conversation_id, role, content, thinking, status, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC, id ASC;
            """,
            (conversation_id,),
        )
        values = [_message_from_row(row) for row in rows]
        log_event(
            self._logger,
            logging.INFO,
            "service.list_messages.done",
            {"conversation_id": conversation_id, "count": len(values)},
        )
        return values

    async def append_user_message(self, conversation_id: str, content: str) -> MessageRecord:
        now = utc_now_iso()
        conversation = await self._get_conversation(conversation_id)
        if not conversation:
            await db.execute(
                """
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?);
                """,
                (conversation_id, "New Chat", now, now),
            )
            title = content.strip()[:24] or "New Chat"
            await db.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?;",
                (title, now, conversation_id),
            )
        else:
            title = conversation.title
            if title == "New Chat":
                title = content.strip()[:24] or "New Chat"
            await db.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?;",
                (title, now, conversation_id),
            )

        msg = MessageRecord(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="user",
            content=content,
            status="done",
            created_at=now,
        )
        await db.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, thinking, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (msg.id, conversation_id, msg.role, msg.content, msg.thinking, msg.status, msg.created_at),
        )
        log_event(
            self._logger,
            logging.INFO,
            "service.append_user_message.done",
            {"conversation_id": conversation_id, "message_id": msg.id},
        )
        return msg

    async def create_assistant_message_placeholder(self, conversation_id: str) -> MessageRecord:
        msg = MessageRecord(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="assistant",
            content="",
            thinking="",
            status="streaming",
            created_at=utc_now_iso(),
        )
        await db.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, thinking, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (msg.id, conversation_id, msg.role, msg.content, msg.thinking, msg.status, msg.created_at),
        )
        await self._touch_conversation(conversation_id)
        log_event(
            self._logger,
            logging.INFO,
            "service.assistant_placeholder.created",
            {"conversation_id": conversation_id, "message_id": msg.id},
        )
        return msg

    async def abort(self, conversation_id: str) -> None:
        if not await self._conversation_exists(conversation_id):
            raise AppError(
                "CONVERSATION_NOT_FOUND",
                f"Conversation not found: {conversation_id}",
                status_code=404,
                context={"conversation_id": conversation_id},
            )
        flag = self._active_abort_flags.get(conversation_id)
        if flag:
            flag.set()
            log_event(self._logger, logging.WARNING, "stream.abort.requested", {"conversation_id": conversation_id})
        else:
            log_event(self._logger, logging.INFO, "stream.abort.no_active_stream", {"conversation_id": conversation_id})

    async def stream_json(
        self,
        conversation_id: str,
        user_content: str,
        enable_thinking: bool,
        runtime_options: Optional["StreamRuntimeOptions"] = None,
    ) -> AsyncGenerator[str, None]:
        options = runtime_options or StreamRuntimeOptions()
        abort_flag = asyncio.Event()
        self._active_abort_flags[conversation_id] = abort_flag
        assistant = await self.create_assistant_message_placeholder(conversation_id)
        log_event(
            self._logger,
            logging.INFO,
            "stream.json.start",
            {
                "conversation_id": conversation_id,
                "message_id": assistant.id,
                "enable_thinking": enable_thinking,
                "enable_web_search": options.enable_web_search,
                "attachments_count": len(options.attachments),
            },
        )

        try:
            async for event_type, delta in self._stream_with_provider_fallback(
                conversation_id, user_content, enable_thinking, options
            ):
                if abort_flag.is_set():
                    await self._mark_stopped(conversation_id, assistant.id)
                    log_event(
                        self._logger,
                        logging.WARNING,
                        "stream.stopped",
                        {"conversation_id": conversation_id, "message_id": assistant.id},
                    )
                    yield 'event: done\ndata: {"stopped":true}\n\n'
                    return

                if event_type == "thinking":
                    await self._append_assistant_thinking(conversation_id, assistant.id, delta)
                    payload = json.dumps({"delta": delta}, ensure_ascii=False)
                    yield f"event: thinking\ndata: {payload}\n\n"
                else:
                    await self._append_assistant_text(conversation_id, assistant.id, delta)
                    payload = json.dumps({"delta": delta}, ensure_ascii=False)
                    yield f"event: chunk\ndata: {payload}\n\n"

            await self._mark_done(conversation_id, assistant.id)
            log_event(
                self._logger,
                logging.INFO,
                "stream.done",
                {"conversation_id": conversation_id, "message_id": assistant.id},
            )
            yield 'event: done\ndata: {"done":true}\n\n'
        except AppError as error:
            await self._mark_error(conversation_id, assistant.id)
            log_event(
                self._logger,
                logging.ERROR,
                "stream.app_error",
                {
                    "conversation_id": conversation_id,
                    "message_id": assistant.id,
                    "code": error.code,
                    "message": error.message,
                },
            )
            payload = json.dumps({"code": error.code, "message": error.message}, ensure_ascii=False)
            yield f"event: error\ndata: {payload}\n\n"
            yield 'event: done\ndata: {"error":true}\n\n'
        except Exception as error:
            await self._mark_error(conversation_id, assistant.id)
            log_event(
                self._logger,
                logging.ERROR,
                "stream.internal_error",
                {
                    "conversation_id": conversation_id,
                    "message_id": assistant.id,
                    "error": str(error),
                },
            )
            payload = json.dumps(
                {"code": "STREAM_INTERNAL_ERROR", "message": "Stream failed unexpectedly."},
                ensure_ascii=False,
            )
            yield f"event: error\ndata: {payload}\n\n"
            yield 'event: done\ndata: {"error":true}\n\n'
        finally:
            self._active_abort_flags.pop(conversation_id, None)

    async def stream_binary(
        self,
        conversation_id: str,
        user_content: str,
        enable_thinking: bool,
        runtime_options: Optional["StreamRuntimeOptions"] = None,
    ) -> AsyncGenerator[bytes, None]:
        options = runtime_options or StreamRuntimeOptions()
        abort_flag = asyncio.Event()
        self._active_abort_flags[conversation_id] = abort_flag
        assistant = await self.create_assistant_message_placeholder(conversation_id)
        log_event(
            self._logger,
            logging.INFO,
            "stream.binary.start",
            {
                "conversation_id": conversation_id,
                "message_id": assistant.id,
                "enable_thinking": enable_thinking,
                "enable_web_search": options.enable_web_search,
                "attachments_count": len(options.attachments),
            },
        )
        try:
            async for event_type, delta in self._stream_with_provider_fallback(
                conversation_id, user_content, enable_thinking, options
            ):
                if abort_flag.is_set():
                    await self._mark_stopped(conversation_id, assistant.id)
                    log_event(
                        self._logger,
                        logging.WARNING,
                        "stream.binary.stopped",
                        {"conversation_id": conversation_id, "message_id": assistant.id},
                    )
                    return
                if event_type != "answer":
                    continue
                content = delta.encode("utf-8")
                await self._append_assistant_text(conversation_id, assistant.id, delta)
                yield content
            await self._mark_done(conversation_id, assistant.id)
            log_event(
                self._logger,
                logging.INFO,
                "stream.binary.done",
                {"conversation_id": conversation_id, "message_id": assistant.id},
            )
        finally:
            self._active_abort_flags.pop(conversation_id, None)

    async def _stream_with_provider_fallback(
        self,
        conversation_id: str,
        user_content: str,
        enable_thinking: bool,
        runtime_options: "StreamRuntimeOptions",
    ) -> AsyncGenerator[tuple[str, str], None]:
        ai_options = AIRequestOptions(
            api_key=runtime_options.api_key,
            base_url=runtime_options.api_base_url,
            model=runtime_options.api_model,
            reasoning_model=runtime_options.api_reasoning_model,
        )
        if ai_client.is_enabled(ai_options):
            history = await self._build_provider_messages(
                conversation_id,
                user_content=user_content,
                enable_web_search=runtime_options.enable_web_search,
                attachments=runtime_options.attachments,
            )
            try:
                async for event_type, delta in ai_client.stream_chat(
                    history, enable_thinking=enable_thinking, options=ai_options
                ):
                    if event_type == "thinking" and not enable_thinking:
                        continue
                    yield (event_type, delta)
                return
            except httpx.HTTPError as error:
                log_event(
                    self._logger,
                    logging.ERROR,
                    "stream.provider.failed",
                    {
                        "conversation_id": conversation_id,
                        "error": str(error),
                        "enable_web_search": runtime_options.enable_web_search,
                    },
                )
                if not settings.ai_fallback_on_error:
                    raise AppError(
                        "AI_PROVIDER_ERROR",
                        "Provider request failed.",
                        status_code=502,
                        context={"conversation_id": conversation_id},
                    )
                log_event(
                    self._logger,
                    logging.WARNING,
                    "stream.provider.fallback",
                    {"conversation_id": conversation_id},
                )

        if enable_thinking and settings.thinking_enabled:
            for token in build_thinking_summary(user_content).split(" "):
                yield ("thinking", token + " ")
                await asyncio.sleep(settings.token_delay_seconds)

        for token in build_assistant_reply(user_content).split(" "):
            yield ("answer", token + " ")
            await asyncio.sleep(settings.token_delay_seconds)

    async def _build_provider_messages(
        self,
        conversation_id: str,
        user_content: str,
        enable_web_search: bool,
        attachments: tuple["RuntimeAttachment", ...] = (),
    ) -> list[dict[str, str]]:
        history = await self.list_messages(conversation_id)
        provider_messages: list[dict[str, str]] = [
            {"role": "system", "content": "You are a concise and practical assistant."}
        ]
        if enable_web_search:
            context = await self._build_web_search_context(user_content)
            if context:
                provider_messages.append(
                    {
                        "role": "system",
                        "content": (
                            "Web search snippets for this question (may be incomplete/outdated):\n"
                            f"{context}\n"
                            "Use them as references and mention uncertainty when needed."
                        ),
                    }
                )
        attachment_context = self._build_attachment_context(attachments)
        if attachment_context:
            provider_messages.append(
                {
                    "role": "system",
                    "content": (
                        "User uploaded text attachments. Use this material as additional context when relevant:\n"
                        f"{attachment_context}"
                    ),
                }
            )
        for item in history:
            if item.role not in {"user", "assistant"}:
                continue
            if item.content.strip():
                provider_messages.append({"role": item.role, "content": item.content})
        return provider_messages

    def _build_attachment_context(self, attachments: tuple["RuntimeAttachment", ...]) -> str:
        if not attachments:
            return ""
        blocks: list[str] = []
        for item in attachments:
            if not item.content.strip():
                continue
            blocks.append(
                (
                    f"[Attachment] name={item.name} mime={item.mime_type} size={item.size}\n"
                    f"{item.content.strip()}"
                )
            )
        return "\n\n".join(blocks)

    async def _build_web_search_context(self, query: str) -> str:
        context = await search_web_context(query)
        if context:
            log_event(self._logger, logging.INFO, "stream.web_search.context_ready")
        else:
            log_event(self._logger, logging.INFO, "stream.web_search.no_result")
        return context

    async def _append_assistant_text(self, conversation_id: str, message_id: str, delta: str) -> None:
        await db.execute(
            """
            UPDATE messages
            SET content = content || ?, status = 'streaming'
            WHERE id = ? AND conversation_id = ?;
            """,
            (delta, message_id, conversation_id),
        )
        await self._touch_conversation(conversation_id)

    async def _append_assistant_thinking(self, conversation_id: str, message_id: str, delta: str) -> None:
        await db.execute(
            """
            UPDATE messages
            SET thinking = thinking || ?, status = 'streaming'
            WHERE id = ? AND conversation_id = ?;
            """,
            (delta, message_id, conversation_id),
        )
        await self._touch_conversation(conversation_id)

    async def _mark_done(self, conversation_id: str, message_id: str) -> None:
        await db.execute(
            "UPDATE messages SET status = 'done' WHERE id = ? AND conversation_id = ?;",
            (message_id, conversation_id),
        )
        await self._touch_conversation(conversation_id)

    async def _mark_stopped(self, conversation_id: str, message_id: str) -> None:
        await db.execute(
            "UPDATE messages SET status = 'stopped' WHERE id = ? AND conversation_id = ?;",
            (message_id, conversation_id),
        )
        await self._touch_conversation(conversation_id)

    async def _mark_error(self, conversation_id: str, message_id: str) -> None:
        await db.execute(
            "UPDATE messages SET status = 'error' WHERE id = ? AND conversation_id = ?;",
            (message_id, conversation_id),
        )
        await self._touch_conversation(conversation_id)

    async def _touch_conversation(self, conversation_id: str) -> None:
        await db.execute("UPDATE conversations SET updated_at = ? WHERE id = ?;", (utc_now_iso(), conversation_id))

    async def _conversation_exists(self, conversation_id: str) -> bool:
        row = await db.fetchone("SELECT id FROM conversations WHERE id = ?;", (conversation_id,))
        return row is not None

    async def _get_conversation(self, conversation_id: str) -> Optional[ConversationRecord]:
        row = await db.fetchone(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?;",
            (conversation_id,),
        )
        return _conversation_from_row(row) if row else None


chat_service = ChatService()


@dataclass(frozen=True)
class StreamRuntimeOptions:
    enable_web_search: bool = False
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    api_model: Optional[str] = None
    api_reasoning_model: Optional[str] = None
    attachments: tuple["RuntimeAttachment", ...] = ()


@dataclass(frozen=True)
class RuntimeAttachment:
    name: str
    mime_type: str
    content: str
    size: int
