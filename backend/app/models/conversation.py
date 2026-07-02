"""ORM models for conversation memory and generated itineraries."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ConversationSession(Base):
    """A single conversation/trip-planning session (the agent's memory)."""

    __tablename__ = "conversation_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="collecting", nullable=False)
    trip_info: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="Message.id"
    )
    itineraries: Mapped[list["ItineraryRecord"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ItineraryRecord.version"
    )


class Message(Base):
    """A single chat turn, either from the user or the assistant."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    session: Mapped[ConversationSession] = relationship(back_populates="messages")


class ItineraryRecord(Base):
    """A generated (or revised) structured itinerary tied to a session."""

    __tablename__ = "itinerary_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversation_sessions.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_valid: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    session: Mapped[ConversationSession] = relationship(back_populates="itineraries")
