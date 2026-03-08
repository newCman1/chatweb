import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import get_logger, log_event, setup_logging


setup_logging(settings.log_level)
logger = get_logger("chatweb.backend.main")

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    log_event(logger, logging.INFO, "health.ok", {"env": settings.app_env})
    return {"status": "ok"}
