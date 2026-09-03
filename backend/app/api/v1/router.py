from fastapi import APIRouter

from backend.app.api.v1.endpoints.recommendations import (
    router as recommendations_router,
)
from backend.app.api.v1.endpoints.resume import router as resume_router

api_v1_router = APIRouter()

api_v1_router.include_router(resume_router)
api_v1_router.include_router(recommendations_router)
