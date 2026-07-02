"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("")
async def health():
    return {"status": "ok", "llm_provider": settings.llm_provider}
