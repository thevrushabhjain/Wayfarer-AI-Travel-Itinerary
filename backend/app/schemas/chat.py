"""Conversation memory schema and chat API contracts."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.travel import TravelItinerary


class TripInfo(BaseModel):
    """Structured trip requirements accumulated across the conversation.

    This is the agent's working memory. Fields are intentionally optional
    since they are filled in progressively as the user answers questions.
    """

    destination: str | None = Field(default=None, description="Primary destination city/country")
    origin_city: str | None = Field(default=None, description="City the traveler departs from, if mentioned")
    start_date: str | None = Field(default=None, description="ISO date YYYY-MM-DD if the user gave exact dates")
    end_date: str | None = Field(default=None, description="ISO date YYYY-MM-DD if the user gave exact dates")
    duration_days: int | None = Field(default=None, description="Trip length in days, derived or stated directly")
    travel_month: str | None = Field(
        default=None, description="Approximate travel window if exact dates are unknown, e.g. 'June 2026'"
    )
    travelers: int | None = Field(default=None, description="Number of travelers")
    budget: float | None = Field(default=None, description="Total trip budget as a number")
    budget_currency: str = Field(default="USD", description="ISO currency code for the budget")
    interests: list[str] | None = Field(
        default=None, description="Traveler interests, e.g. ['art', 'food', 'hiking']. Empty list means asked and none."
    )
    pace: str | None = Field(
        default=None, description="Preferred pace: 'relaxed', 'moderate', 'fast-paced', or 'no preference'"
    )
    hotel_preference: str | None = Field(
        default=None, description="Accommodation preference: 'budget', 'mid-range', 'luxury', or free text"
    )
    dietary_preferences: list[str] | None = Field(
        default=None, description="Dietary restrictions/preferences. Empty list means asked and none."
    )


class ChatRequest(BaseModel):
    session_id: str | None = Field(default=None, description="Existing session id, or null to start a new one")
    message: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime


class SessionHistoryResponse(BaseModel):
    session_id: str
    status: str
    trip_info: TripInfo
    messages: list[MessageOut]
    itinerary: TravelItinerary | None = None
