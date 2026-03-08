from typing import Optional

from pydantic import BaseModel, Field


class SupervisorRunRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    objective: str
    plan: Optional[str] = None
    max_tasks: int = Field(default=4, alias="maxTasks")
    max_retries: int = Field(default=1, alias="maxRetries")
    primary_api_key: Optional[str] = Field(default=None, alias="primaryApiKey")
    primary_api_base_url: Optional[str] = Field(default=None, alias="primaryApiBaseUrl")
    primary_api_model: Optional[str] = Field(default=None, alias="primaryApiModel")
    primary_api_reasoning_model: Optional[str] = Field(default=None, alias="primaryApiReasoningModel")
    worker_api_key: Optional[str] = Field(default=None, alias="workerApiKey")
    worker_api_base_url: Optional[str] = Field(default=None, alias="workerApiBaseUrl")
    worker_api_model: Optional[str] = Field(default=None, alias="workerApiModel")
    worker_api_reasoning_model: Optional[str] = Field(default=None, alias="workerApiReasoningModel")


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
