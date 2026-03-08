from dataclasses import dataclass, field
from typing import Literal


SupervisorRunStatus = Literal["running", "completed", "failed", "aborted"]
SupervisorTaskStatus = Literal["running", "completed", "failed", "aborted"]


@dataclass
class SupervisorTaskRecord:
    index: int
    title: str
    worker_output: str
    review_verdict: str
    review_feedback: str
    status: SupervisorTaskStatus
    retries: int = 0


@dataclass
class SupervisorRunRecord:
    id: str
    conversation_id: str
    objective: str
    plan_text: str
    primary_name: str
    worker_name: str
    status: SupervisorRunStatus
    summary: str
    created_at: str
    tasks: list[SupervisorTaskRecord] = field(default_factory=list)
