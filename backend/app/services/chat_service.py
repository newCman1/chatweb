import asyncio
import json
import logging
from collections import defaultdict
from typing import AsyncGenerator
from uuid import uuid4

import httpx

from app.core.config import settings
from app.core.errors import AppError
from app.core.logging import log_event
from app.models.chat import ConversationRecord, MessageRecord, utc_now_iso
from app.services.ai_client import ai_client


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


class ChatService:
    def __init__(self) -> None:
        self._conversations: dict[str, ConversationRecord] = {}
        self._messages: dict[str, list[MessageRecord]] = defaultdict(list)
        self._active_abort_flags: dict[str, asyncio.Event] = {}
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger("chatweb.backend.services.chat")

    async def list_conversations(self) -> list[ConversationRecord]:
        log_event(self._logger, logging.INFO, "service.list_conversations.start")
        async with self._lock:
            values = list(self._conversations.values())
        ordered = sorted(values, key=lambda x: x.updated_at, reverse=True)
        log_event(self._logger, logging.INFO, "service.list_conversations.done", {"count": len(ordered)})
        return ordered

    async def create_conversation(self) -> ConversationRecord:
        conversation_id = str(uuid4())
        now = utc_now_iso()
        item = ConversationRecord(
            id=conversation_id,
            title="New Chat",
            created_at=now,
            updated_at=now,
        )
        async with self._lock:
            self._conversations[conversation_id] = item
        log_event(self._logger, logging.INFO, "conversation.created", {"conversation_id": conversation_id})
        return item

    async def list_messages(self, conversation_id: str) -> list[MessageRecord]:
        log_event(self._logger, logging.INFO, "service.list_messages.start", {"conversation_id": conversation_id})
        async with self._lock:
            if conversation_id not in self._conversations:
                raise AppError(
                    "CONVERSATION_NOT_FOUND",
                    f"Conversation not found: {conversation_id}",
                    status_code=404,
                    context={"conversation_id": conversation_id},
                )
            rows = list(self._messages.get(conversation_id, []))
        log_event(
            self._logger,
            logging.INFO,
            "service.list_messages.done",
            {"conversation_id": conversation_id, "count": len(rows)},
        )
        return rows

    async def append_user_message(self, conversation_id: str, content: str) -> MessageRecord:
        now = utc_now_iso()
        msg = MessageRecord(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="user",
            content=content,
            status="done",
            created_at=now,
        )
        async with self._lock:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = ConversationRecord(
                    id=conversation_id,
                    title="New Chat",
                    created_at=now,
                    updated_at=now,
                )
            conv = self._conversations[conversation_id]
            if conv.title == "New Chat":
                conv.title = content.strip()[:24] or "New Chat"
            conv.updated_at = now
            self._messages[conversation_id].append(msg)
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
        async with self._lock:
            self._messages[conversation_id].append(msg)
        log_event(
            self._logger,
            logging.INFO,
            "service.assistant_placeholder.created",
            {"conversation_id": conversation_id, "message_id": msg.id},
        )
        return msg

    async def abort(self, conversation_id: str) -> None:
        if conversation_id not in self._conversations:
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
        self, conversation_id: str, user_content: str, enable_thinking: bool
    ) -> AsyncGenerator[str, None]:
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
            },
        )

        try:
            async for event_type, delta in self._stream_with_provider_fallback(
                conversation_id, user_content, enable_thinking
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
        self, conversation_id: str, user_content: str, enable_thinking: bool
    ) -> AsyncGenerator[bytes, None]:
        abort_flag = asyncio.Event()
        self._active_abort_flags[conversation_id] = abort_flag
        assistant = await self.create_assistant_message_placeholder(conversation_id)
        chunks = build_assistant_reply(user_content).split(" ")
        log_event(
            self._logger,
            logging.INFO,
            "stream.binary.start",
            {
                "conversation_id": conversation_id,
                "message_id": assistant.id,
                "enable_thinking": enable_thinking,
            },
        )
        try:
            for chunk in chunks:
                if abort_flag.is_set():
                    await self._mark_stopped(conversation_id, assistant.id)
                    log_event(
                        self._logger,
                        logging.WARNING,
                        "stream.binary.stopped",
                        {"conversation_id": conversation_id, "message_id": assistant.id},
                    )
                    return
                content = (chunk + " ").encode("utf-8")
                await self._append_assistant_text(conversation_id, assistant.id, chunk + " ")
                yield content
                await asyncio.sleep(settings.token_delay_seconds)
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
        self, conversation_id: str, user_content: str, enable_thinking: bool
    ) -> AsyncGenerator[tuple[str, str], None]:
        if ai_client.enabled:
            history = await self._build_provider_messages(conversation_id)
            try:
                async for event_type, delta in ai_client.stream_chat(history, enable_thinking=enable_thinking):
                    if event_type == "thinking" and not enable_thinking:
                        continue
                    yield (event_type, delta)
                return
            except httpx.HTTPError as error:
                log_event(
                    self._logger,
                    logging.ERROR,
                    "stream.provider.failed",
                    {"conversation_id": conversation_id, "error": str(error)},
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

    async def _build_provider_messages(self, conversation_id: str) -> list[dict[str, str]]:
        async with self._lock:
            history = list(self._messages.get(conversation_id, []))
        provider_messages: list[dict[str, str]] = [
            {"role": "system", "content": "You are a concise and practical assistant."}
        ]
        for item in history:
            if item.role not in {"user", "assistant"}:
                continue
            if item.content.strip():
                provider_messages.append({"role": item.role, "content": item.content})
        return provider_messages

    async def _append_assistant_text(self, conversation_id: str, message_id: str, delta: str) -> None:
        async with self._lock:
            messages = self._messages.get(conversation_id, [])
            target = next((msg for msg in messages if msg.id == message_id), None)
            if target:
                target.content += delta
                target.status = "streaming"
                self._conversations[conversation_id].updated_at = utc_now_iso()

    async def _append_assistant_thinking(self, conversation_id: str, message_id: str, delta: str) -> None:
        async with self._lock:
            messages = self._messages.get(conversation_id, [])
            target = next((msg for msg in messages if msg.id == message_id), None)
            if target:
                target.thinking += delta
                target.status = "streaming"
                self._conversations[conversation_id].updated_at = utc_now_iso()

    async def _mark_done(self, conversation_id: str, message_id: str) -> None:
        async with self._lock:
            for msg in self._messages.get(conversation_id, []):
                if msg.id == message_id:
                    msg.status = "done"
                    break

    async def _mark_stopped(self, conversation_id: str, message_id: str) -> None:
        async with self._lock:
            for msg in self._messages.get(conversation_id, []):
                if msg.id == message_id:
                    msg.status = "stopped"
                    break

    async def _mark_error(self, conversation_id: str, message_id: str) -> None:
        async with self._lock:
            for msg in self._messages.get(conversation_id, []):
                if msg.id == message_id:
                    msg.status = "error"
                    break


chat_service = ChatService()
