"""Rules describing which TripInfo fields are required and in what order
the agent should ask about them. This drives the "ask only what's missing,
one field at a time" behaviour.
"""

from dataclasses import dataclass

from app.schemas.chat import TripInfo


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    description: str


FIELD_ORDER: list[FieldSpec] = [
    FieldSpec("destination", "destination", "where the traveler wants to go"),
    FieldSpec("trip_dates", "travel dates or trip length", "when they're traveling and for how long"),
    FieldSpec("travelers", "number of travelers", "how many people are traveling"),
    FieldSpec("budget", "budget", "their approximate total budget for the trip"),
    FieldSpec("interests", "interests", "what kind of experiences they enjoy (e.g. food, art, hiking, nightlife)"),
    FieldSpec("pace", "travel pace", "whether they prefer a relaxed, moderate, or fast-paced schedule"),
    FieldSpec("hotel_preference", "accommodation preference", "budget, mid-range, or luxury accommodation"),
    FieldSpec("dietary_preferences", "dietary preferences", "any dietary restrictions or preferences"),
]

_FIELD_BY_KEY = {spec.key: spec for spec in FIELD_ORDER}


def _is_present(field_key: str, trip_info: TripInfo) -> bool:
    if field_key == "destination":
        return bool(trip_info.destination)
    if field_key == "trip_dates":
        has_explicit_dates = bool(trip_info.start_date and trip_info.end_date)
        return has_explicit_dates or bool(trip_info.duration_days)
    if field_key == "travelers":
        return trip_info.travelers is not None and trip_info.travelers > 0
    if field_key == "budget":
        return trip_info.budget is not None and trip_info.budget > 0
    if field_key == "interests":
        return trip_info.interests is not None
    if field_key == "pace":
        return bool(trip_info.pace)
    if field_key == "hotel_preference":
        return bool(trip_info.hotel_preference)
    if field_key == "dietary_preferences":
        return trip_info.dietary_preferences is not None
    return False


def get_missing_fields(trip_info: TripInfo) -> list[str]:
    """Return the ordered list of field keys still missing from trip_info."""
    return [spec.key for spec in FIELD_ORDER if not _is_present(spec.key, trip_info)]


def is_ready(trip_info: TripInfo) -> bool:
    return len(get_missing_fields(trip_info)) == 0


def get_field_spec(field_key: str) -> FieldSpec:
    return _FIELD_BY_KEY[field_key]


def known_fields_summary(trip_info: TripInfo) -> str:
    """A short, human-readable summary of what's already known, used to keep
    prompts (and the clarifying questions they produce) context-aware."""
    parts: list[str] = []
    if trip_info.destination:
        parts.append(f"destination: {trip_info.destination}")
    if trip_info.origin_city:
        parts.append(f"origin: {trip_info.origin_city}")
    if trip_info.start_date and trip_info.end_date:
        parts.append(f"dates: {trip_info.start_date} to {trip_info.end_date}")
    elif trip_info.duration_days:
        parts.append(f"duration: {trip_info.duration_days} days")
    if trip_info.travel_month:
        parts.append(f"travel window: {trip_info.travel_month}")
    if trip_info.travelers:
        parts.append(f"travelers: {trip_info.travelers}")
    if trip_info.budget:
        parts.append(f"budget: {trip_info.budget} {trip_info.budget_currency}")
    if trip_info.interests:
        parts.append(f"interests: {', '.join(trip_info.interests)}")
    if trip_info.pace:
        parts.append(f"pace: {trip_info.pace}")
    if trip_info.hotel_preference:
        parts.append(f"hotel preference: {trip_info.hotel_preference}")
    if trip_info.dietary_preferences:
        parts.append(f"dietary preferences: {', '.join(trip_info.dietary_preferences)}")
    return "; ".join(parts) if parts else "nothing yet"
