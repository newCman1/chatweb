from typing import Literal
from typing import Optional

from pydantic import BaseModel, Field


MessageRole = Literal["user", "assistant", "system"]
MessageStatus = Literal["streaming", "done", "stopped", "error"]
StreamFormat = Literal["json", "binary"]


class ConversationDTO(BaseModel):
    id: str
    title: str
    created_at: str = Field(alias="createdAt")
    updated_at: str = Field(alias="updatedAt")


class MessageDTO(BaseModel):
    id: str
    conversation_id: str = Field(alias="conversationId")
    role: MessageRole
    content: str
    thinking: Optional[str] = None
    status: MessageStatus
    created_at: str = Field(alias="createdAt")


class CreateConversationResponse(BaseModel):
    conversation: ConversationDTO


class ListConversationsResponse(BaseModel):
    conversations: list[ConversationDTO]


class ListMessagesResponse(BaseModel):
    messages: list[MessageDTO]


class SendMessageRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    content: str
    enable_thinking: bool = Field(default=False, alias="enableThinking")
    stream_format: StreamFormat = Field(default="json", alias="streamFormat")


class AbortRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")


class SimpleResponse(BaseModel):
    ok: bool
