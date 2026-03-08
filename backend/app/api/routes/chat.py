import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.logging import get_logger, log_event
from app.schemas.chat import (
    AbortRequest,
    CreateConversationResponse,
    ListConversationsResponse,
    ListMessagesResponse,
    MessageDTO,
    SendMessageRequest,
    SimpleResponse,
)
from app.services.chat_service import chat_service


router = APIRouter()
logger = get_logger("chatweb.backend.routes.chat")


@router.get("/conversations", response_model=ListConversationsResponse)
async def list_conversations() -> ListConversationsResponse:
    rows = await chat_service.list_conversations()
    log_event(logger, logging.INFO, "conversations.list", {"count": len(rows)})
    return ListConversationsResponse(
        conversations=[
            {
                "id": item.id,
                "title": item.title,
                "createdAt": item.created_at,
                "updatedAt": item.updated_at,
            }
            for item in rows
        ]
    )


@router.post("/conversations", response_model=CreateConversationResponse)
async def create_conversation() -> CreateConversationResponse:
    item = await chat_service.create_conversation()
    log_event(logger, logging.INFO, "conversations.create", {"conversation_id": item.id})
    return CreateConversationResponse(
        conversation={
            "id": item.id,
            "title": item.title,
            "createdAt": item.created_at,
            "updatedAt": item.updated_at,
        }
    )


@router.get("/conversations/{conversation_id}/messages", response_model=ListMessagesResponse)
async def list_messages(conversation_id: str) -> ListMessagesResponse:
    rows = await chat_service.list_messages(conversation_id)
    log_event(logger, logging.INFO, "messages.list", {"conversation_id": conversation_id, "count": len(rows)})
    return ListMessagesResponse(
        messages=[
            MessageDTO(
                id=item.id,
                conversationId=item.conversation_id,
                role=item.role,
                content=item.content,
                status=item.status,
                createdAt=item.created_at,
            )
            for item in rows
        ]
    )


@router.post("/chat/stream")
async def stream_chat(payload: SendMessageRequest) -> StreamingResponse:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    log_event(
        logger,
        logging.INFO,
        "chat.stream.request",
        {
            "conversation_id": payload.conversation_id,
            "stream_format": payload.stream_format,
            "content_length": len(content),
        },
    )
    await chat_service.append_user_message(payload.conversation_id, content)
    if payload.stream_format == "binary":
        return StreamingResponse(
            chat_service.stream_binary(payload.conversation_id, content),
            media_type="application/octet-stream",
        )
    return StreamingResponse(
        chat_service.stream_json(payload.conversation_id, content),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/chat/abort", response_model=SimpleResponse)
async def abort_chat(payload: AbortRequest) -> SimpleResponse:
    await chat_service.abort(payload.conversation_id)
    log_event(logger, logging.WARNING, "chat.abort", {"conversation_id": payload.conversation_id})
    return SimpleResponse(ok=True)
