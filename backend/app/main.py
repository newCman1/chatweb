import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError, error_response
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


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    log_event(
        logger,
        logging.INFO,
        "request.start",
        {"request_id": request_id, "method": request.method, "path": request.url.path},
    )
    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    log_event(
        logger,
        logging.INFO,
        "request.done",
        {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    request_id = getattr(request.state, "request_id", "unknown")
    log_event(
        logger,
        logging.ERROR,
        "request.app_error",
        {
            "request_id": request_id,
            "path": request.url.path,
            "code": exc.code,
            "message": exc.message,
            "status_code": exc.status_code,
            "context": exc.context,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.code, exc.message, request_id),
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    log_event(
        logger,
        logging.ERROR,
        "request.validation_error",
        {
            "request_id": request_id,
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content=error_response("REQUEST_VALIDATION_ERROR", "Request validation failed.", request_id),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    detail = exc.detail if isinstance(exc.detail, str) else "HTTP request failed."
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        429: "TOO_MANY_REQUESTS",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    log_event(
        logger,
        logging.ERROR,
        "request.http_error",
        {
            "request_id": request_id,
            "path": request.url.path,
            "status_code": exc.status_code,
            "code": code,
            "detail": detail,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code, detail, request_id),
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    log_event(
        logger,
        logging.ERROR,
        "request.unhandled_error",
        {
            "request_id": request_id,
            "path": request.url.path,
            "error": str(exc),
        },
    )
    return JSONResponse(
        status_code=500,
        content=error_response("INTERNAL_SERVER_ERROR", "Internal server error.", request_id),
    )


app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    log_event(logger, logging.INFO, "health.ok", {"env": settings.app_env})
    return {"status": "ok"}
