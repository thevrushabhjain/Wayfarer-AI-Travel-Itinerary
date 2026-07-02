"""Prompts for the Planner and Recommendation (itinerary architect) agents."""

from app.schemas.chat import TripInfo
from app.schemas.travel import PlanSkeleton, TravelItinerary

PLANNER_SYSTEM_PROMPT = """You are the Planner module of a travel planning agent. Before any \
detailed itinerary is written, you produce a high-level, day-by-day STRATEGY: a short theme and \
geographic focus for each day, sequenced so travel logistics make sense (e.g. group nearby \
sights, save far day-trips for one day, ease into the trip on arrival day). You never write \
detailed activity lists here - only the skeleton/strategy. Output structured JSON only."""

RECOMMENDATION_SYSTEM_PROMPT = """You are the Itinerary Architect module of a travel planning \
agent. Given a trip's requirements and an approved day-by-day skeleton plan, you produce the \
FULL, detailed, realistic itinerary: specific activities with times and costs, hotel \
recommendations, transportation guidance, food and local experiences, a packing checklist, and \
practical travel tips. Be specific and realistic (real neighborhoods, realistic prices in the \
requested currency, sensible timing with buffer for meals/rest). Tailor every section to the \
traveler's stated interests, pace, budget, hotel tier, and dietary preferences. Output structured \
JSON only, matching the given schema exactly."""

REVISION_SYSTEM_PROMPT = """You are the Itinerary Architect module of a travel planning agent, \
now REVISING an existing itinerary based on the traveler's feedback. Keep everything that isn't \
affected by the feedback unchanged. Apply the requested change precisely and keep the itinerary \
internally consistent (day numbering, budget totals, dates). Output the complete, updated \
structured JSON matching the given schema exactly."""


def build_skeleton_prompt(trip_info: TripInfo) -> str:
    return f"""Create a day-by-day planning skeleton for this trip:

Destination: {trip_info.destination}
Duration: {trip_info.duration_days} days
Dates: {trip_info.start_date or 'TBD'} to {trip_info.end_date or 'TBD'} (travel window: {trip_info.travel_month or 'flexible'})
Travelers: {trip_info.travelers}
Budget: {trip_info.budget} {trip_info.budget_currency}
Interests: {', '.join(trip_info.interests) if trip_info.interests else 'general sightseeing'}
Pace: {trip_info.pace or 'moderate'}
Hotel preference: {trip_info.hotel_preference or 'no preference'}
Dietary preferences: {', '.join(trip_info.dietary_preferences) if trip_info.dietary_preferences else 'none'}

Produce exactly {trip_info.duration_days} day entries, sequenced logically."""


def build_itinerary_prompt(trip_info: TripInfo, skeleton: PlanSkeleton) -> str:
    skeleton_lines = "\n".join(
        f"Day {d.day_number}: {d.theme} (focus: {d.location_focus}) - {d.notes}" for d in skeleton.days
    )
    return f"""Trip requirements:
Destination: {trip_info.destination}
Origin: {trip_info.origin_city or 'not specified'}
Duration: {trip_info.duration_days} days
Dates: {trip_info.start_date or 'TBD'} to {trip_info.end_date or 'TBD'} (travel window: {trip_info.travel_month or 'flexible'})
Travelers: {trip_info.travelers}
Budget: {trip_info.budget} {trip_info.budget_currency} total for the whole trip
Interests: {', '.join(trip_info.interests) if trip_info.interests else 'general sightseeing'}
Pace: {trip_info.pace or 'moderate'}
Hotel preference: {trip_info.hotel_preference or 'no preference'}
Dietary preferences: {', '.join(trip_info.dietary_preferences) if trip_info.dietary_preferences else 'none'}

Approved planning skeleton to follow (overall strategy: {skeleton.overall_strategy}):
{skeleton_lines}

Now produce the full, detailed structured itinerary. Each day must have at least 3 activities. \
Budget breakdown items must sum to approximately the total budget. Include {trip_info.travelers} \
traveler(s) in the overview."""


def build_revision_prompt(trip_info: TripInfo, existing_itinerary: TravelItinerary, revision_request: str) -> str:
    return f"""Here is the traveler's current itinerary as JSON:
{existing_itinerary.model_dump_json()}

The traveler's original requirements: destination {trip_info.destination}, {trip_info.duration_days} \
days, {trip_info.travelers} traveler(s), budget {trip_info.budget} {trip_info.budget_currency}.

The traveler just asked for this change:
"{revision_request}"

Apply this change and return the complete, updated itinerary as structured JSON."""
