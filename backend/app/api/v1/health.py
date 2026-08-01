"""
Health check endpoint.

Purpose: lets the frontend, Docker healthchecks, and (later) Render's
deploy monitor verify the backend is alive without touching any business
logic. This is the first thing we test in Milestone 1, and it stays useful
for the life of the project.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="strix-backend")
