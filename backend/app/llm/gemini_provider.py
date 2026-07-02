"""Google Gemini provider implementation using the public `google-genai` SDK."""

import json

from google import genai
from google.genai import types
from pydantic import ValidationError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.logging_config import get_logger
from app.llm.base import LLMProvider, LLMProviderError, SchemaT
from app.llm.retry_utils import is_retryable_gemini_error

logger = get_logger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise LLMProviderError(
                "GEMINI_API_KEY is not set. Get a free key at https://aistudio.google.com/apikey "
                "and set it in backend/.env"
            )
        self.client = genai.Client(api_key=api_key)
        self.model = model

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable_gemini_error),
    )
    async def generate_structured(
        self,
        prompt: str,
        schema: type[SchemaT],
        system_instruction: str | None = None,
    ) -> SchemaT:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            system_instruction=system_instruction,
            temperature=0.4,
        )
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini structured generation failed: %s", exc)
            raise LLMProviderError(f"Gemini API error: {exc}") from exc

        if not response.text:
            raise LLMProviderError("Gemini returned an empty structured response")

        try:
            data = json.loads(response.text)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.error("Gemini structured output failed validation: %s", exc)
            raise LLMProviderError(f"Gemini returned invalid structured output: {exc}") from exc

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception(is_retryable_gemini_error),
    )
    async def generate_text(self, prompt: str, system_instruction: str | None = None) -> str:
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini text generation failed: %s", exc)
            raise LLMProviderError(f"Gemini API error: {exc}") from exc

        return (response.text or "").strip()
