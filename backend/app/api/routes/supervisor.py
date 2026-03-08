import logging

from fastapi import APIRouter

from app.core.logging import get_logger, log_event
from app.schemas.supervisor import SupervisorRunRequest, SupervisorRunResponse
from app.services.supervisor_service import supervisor_service, supervisor_to_dict


router = APIRouter()
logger = get_logger("chatweb.backend.routes.supervisor")


@router.post("/supervisor/run", response_model=SupervisorRunResponse)
async def run_supervisor(payload: SupervisorRunRequest) -> SupervisorRunResponse:
    log_event(
        logger,
        logging.INFO,
        "supervisor.run.request",
        {
            "conversation_id": payload.conversation_id,
            "objective_length": len(payload.objective.strip()),
            "max_tasks": payload.max_tasks,
            "max_retries": payload.max_retries,
        },
    )
    run = await supervisor_service.run(payload)
    log_event(logger, logging.INFO, "supervisor.run.response", {"run_id": run.id, "status": run.status})
    return SupervisorRunResponse(run=supervisor_to_dict(run))


@router.get("/supervisor/run/{run_id}", response_model=SupervisorRunResponse)
async def get_supervisor_run(run_id: str) -> SupervisorRunResponse:
    log_event(logger, logging.INFO, "supervisor.get.start", {"run_id": run_id})
    run = supervisor_service.get_run(run_id)
    log_event(logger, logging.INFO, "supervisor.get.done", {"run_id": run_id, "status": run.status})
    return SupervisorRunResponse(run=supervisor_to_dict(run))
