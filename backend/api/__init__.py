from fastapi import APIRouter

from backend.api.health import router as health_router
from backend.api.auth import router as auth_router
from backend.api.history import router as history_router
from backend.api.analyze import router as analyze_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(history_router)
api_router.include_router(analyze_router)
