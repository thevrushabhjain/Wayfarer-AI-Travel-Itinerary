"""Recommendation / Itinerary Architect agent: expands the skeleton into the full itinerary."""

from app.llm.base import LLMProvider
from app.prompts.planning_prompts import (
    RECOMMENDATION_SYSTEM_PROMPT,
    REVISION_SYSTEM_PROMPT,
    build_itinerary_prompt,
    build_revision_prompt,
)
from app.schemas.chat import TripInfo
from app.schemas.travel import PlanSkeleton, TravelItinerary


class RecommendationService:
    """Collaborating agent responsible for the detailed itinerary and its revisions."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def build_itinerary(self, trip_info: TripInfo, skeleton: PlanSkeleton) -> TravelItinerary:
        prompt = build_itinerary_prompt(trip_info, skeleton)
        return await self.provider.generate_structured(
            prompt=prompt, schema=TravelItinerary, system_instruction=RECOMMENDATION_SYSTEM_PROMPT
        )

    async def revise_itinerary(
        self, trip_info: TripInfo, existing_itinerary: TravelItinerary, revision_request: str
    ) -> TravelItinerary:
        prompt = build_revision_prompt(trip_info, existing_itinerary, revision_request)
        return await self.provider.generate_structured(
            prompt=prompt, schema=TravelItinerary, system_instruction=REVISION_SYSTEM_PROMPT
        )
