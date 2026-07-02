"""Clarifier agent: asks exactly one natural, context-aware follow-up question."""

from app.llm.base import LLMProvider
from app.prompts.clarifier_prompts import CLARIFIER_SYSTEM_PROMPT, build_clarifying_question_prompt
from app.schemas.chat import TripInfo
from app.utils.field_rules import get_field_spec


class ClarifierService:
    """Collaborating agent responsible for phrasing missing-information questions."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def ask(self, trip_info: TripInfo, missing_field_key: str, conversation_text: str) -> str:
        field_spec = get_field_spec(missing_field_key)
        prompt = build_clarifying_question_prompt(trip_info, field_spec, conversation_text)
        question = await self.provider.generate_text(prompt=prompt, system_instruction=CLARIFIER_SYSTEM_PROMPT)
        return question.strip()
