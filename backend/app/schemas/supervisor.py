from typing import Optional

from pydantic import BaseModel, Field


class SupervisorRunRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    objective: str
    plan: Optional[str] = None
    max_tasks: int = Field(default=4, alias="maxTasks")
    max_retries: int = Field(default=1, alias="maxRetries")


class SupervisorTaskDTO(BaseModel):
    index: int
    title: str
    worker_output: str = Field(alias="workerOutput")
    review_verdict: str = Field(alias="reviewVerdict")
    review_feedback: str = Field(alias="reviewFeedback")
    status: str
    retries: int


class SupervisorRunDTO(BaseModel):
    id: str
    conversation_id: str = Field(alias="conversationId")
    objective: str
    plan_text: str = Field(alias="planText")
    primary_name: str = Field(alias="primaryName")
    worker_name: str = Field(alias="workerName")
    status: str
    summary: str
    created_at: str = Field(alias="createdAt")
    tasks: list[SupervisorTaskDTO]


class SupervisorRunResponse(BaseModel):
    run: SupervisorRunDTO


class SupervisorRunListResponse(BaseModel):
    runs: list[SupervisorRunDTO]
