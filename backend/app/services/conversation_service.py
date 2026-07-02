"""Conversation memory: persistence helpers for sessions, messages and itineraries."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import ConversationSession, ItineraryRecord, Message
from app.schemas.chat import TripInfo
from app.schemas.travel import TravelItinerary

MAX_HISTORY_MESSAGES = 20


async def get_or_create_session(db: AsyncSession, session_id: str | None) -> ConversationSession:
    if session_id:
        result = await db.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            return session

    new_session = ConversationSession(id=session_id or str(uuid.uuid4()), status="collecting", trip_info={})
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


async def save_message(db: AsyncSession, session_id: str, role: str, content: str) -> None:
    db.add(Message(session_id=session_id, role=role, content=content))
    await db.commit()


async def get_recent_messages(db: AsyncSession, session_id: str, limit: int = MAX_HISTORY_MESSAGES) -> list[Message]:
    result = await db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.id.desc()).limit(limit)
    )
    return list(reversed(result.scalars().all()))


def format_conversation_text(messages: list[Message]) -> str:
    if not messages:
        return "(no prior conversation)"
    lines = [f"{'Traveler' if m.role == 'user' else 'Assistant'}: {m.content}" for m in messages]
    return "\n".join(lines)


async def update_trip_info(db: AsyncSession, session: ConversationSession, trip_info: TripInfo) -> None:
    session.trip_info = trip_info.model_dump()
    await db.commit()


async def set_status(db: AsyncSession, session: ConversationSession, status: str) -> None:
    session.status = status
    await db.commit()


async def save_itinerary(db: AsyncSession, session_id: str, itinerary: TravelItinerary, is_valid: bool) -> None:
    result = await db.execute(
        select(ItineraryRecord).where(ItineraryRecord.session_id == session_id).order_by(ItineraryRecord.version.desc())
    )
    latest = result.scalars().first()
    next_version = (latest.version + 1) if latest else 1
    db.add(
        ItineraryRecord(
            session_id=session_id,
            version=next_version,
            data=itinerary.model_dump(mode="json"),
            is_valid=is_valid,
        )
    )
    await db.commit()


async def get_latest_itinerary(db: AsyncSession, session_id: str) -> TravelItinerary | None:
    result = await db.execute(
        select(ItineraryRecord).where(ItineraryRecord.session_id == session_id).order_by(ItineraryRecord.version.desc())
    )
    record = result.scalars().first()
    if not record:
        return None
    return TravelItinerary.model_validate(record.data)
