"""Prompts for the Validator/Reflection agent."""

from app.schemas.chat import TripInfo
from app.schemas.travel import TravelItinerary

VALIDATOR_SYSTEM_PROMPT = """You are the Validator module of a travel planning agent, performing \
a final reflection pass. You are given a generated itinerary and a list of specific issues found \
by automated checks. Fix ONLY those issues while preserving everything else that is already \
correct and good. Output the complete, corrected structured JSON matching the given schema \
exactly."""


def build_repair_prompt(trip_info: TripInfo, itinerary: TravelItinerary, issues: list[str]) -> str:
    issues_text = "\n".join(f"- {issue}" for issue in issues)
    return f"""Trip requirements: {trip_info.destination}, {trip_info.duration_days} days, \
{trip_info.travelers} traveler(s), budget {trip_info.budget} {trip_info.budget_currency}.

Current itinerary as JSON:
{itinerary.model_dump_json()}

Automated validation found these issues that MUST be fixed:
{issues_text}

Return the complete, corrected itinerary as structured JSON."""
