from __future__ import annotations

from fastapi import APIRouter

from app.api.endpoints.process import router as process_router
from app.api.endpoints.system import router as system_router

api_router = APIRouter()
api_router.include_router(process_router)
api_router.include_router(system_router)

__all__ = ["api_router"]
