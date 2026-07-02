"""Validator / Reflection agent: deterministic checks plus a single LLM repair pass."""

from app.core.logging_config import get_logger
from app.llm.base import LLMProvider
from app.prompts.validation_prompts import VALIDATOR_SYSTEM_PROMPT, build_repair_prompt
from app.schemas.chat import TripInfo
from app.schemas.travel import TravelItinerary

logger = get_logger(__name__)

_BUDGET_TOLERANCE_PCT = 15.0


class ValidatorService:
    """Collaborating agent responsible for the final validation/reflection step."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def run_checks(self, trip_info: TripInfo, itinerary: TravelItinerary) -> list[str]:
        issues: list[str] = []

        expected_days = trip_info.duration_days or len(itinerary.day_plans)
        if len(itinerary.day_plans) != expected_days:
            issues.append(
                f"The itinerary has {len(itinerary.day_plans)} day(s) but the trip is {expected_days} day(s) long."
            )

        for day in itinerary.day_plans:
            if len(day.activities) < 2:
                issues.append(f"Day {day.day_number} has too few activities ({len(day.activities)}); needs at least 2-3.")

        if trip_info.budget:
            budget_sum = sum(item.amount for item in itinerary.budget_breakdown.items)
            deviation_pct = abs(budget_sum - trip_info.budget) / trip_info.budget * 100
            if deviation_pct > _BUDGET_TOLERANCE_PCT:
                issues.append(
                    f"Budget breakdown sums to {budget_sum:.0f} but the total budget is "
                    f"{trip_info.budget:.0f}; adjust category amounts so they sum close to the total."
                )

        if not itinerary.hotels:
            issues.append("No hotel recommendations were provided; add at least 2.")
        if not itinerary.transportation:
            issues.append("No transportation options were provided; add at least 2.")
        if not itinerary.food_experiences:
            issues.append("No food/local experiences were provided; add at least 4.")
        if not itinerary.packing_checklist:
            issues.append("No packing checklist was provided; add at least 8 items.")
        if not itinerary.travel_tips:
            issues.append("No travel tips were provided; add at least 5.")

        if trip_info.travelers and itinerary.overview.travelers != trip_info.travelers:
            issues.append(f"Overview lists {itinerary.overview.travelers} traveler(s) but trip has {trip_info.travelers}.")

        return issues

    async def validate_and_repair(
        self, trip_info: TripInfo, itinerary: TravelItinerary
    ) -> tuple[TravelItinerary, bool, list[str]]:
        issues = self.run_checks(trip_info, itinerary)
        if not issues:
            return itinerary, True, []

        logger.info("Validator found %d issue(s), attempting one repair pass: %s", len(issues), issues)
        prompt = build_repair_prompt(trip_info, itinerary, issues)
        try:
            repaired = await self.provider.generate_structured(
                prompt=prompt, schema=TravelItinerary, system_instruction=VALIDATOR_SYSTEM_PROMPT
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Repair pass failed (%s); returning original itinerary with known issues.", exc)
            return itinerary, False, issues

        remaining_issues = self.run_checks(trip_info, repaired)
        return repaired, len(remaining_issues) == 0, remaining_issues
