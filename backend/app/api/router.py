from fastapi import APIRouter

from .routes import analytics, auth, export, finance, health, learning, productivity, admin

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(finance.router)
api_router.include_router(productivity.router)
api_router.include_router(learning.router)
api_router.include_router(analytics.router)
api_router.include_router(export.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
