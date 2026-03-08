from fastapi import APIRouter

from app.api.routes.chat import router as chat_router
from app.api.routes.supervisor import router as supervisor_router


api_router = APIRouter()
api_router.include_router(chat_router, prefix="", tags=["chat"])
api_router.include_router(supervisor_router, prefix="", tags=["supervisor"])
