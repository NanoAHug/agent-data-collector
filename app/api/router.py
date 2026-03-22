from fastapi import APIRouter

from app.api.endpoints import collect, conversations, stats

api_router = APIRouter(prefix="/api")

api_router.include_router(collect.router)
api_router.include_router(conversations.router)
api_router.include_router(stats.router)
