import logging

from fastapi import APIRouter
from fastapi import Query

from app.core.logging import get_logger, log_event
from app.schemas.supervisor import SupervisorRunListResponse, SupervisorRunRequest, SupervisorRunResponse
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
            "primary_runtime_override": bool(
                payload.primary_api_key
                or payload.primary_api_base_url
                or payload.primary_api_model
                or payload.primary_api_reasoning_model
            ),
            "worker_runtime_override": bool(
                payload.worker_api_key
                or payload.worker_api_base_url
                or payload.worker_api_model
                or payload.worker_api_reasoning_model
            ),
        },
    )
    run = await supervisor_service.run(payload)
    log_event(logger, logging.INFO, "supervisor.run.response", {"run_id": run.id, "status": run.status})
    return SupervisorRunResponse(run=supervisor_to_dict(run))


@router.post("/supervisor/run/start", response_model=SupervisorRunResponse)
async def start_supervisor(payload: SupervisorRunRequest) -> SupervisorRunResponse:
    log_event(
        logger,
        logging.INFO,
        "supervisor.start.request",
        {
            "conversation_id": payload.conversation_id,
            "objective_length": len(payload.objective.strip()),
            "max_tasks": payload.max_tasks,
            "max_retries": payload.max_retries,
            "primary_runtime_override": bool(
                payload.primary_api_key
                or payload.primary_api_base_url
                or payload.primary_api_model
                or payload.primary_api_reasoning_model
            ),
            "worker_runtime_override": bool(
                payload.worker_api_key
                or payload.worker_api_base_url
                or payload.worker_api_model
                or payload.worker_api_reasoning_model
            ),
        },
    )
    run = await supervisor_service.start(payload)
    log_event(logger, logging.INFO, "supervisor.start.response", {"run_id": run.id, "status": run.status})
    return SupervisorRunResponse(run=supervisor_to_dict(run))


@router.post("/supervisor/run/{run_id}/abort", response_model=SupervisorRunResponse)
async def abort_supervisor(run_id: str) -> SupervisorRunResponse:
    log_event(logger, logging.WARNING, "supervisor.abort.request", {"run_id": run_id})
    run = await supervisor_service.abort(run_id)
    log_event(logger, logging.WARNING, "supervisor.abort.response", {"run_id": run.id, "status": run.status})
    return SupervisorRunResponse(run=supervisor_to_dict(run))


@router.get("/supervisor/run/{run_id}", response_model=SupervisorRunResponse)
async def get_supervisor_run(run_id: str) -> SupervisorRunResponse:
    log_event(logger, logging.INFO, "supervisor.get.start", {"run_id": run_id})
    run = await supervisor_service.get_run(run_id)
    log_event(logger, logging.INFO, "supervisor.get.done", {"run_id": run_id, "status": run.status})
    return SupervisorRunResponse(run=supervisor_to_dict(run))


@router.get("/supervisor/runs", response_model=SupervisorRunListResponse)
async def list_supervisor_runs(conversation_id: str = Query(alias="conversationId")) -> SupervisorRunListResponse:
    log_event(logger, logging.INFO, "supervisor.list.start", {"conversation_id": conversation_id})
    runs = await supervisor_service.list_runs(conversation_id)
    log_event(logger, logging.INFO, "supervisor.list.done", {"conversation_id": conversation_id, "count": len(runs)})
    return SupervisorRunListResponse(runs=[supervisor_to_dict(item) for item in runs])
