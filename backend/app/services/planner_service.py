"""Planner agent: produces a high-level day-by-day skeleton before detailed execution."""

from app.llm.base import LLMProvider
from app.prompts.planning_prompts import PLANNER_SYSTEM_PROMPT, build_skeleton_prompt
from app.schemas.chat import TripInfo
from app.schemas.travel import PlanSkeleton


class PlannerService:
    """Collaborating agent responsible for multi-step planning BEFORE execution."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def create_skeleton(self, trip_info: TripInfo) -> PlanSkeleton:
        prompt = build_skeleton_prompt(trip_info)
        return await self.provider.generate_structured(
            prompt=prompt, schema=PlanSkeleton, system_instruction=PLANNER_SYSTEM_PROMPT
        )
