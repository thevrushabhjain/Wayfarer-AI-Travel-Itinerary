"""Conversational chat endpoint: streams agent progress + the final structured result."""

import json

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from starlette.responses import StreamingResponse

from app.core.database import AsyncSessionLocal
from app.core.logging_config import get_logger
from app.llm.factory import get_llm_provider
from app.models.conversation import ConversationSession
from app.schemas.chat import ChatRequest, MessageOut, SessionHistoryResponse, TripInfo
from app.services import conversation_service
from app.services.orchestrator_service import OrchestratorService

logger = get_logger(__name__)
router = APIRouter()


def _sse_event(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Main conversational endpoint. Streams Server-Sent Events:

    - `progress`  : {"stage": "understanding" | "planning" | "finalizing"}
    - `result`    : {"type": "question" | "itinerary", ...}
    - `error`     : {"detail": str}
    """

    async def event_generator():
        async with AsyncSessionLocal() as db:
            session = await conversation_service.get_or_create_session(db, request.session_id)
            try:
                provider = get_llm_provider()
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to initialize LLM provider: %s", exc)
                yield _sse_event("error", {"detail": str(exc)})
                return

            orchestrator = OrchestratorService(provider)
            async for event in orchestrator.process_turn(db, session, request.message):
                event_type = event.pop("event")
                yield _sse_event(event_type, event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/{session_id}/history", response_model=SessionHistoryResponse)
async def get_history(session_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ConversationSession).where(ConversationSession.id == session_id))
        session = result.scalar_one_or_none()
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")

        messages = await conversation_service.get_recent_messages(db, session_id, limit=100)
        itinerary = await conversation_service.get_latest_itinerary(db, session_id)

        return SessionHistoryResponse(
            session_id=session.id,
            status=session.status,
            trip_info=TripInfo.model_validate(session.trip_info),
            messages=[MessageOut(role=m.role, content=m.content, created_at=m.created_at) for m in messages],
            itinerary=itinerary,
        )
