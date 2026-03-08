from dataclasses import dataclass
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


@dataclass
class ConversationRecord:
    id: str
    title: str
    created_at: str
    updated_at: str


@dataclass
class MessageRecord:
    id: str
    conversation_id: str
    role: str
    content: str
    status: str
    created_at: str
    thinking: str = ""
