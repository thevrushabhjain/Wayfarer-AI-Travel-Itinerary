"""Read-only itinerary retrieval endpoint (used for direct dashboard reloads)."""

from fastapi import APIRouter, HTTPException

from app.core.database import AsyncSessionLocal
from app.schemas.travel import TravelItinerary
from app.services import conversation_service

router = APIRouter()


@router.get("/{session_id}", response_model=TravelItinerary)
async def get_itinerary(session_id: str):
    async with AsyncSessionLocal() as db:
        itinerary = await conversation_service.get_latest_itinerary(db, session_id)
        if itinerary is None:
            raise HTTPException(status_code=404, detail="No itinerary found for this session")
        return itinerary
