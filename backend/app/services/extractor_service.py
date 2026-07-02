"""Extractor agent: turns natural language + conversation history into structured TripInfo."""

from app.core.logging_config import get_logger
from app.llm.base import LLMProvider
from app.prompts.extraction_prompts import EXTRACTION_SYSTEM_PROMPT, build_extraction_prompt
from app.schemas.chat import TripInfo

logger = get_logger(__name__)


class ExtractorService:
    """Collaborating agent responsible for natural-language-to-structured extraction."""

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def extract(self, current_trip_info: TripInfo, conversation_text: str, latest_message: str) -> TripInfo:
        prompt = build_extraction_prompt(current_trip_info, conversation_text, latest_message)
        extracted = await self.provider.generate_structured(
            prompt=prompt, schema=TripInfo, system_instruction=EXTRACTION_SYSTEM_PROMPT
        )
        merged = self._merge(current_trip_info, extracted)
        logger.info("Extractor updated trip_info for fields present: %s", list(merged.model_dump(exclude_none=True)))
        return merged

    @staticmethod
    def _merge(old: TripInfo, new: TripInfo) -> TripInfo:
        """Defensive merge: a field only regresses to null if it truly was null in both;
        the LLM is instructed to preserve known fields, but we double-guard here so a
        single ambiguous turn never erases previously confirmed information."""
        merged_data = old.model_dump()
        new_data = new.model_dump()
        for key, new_value in new_data.items():
            if new_value is not None:
                merged_data[key] = new_value
        return TripInfo.model_validate(merged_data)
