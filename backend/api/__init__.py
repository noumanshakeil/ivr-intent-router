from fastapi import APIRouter
from backend.api import health, ivr, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(ivr.router, prefix="/api", tags=["ivr"])
api_router.include_router(ui.router, tags=["ui"])
